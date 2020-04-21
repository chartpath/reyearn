import warnings
from datetime import timedelta
from prefect import task, Flow, Parameter
from prefect.engine.executors import DaskExecutor

# the connection pool used for the API is not serializable
# use synchronous client for distributed transactions
from prefect.tasks.postgres import PostgresFetch, PostgresExecute

# todo: use real schmas when improving prefect db client
# from db.schemas import observations, annotations

# keeping it "manual" for now
# from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from joblib import dump

pg_fetch = PostgresFetch("reyearn_dev", user=None, password=None, host="localhost",)
pg_ex = PostgresExecute("reyearn_dev", user=None, password=None, host="localhost",)

fetch_query_partial = f"""
--sql
select annos.class_label, obs.text, annos.observation_hash, obs.id obs_id
    from reyearn.annotations annos
        inner join reyearn_tenant_0.observations obs
        on annos.observation_hash = obs.hash
        where annos.class_label = %s
--end-sql
"""


@task
def get_classes_and_labels(max_retries=3):
    classes = list(
        pg_fetch.run(fetch="all", query="select type, label from reyearn.classes;")
    )
    labels = [label[1] for label in classes]
    return [classes, labels]


# fetch unique subset of total annotated observations for training
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_training_reference_data(label_limit, class_type, classes_and_labels):
    labels = classes_and_labels[1]
    training_reference_data = []
    training_reference_target = []
    for label in labels:
        labelled_ref_data = list(
            pg_fetch.run(
                fetch="all",
                # order opposite test data to keep subsets apart (head/tail)
                query=f"""
                    --sql
                    {fetch_query_partial}
                    order by obs.id asc limit %s;
                """,
                data=(label, label_limit,),
            )
        )
        training_reference_data.append(labelled_ref_data)
        training_reference_target.extend([labels.index(label)] * len(labelled_ref_data))
    return [training_reference_data, training_reference_target]


# fetch separate unique subset of total annotated observations for testing
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_training_test_data(label_limit, class_type, classes_and_labels):
    labels = classes_and_labels[1]
    training_test_data = []
    training_test_target = []
    for label in labels:
        labelled_test_data = list(
            pg_fetch.run(
                fetch="all",
                # order opposite reference data to keep subsets apart (head/tail)
                query=f"""
                    --sql
                    {fetch_query_partial}
                    order by obs.id desc limit %s;
                """,
                data=(label, label_limit,),
            )
        )
        training_test_data.append(labelled_test_data)
        training_test_target.extend([labels.index(label)] * len(labelled_test_data))
    return [training_test_data, training_test_target]


@task
def get_word_embeddings(training_reference):
    ref_data_corpus = []
    for label_subset in training_reference[0]:
        docs = [docs[1] for docs in label_subset]
        for doc in docs:
            ref_data_corpus.append(doc)

    # todo: test count vector with stop_words='english', parameterize if useful
    count_vectorizer = CountVectorizer()
    tfidf_transformer = TfidfTransformer()
    word_count_vector = count_vectorizer.fit_transform(ref_data_corpus)
    word_embeddings_tfidf = tfidf_transformer.fit_transform(word_count_vector)
    return {
        "count_vectorizer": count_vectorizer,
        "tfidf_transformer": tfidf_transformer,
        "word_count_vector": word_count_vector,
        "word_embeddings_tfidf": word_embeddings_tfidf,
    }


@task
def train_model(training_reference, word_embeddings, classes_and_labels):
    labels = classes_and_labels[1]
    model = MultinomialNB().fit(
        word_embeddings["word_embeddings_tfidf"], training_reference[1],
    )
    return model


@task
def test_model(
    model, training_test, training_reference_data, word_embeddings, classes_and_labels
):
    test_data_corpus = []
    for label_subset in training_test[0]:
        docs = [docs[1] for docs in label_subset]
        for doc in docs:
            test_data_corpus.append(doc)

    test_word_count_vector = word_embeddings["count_vectorizer"].transform(
        test_data_corpus
    )

    test_word_embeddings_tfidf = word_embeddings["tfidf_transformer"].transform(
        test_word_count_vector
    )
    predictions = model.predict(test_word_embeddings_tfidf)
    model_report = metrics.classification_report(
        training_test[1],
        predictions,
        target_names=classes_and_labels[1],
        output_dict=True,
    )
    return model_report


@task
def deploy_model(model, model_report):
    print("deploying model...")
    try:
        # todo: extend for multi-model
        model_info = pg_fetch.run(
            fetch="one",
            query="""
                --sql
                select version, accuracy::text from reyearn.models where version = 'latest';
            """,
        )
        # is it better?
        if model_info is None or model_report["accuracy"] > float(model_info[1]):
            dumped = dump(model, "./models/latest.joblib")
            if len(dumped) == 1:
                pg_ex.run(
                    query="""
                        --sql
                        insert into reyearn.models (version, accuracy, precision, recall, f1)
                            values ('latest', %s, %s, %s, %s)
                            on conflict (version) do update
                                set accuracy = excluded.accuracy,
                                    precision = excluded.precision,
                                    recall = excluded.recall,
                                    f1 = excluded.f1;
                    """,
                    data=(
                        model_report["accuracy"],
                        model_report["weighted avg"]["precision"],
                        model_report["weighted avg"]["recall"],
                        model_report["weighted avg"]["f1-score"],
                    ),
                )
            else:
                warnings.warn(
                    f"Problem deploying model: {model_report}, {dumped}", Warning
                )
        else:
            warnings.warn(f"Model not improved, not deploying: {model_report}", Warning)
        return True
    except Exception as e:
        raise e


def main(params={"label_limit": 500, "class_type": "email"}):

    with Flow("trainer", schedule=None) as flow:

        # rand = Parameter("rand", default=params["rand"])
        label_limit = Parameter("label_limit", default=params["label_limit"])
        class_type = Parameter("class_type", default=params["class_type"])

        # tasks
        classes_and_labels = get_classes_and_labels()
        training_reference = fetch_training_reference_data(
            label_limit, class_type, classes_and_labels
        )
        training_test = fetch_training_test_data(
            label_limit, class_type, classes_and_labels
        )
        word_embeddings = get_word_embeddings(training_reference)
        model = train_model(training_reference, word_embeddings, classes_and_labels)
        model_report = test_model(
            model,
            training_test,
            training_reference,
            word_embeddings,
            classes_and_labels,
        )
        deployed_model = deploy_model(model, model_report)

        # register with dashboard
        try:
            flow.register(project_name="Reyearn")
        except:
            pass

        # agent can be run externally with `prefect agent start`
        # flow.run_agent(show_flow_logs=True)

        flow_state = flow.run(executor=DaskExecutor(), parameters=params)

        # uncomment to output pdf visualization of this flow
        # flow.visualize(flow_state=flow_state, filename="dags/trainer_latest")


if __name__ == "__main__":
    main()

from datetime import timedelta
from prefect import task, Flow, Parameter
from prefect.engine.executors import DaskExecutor

# the connection pool used for the API is not serializable
# use synchronous client for distributed transactions
from prefect.tasks.postgres import PostgresExecute
from db.schemas import observations, annotations

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from sklearn import metrics

# fetch unique subset of total annotated observations for training
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_training_reference_data(rand, limit, class_type):
    labels = ["alt.atheism", "soc.religion.christian", "comp.graphics", "sci.med"]
    training_reference_data = fetch_20newsgroups(
        subset="train", categories=labels, shuffle=True, random_state=42
    )
    print(
        "fetching training data for labels", training_reference_data.target_names,
    )
    return training_reference_data


# fetch separate unique subset of total annotated observations for testing
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_training_test_data(rand, limit, class_type):
    training_test_data = ["God is love", "OpenGL on the GPU is fast"]
    print("fetching test data", training_test_data)
    return training_test_data


@task
def get_word_embeddings(training_reference_data):
    # todo: test count vector with stop_words='english', parameterize if useful
    count_vectorizer = CountVectorizer()
    tfidf_transformer = TfidfTransformer()
    word_count_vector = count_vectorizer.fit_transform(training_reference_data.data)
    word_embeddings_tfidf = tfidf_transformer.fit_transform(word_count_vector)
    return {
        "count_vectorizer": count_vectorizer,
        "tfidf_transformer": tfidf_transformer,
        "word_count_vector": word_count_vector,
        "word_embeddings_tfidf": word_embeddings_tfidf,
    }


@task
def train_model(training_reference_data, word_embeddings):
    model = MultinomialNB().fit(
        word_embeddings["word_embeddings_tfidf"], training_reference_data.target
    )
    return model


@task
def test_model(model, training_test_data, training_reference_data, word_embeddings):
    test_word_count_vector = word_embeddings["count_vectorizer"].transform(
        training_test_data
    )
    test_word_embeddings_tfidf = word_embeddings["tfidf_transformer"].transform(
        test_word_count_vector
    )
    predictions = model.predict(test_word_embeddings_tfidf)
    for observation, label in zip(training_test_data, predictions):
        print("%r => %s" % (observation, training_reference_data.target_names[label]))


def main(params={"rand": True, "limit": 1000, "class_type": "email"}):

    with Flow("trainer", schedule=None) as flow:

        rand = Parameter("rand", default=params["rand"])
        limit = Parameter("limit", default=params["limit"])
        class_type = Parameter("class_type", default=params["class_type"])

        # tasks
        training_reference_data = fetch_training_reference_data(rand, limit, class_type)
        training_test_data = fetch_training_test_data(rand, limit, class_type)
        word_embeddings = get_word_embeddings(training_reference_data)
        model = train_model(training_reference_data, word_embeddings)
        test_model(model, training_test_data, training_reference_data, word_embeddings)

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

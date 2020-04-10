from datetime import timedelta
from prefect import task, Flow, unmapped
from prefect.engine.executors import DaskExecutor
import os

# the async db client pool used for the API is not serializable
from prefect.tasks.postgres import PostgresExecute, PostgresFetch
from db.schemas import observations, annotations
from psycopg2.errors import UniqueViolation

# todo: these prefect core tasks should be extended to support connection.executemany()
# to run whole chunks in a single transaction
pg_ex = PostgresExecute("reyearn_dev", user=None, password=None, host="localhost",)
pg_fetch = PostgresFetch("reyearn_dev", user=None, password=None, host="localhost",)


@task
def get_existing_classes():
    existing_classes = list(
        # returns 2d tuples
        pg_fetch.run(
            fetch="all",
            query="""
            --sql
            select type, label from reyearn.classes;
        """,
        )
    )
    existing_labels = [label[1] for label in existing_classes]
    return [existing_classes, existing_labels]


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def build_file_lists():
    chunk_size = 100
    labelled_file_list = []
    unlabelled_file_list = []
    for dirpath, dirs, files in os.walk("./data/import", followlinks=True):
        for f in files:
            if "README.md" not in f and "." not in f[0]:
                label = dirpath.split("/")[-1]
                # labelled data has a label path with len > 1 level
                # label roots are identical to the class type
                if "." in label:
                    labelled_file_list.append(f"{dirpath}/{f}")
                else:
                    unlabelled_file_list.append(f"{dirpath}/{f}")
    chunked_labelled_files = [
        labelled_file_list[i * chunk_size : (i + 1) * chunk_size]
        for i in range((len(labelled_file_list) + chunk_size - 1) // chunk_size)
    ]
    chunked_unlabelled_files = [
        unlabelled_file_list[i * chunk_size : (i + 1) * chunk_size]
        for i in range((len(unlabelled_file_list) + chunk_size - 1) // chunk_size)
    ]
    return [chunked_labelled_files, chunked_unlabelled_files]


@task
def load_chunked_files(chunked_files, existing_labels):
    annotations = []
    for file in chunked_files:
        # toss weird characters, they won't make it past the tokenizer anyway
        # full content type parsing is of course the holy grail
        with open(file, "r", encoding="latin-1", errors="ignore") as filehandle:
            filecontent = filehandle.read()
            file_label = file.split("/")[-2]
            if file_label not in existing_labels:
                label_root = file_label.split(".")[0]
                # todo: fix minor seq inflation with extra select
                # when migrating to chunk-level transactions
                pg_ex.run(
                    query="""
                        --sql
                        insert into reyearn.classes (type, label) values (%s, %s)
                            on conflict do nothing;
                    """,
                    data=(label_root, file_label),
                )
            try:
                pg_ex.run(
                    query=f"""
                        --sql
                        insert into reyearn_tenant_0.observations (text, hash)
                            values (%s, MD5(%s)) on conflict do nothing;
                    """,
                    data=(filecontent, filecontent),
                )
            except UniqueViolation as error:
                pass
            # todo: remove once client supports inserts with returning,
            # for chunk-level transactions, and revisit other hash functions
            file_hash = pg_fetch.run(
                fetch="one", query="select md5(%s);", data=(filecontent,)
            )
            annotations.append((file_label, file_hash[0]))
    return annotations


@task
def load_annotations(annotations):
    for anno in annotations:
        pg_ex.run(
            query="""
            --sql
            insert into reyearn.annotations (class_label, observation_hash, status)
                values (%s, %s, %s) on conflict do nothing;
            """,
            data=(anno[0], anno[1], "confirmed"),
        )


def main():

    with Flow("importer", schedule=None) as flow:
        # tasks
        existing_classes = get_existing_classes()
        chunked_files = build_file_lists()

        # partition and map over to flatten load curve
        # labelled data
        annotations = load_chunked_files.map(
            chunked_files[0], unmapped(existing_classes[1]),
        )
        # unlabelled data
        load_chunked_files.map(
            chunked_files[1], unmapped(existing_classes[1]),
        )

        load_annotations.map(annotations)

        # register with dashboard
        try:
            flow.register(project_name="Reyearn")
        except:
            pass

        # agent can be run externally with `prefect agent start`
        # flow.run_agent(show_flow_logs=True)

        flow_state = flow.run(executor=DaskExecutor())

        # uncomment to output pdf visualization of this flow
        flow.visualize(flow_state=flow_state, filename="dags/importer_latest")


if __name__ == "__main__":
    main()

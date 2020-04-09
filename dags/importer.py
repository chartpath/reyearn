from datetime import timedelta
from prefect import task, Flow
from prefect.engine.executors import DaskExecutor
import os

# the async db client pool used for the API is not serializable
from prefect.tasks.postgres import PostgresExecute
from db.schemas import observations, annotations
from psycopg2.errors import UniqueViolation

pg_task = PostgresExecute("reyearn_dev", user=None, password=None, host="localhost",)


def load_chunked_files(chunked_files):
    for file in chunked_files:
        # toss weird characters, they would be thrown out by the tokenizer anyway
        # full content type parsing is of course the holy grail
        with open(file, "r", encoding="latin-1", errors="ignore") as filehandle:
            filecontent = filehandle.read()
            # this performs fine for now, but if optimization is needed
            # PostgresExecute can be extended to support connection.executemany()
            # to run the whole chunk in a single transaction, or use driver directly
            try:
                pg_task.run(
                    query=f"""
                        --sql
                        insert into reyearn_tenant_0.observations (text, md5)
                            values (%s, MD5(%s));
                    """,
                    data=(filecontent, filecontent),
                )
            except UniqueViolation as error:
                print(error)
                pass


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def build_file_lists():
    chunk_size = 100
    # labelled_files = {}
    labelled_file_list = []
    unlabelled_file_list = []
    for dirpath, dirs, files in os.walk("./data/import",):
        for f in files:
            if "README.md" not in f and "." not in f[0]:
                # labelled data has a label path with > 1 (root) level
                if "." in dirpath.split("/")[-1]:
                    # labelled_files[label].append(f"{dirpath}/{f}")
                    labelled_file_list.append(f"{dirpath}/{f}")
                else:
                    # unlabelled_files[type].append(f"{dirpath}/{f}")
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


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def load_labelled_data(chunked_labelled_files):
    load_chunked_files(chunked_labelled_files)
    return True


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def load_unlabelled_data(chunked_unlabelled_files):
    load_chunked_files(chunked_unlabelled_files)
    return True


def main():

    with Flow("importer", schedule=None) as flow:
        # tasks
        chunked_files = build_file_lists()
        # map to flatten load curve
        labelled_data_loaded = load_labelled_data.map(chunked_files[0])
        unlabelled_data_loaded = load_unlabelled_data.map(chunked_files[1])

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

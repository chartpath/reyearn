from datetime import timedelta
from prefect import task, Flow
from prefect.engine.executors import DaskExecutor
import os
from prefect.tasks.postgres import PostgresExecute, PostgresFetch

# uses a separate pool from the server app
from db.schemas import observations, annotations

pg_task = PostgresExecute("reyearn_dev", user=None, password=None, host="localhost",)


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def build_file_lists():
    chunk_size = 100
    labelled_file_list = []
    unlabelled_file_list = []
    for dirpath, dirs, files in os.walk("./data/import",):
        for f in files:
            if "README.md" not in f and "." not in f[0]:
                # labelled data has a label path with > 1 (root) level
                if "." in dirpath.split("/")[-1]:
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


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def load_labelled_data(chunked_labelled_files):
    for file in chunked_labelled_files:
        with open(file, "r") as filehandle:
            filecontent = filehandle.read()
            pg_task.run(
                query=f"""
                    --sql
                    insert into reyearn_tenant_0.observations (text, md5)
                        values (%s, MD5(%s));
                """,
                data=(filecontent, filecontent),
            )
    return True


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def load_unlabelled_data(chunked_unlabelled_files):
    for file in chunked_unlabelled_files:
        with open(file, "r") as filehandle:
            filecontent = filehandle.read()
            pg_task.run(
                query=f"""
                    --sql
                    insert into reyearn_tenant_0.observations (text, md5)
                        values (%s, MD5(%s));
                """,
                data=(filecontent, filecontent),
            )
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

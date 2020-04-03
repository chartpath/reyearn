from datetime import timedelta
from prefect import task, Flow
from prefect.engine.executors import DaskExecutor
import os

# uses a separate pool from the server app
from db.client import db as db_client


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
def extract_labelled_data(chunked_labelled_files):
    labelled_data = [
        {"label": "email.business", "text": "This is a business email."},
        {"label": "email.personal", "text": "This is a personal email."},
    ]
    print("fetching labelled data...", labelled_data)
    return labelled_data


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def extract_unlabelled_data(chunked_unlabelled_files):
    unlabelled_data = [
        "This is a very new business email observation.",
        "This is a super new personal email observation.",
    ]
    print("fetching unlabelled data...", unlabelled_data)
    return unlabelled_data


@task
def transform(labelled_data, unlabelled_data):
    transformed_unlabelled_data = []
    for observation in unlabelled_data:
        transformed_unlabelled_data.append({"label": "email", "text": observation})
    print("cleaning and transforming data...", transformed_unlabelled_data)
    return transformed_unlabelled_data


@task
def load_labelled_data(labelled_data):
    print("saving labelled data...")


@task
def load_transformed_unlabelled_data(unlabelled_data):
    print("saving lunabelled data...")


def main():

    with Flow("importer", schedule=None) as flow:

        # tasks
        chunked_files = build_file_lists()
        # map to flatten load curve
        labelled_data = extract_labelled_data.map(chunked_files[0])
        unlabelled_data = extract_unlabelled_data.map(chunked_files[1])
        transformed_unlabelled_data = transform(labelled_data, unlabelled_data)
        load_labelled_data(labelled_data)
        load_transformed_unlabelled_data(transformed_unlabelled_data)

        # register with dashboard
        try:
            flow.register(project_name="Reyearn")
        except:
            pass

        # agent can be run externally with `prefect agent start`
        # flow.run_agent(show_flow_logs=True)

        flow_state = flow.run(executor=DaskExecutor())

        # uncomment to output pdf visualization of this flow
        # flow.visualize(flow_state=flow_state, filename="dags/importer_latest")


if __name__ == "__main__":
    main()

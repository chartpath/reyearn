from datetime import timedelta
from prefect import task, Flow, Parameter
from prefect.engine.executors import DaskExecutor

# uses a separate pool from the server app
from db.client import db as db_client

# Fetch a unique subset of total annotated observations for training
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_training_data(rand, limit, class_type):
    training_data = [
        {"label": "email.business", "text": "This is a business email."},
        {"label": "email.personal", "text": "This is a personal email."},
    ]
    print("fetching training data...", training_data)
    return training_data


# Fetch a separate unique subset of total annotated observations for testing
@task(max_retries=3, retry_delay=timedelta(seconds=1))
def fetch_test_data(rand, limit, class_type):
    test_data = [
        {
            "label": "email.business",
            "text": "This is a very new business email observation.",
        },
        {
            "label": "email.personal",
            "text": "This is a super new personal email observation.",
        },
    ]
    print("fetching test data...", test_data)
    return test_data


@task
def train_model(training_data):
    print("training model...")


@task
def test_model(trained_model, test_data):
    print("training model...")


def main(params={"rand": True, "limit": 1000, "class_type": "email"}):

    with Flow("trainer", schedule=None) as flow:

        rand = Parameter("rand", default=params["rand"])
        limit = Parameter("limit", default=params["limit"])
        class_type = Parameter("class_type", default=params["class_type"])

        # tasks
        training_data = fetch_training_data(rand, limit, class_type)
        test_data = fetch_test_data(rand, limit, class_type)
        trained_model = train_model(training_data)
        test_model(trained_model, test_data)

    flow_state = flow.run(executor=DaskExecutor(), parameters=params)

    # uncomment to output pdf visualization of this flow
    flow.visualize(flow_state=flow_state, filename="dags/trainer_latest")


if __name__ == "__main__":
    main()

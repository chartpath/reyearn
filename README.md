# Reyearn (WIP)

![](https://media.giphy.com/media/3orif368drh8LRG7WU/giphy.gif)

A data experimentation and model training framework. Reyearn aims to help people evolve machine learning models and inference engines in production by tightly looping the development lifecycle as a dynamic pipeline: ETL -> annotation -> training or tuning -> testing -> deploying. It is designed to be used with existing applications, being installed into the same database. It takes an ensemble-of-models approach.

## TODO

- [x] DB for classes, annotations, observations, experiments
- [x] split schemas for multi-tenant support
- [x] data ingestion ETL pipeline
- [x] DB for experiments and models
- [x] model training pipeline (implementation stubbed)
- [x] API endpoints for annotations, predictions and observations
- [x] default text classifier with dask-ml TD-IDF/naive bayes
- [x] initial cascade rules
- [ ] hot reload models
- [ ] add model versions to prediction endpoint
- [ ] annotation type column for features
- [ ] annotation range column for NER and POS tags
- [ ] convert to Hashing Vectorizer
- [ ] swap out joblib backend for dask-ml
- [ ] UUIDs for external access
- [ ] symlinks for multi-label import
- [ ] gzip file upload observations
- [ ] integration tests
- [ ] CLI to wrap DAGs and API
- [ ] tutorial in docs
- [ ] proper config management
- [ ] basic JWT
- [ ] custom result handlers in DAGs for failure triage
- [ ] default topic modelling/clustering support
- [ ] prodigy annotation UI integration
- [ ] experiment tracking

## Usage

Assuming PostgresSQL is installed and running on the default port with no username or password (the default on Mac for homebrew builds), this sequence of commands should get you going.

```shell
$ pip install poetry
$ poetry install
...
$ poetry shell
(reyearn-venv)$ createdb reyearn_dev
(reyearn-venv)$ alembic upgrade head
(reyearn-venv)$ python -m server
```

To set up a data import see the [data import readme](./data/import/email/README.md). Then to manually run the importer pipeline to ingest the email data, run `python -m dags.importer`. The server and the importer and trainer DAGs have debug configs for VS code.

To test the API, once the server is running, go to http://127.0.0.1:8000/docs in your browser and call the endpoints. Follow the schema info provided to know what to include in request bodies. Creating annotations will trigger the model training pipeline to run, but right now it is just a stub without a real model behind it (coming soon).

## Implementation Details

### Data Workflows

Reyearn uses [Prefect](https://docs.prefect.io/core/getting_started/why-prefect.html) for parallel and distributed execution of workflows (DAGs). It uses [Dask](https://docs.dask.org/en/latest/why.html) for running serialized distributed tasks that integrate well with the Python data science ecosystem.

### API tooling

[FastAPI](https://fastapi.tiangolo.com/history-design-future/) is the web glue library of choice because it's async (thanks to [Starlette](https://www.starlette.io/)) and provides a lot of type safety and validation out of the box.

### PostgreSQL Database

Reyearn integrates as tightly as possible with PostgreSQL with a thin layer of SQLAlchemy Core on top for query composition and metadata reflection. Class label hierarchies are implemented using the [LTREE](https://www.postgresql.org/docs/9.1/ltree.html) data type. Alembic is used for migrations.
# Reyearn

A server that aims to help people evolve NLP models in production by tightly looping the development pipeline: ingestion -> annotation -> training -> testing -> deploying. It takes an ensemble-of-models approach. For more on the philosophy, read the [vision doc](docs/vision.md).

Made by and for generalists who need a scalable and production-ready NLP solution out of the box, with a friendly pathway towards understanding the underlying concepts. It won't be all things data engineering or all things ML, but should have sane default solutions to common needs and a way to extend the functionality. See the [roadmap](#roadmap/wishlist) and open some issues!

## Features

- Can be installed into an existing application's PostgreSQL database
- Built with multi-tenancy in mind so observations can be siloed by organization
- Everything is async and distributed
- Runtime DAG-based ingestion pipeline to load training data into the database
- Observations and annotations can be added directly through the API
- New predictions optionally persisted as annotations and observations for future processing
- Annotations optionally trigger the model training pipeline to run without blocking
- Previously predicted annotations can be confirmed or rejected to determine if they will get picked up in the next training run
- If the newly trained model is more accurate than the previous one, it will be injected as the new live model via hot-reloading
- Many different models can be used in parallel
- Models can be trained on multiple labels
- Naive bayes with TF-IDF vectors is the firs supported ML algorithm

## Usage

Assuming PostgresSQL is installed and running on the default port with no username or password (the default on Mac for homebrew builds), this sequence of commands should get you going.

```shell
$ pip install poetry
$ poetry install
...
$ poetry shell
(reyearn-venv)$ createdb reyearn_dev
(reyearn-venv)$ cd db && alembic upgrade head
...
(reyearn-venv)$ cd .. && python -m server
```

To set up a data import see the [data import readme](./data/import/email/README.md). Then to manually run the importer pipeline to ingest the data, run `python -m dags.importer`. The server and the importer and trainer DAGs have debug configs for VS code.

The model trainer can be run standalone with `python -m dags.trainer`.

To explore the API, once the server is running, go to http://127.0.0.1:8000/docs in your browser and call the endpoints.

## Implementation Details

### Data Workflows

Reyearn uses [Prefect](https://docs.prefect.io/core/getting_started/why-prefect.html) for parallel and distributed execution of workflows (DAGs). It uses [Dask](https://docs.dask.org/en/latest/why.html) for running serialized distributed tasks that integrate well with the Python data science ecosystem.

### API Tooling

[FastAPI](https://fastapi.tiangolo.com/history-design-future/) is the web glue library of choice because it's async (thanks to [Starlette](https://www.starlette.io/)) and provides a lot of type safety and validation out of the box.

### PostgreSQL Database

Reyearn integrates as tightly as possible with PostgreSQL with a thin layer of SQLAlchemy Core on top for query composition and metadata reflection. Class label hierarchies are implemented using the [LTREE](https://www.postgresql.org/docs/9.1/ltree.html) data type. Alembic is used for migrations.

## Roadmap/wishlist

This will probably be moved to an issue tracker. The list keeps expanding from todos and nice-to-haves observed during development. In no particular order:

- [ ] model metadata and training endpoints
- [ ] class label endpoints
- [ ] plugin system with base classes
- [ ] POS tagging endpoint
- [ ] fine-tune default classifier with better sample control
- [ ] annotation type and range columns to support NER
- [ ] NER endpoint
- [ ] convert naive bayes to use Hashing Vectorizer
- [ ] swap out joblib backend for dask-ml
- [ ] gzip file upload observations
- [ ] integration tests
- [ ] CLI to wrap DAGs and API
- [ ] python and node client libraries
- [ ] proper tutorial in docs
- [ ] proper config management
- [ ] basic JWT/security
- [ ] custom result handlers in DAGs for failure triage
- [ ] prodigy or equivalent annotation UI integration
- [ ] experiment tracking/reporting
- [ ] additional data ingestion sources (e.g. data lakes, distributed file systems)
- [ ] additional ML algorithms (nearest neighbours clustering, topic modelling)
# Reyearn

![](https://media.giphy.com/media/3orif368drh8LRG7WU/giphy.gif)

A data experimentation and model training framework. Reyearn aims to help people evolve machine learning models and inference engines in production by tightly looping the development lifecycle as a dynamic pipeline: ETL -> annotation -> training or tuning -> testing -> deploying. It is designed to be used with existing applications, being installed into the same database. It takes an ensemble-of-models approach.

## TODO

- [x] DB for classes, annotations, observations
- [x] split schemas for multi-tenant support
- [x] data ingestion ETL pipeline
- [x] DB for experiments and models
- [x] model training pipeline (implementation stubbed)
- [x] API endpoints for annotations, predictions and observations
- [ ] default text classifier with gensim
- [ ] UUIDs for external access
- [ ] symlinks for multi-label import
- [ ] gzip file upload observations
- [ ] integration tests
- [ ] CLI to wrap DAGs and API
- [ ] tutorial in docs
- [ ] proper config management
- [ ] basic JWT

## Implementation Details

### Data Workflows

Reyearn uses [Prefect](https://docs.prefect.io/core/getting_started/why-prefect.html) for parallel and distributed execution of workflows (DAGs). It uses [Dask](https://docs.dask.org/en/latest/why.html) for running serialized distributed tasks that integrate well with the Python data science ecosystem.

### API tooling

[FastAPI](https://fastapi.tiangolo.com/history-design-future/) is the web glue library of choice because it's async (thanks to [Starlette](https://www.starlette.io/)) and provides a lot of type safety and validation out of the box.

### PostgreSQL Database

Reyearn integrates as tightly as possible with PostgreSQL with a thin layer of SQLAlchemy Core on top for query composition and metadata reflection. Class label hierarchies are implemented using the [LTREE](https://www.postgresql.org/docs/9.1/ltree.html) data type. Alembic is used for migrations.
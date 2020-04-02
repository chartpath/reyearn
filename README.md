# Reyearn

![](https://media.giphy.com/media/3orif368drh8LRG7WU/giphy.gif)

A data experimentation and model training framework. Reyearn aims to help people evolve machine learning models and inference engines in production by tightly looping the pipeline lifecycle: ETL -> annotation -> training or tuning -> testing -> deploying. It is designed to be used with applications that take an ensemble-of-models approach.

## TODO

- [ ] db for annotations, experiments, observations
- [x] split schemas for multi-tenant support
- [ ] data ingestion ETL pipeline
- [ ] model training pipeline (implementation stubbed)
- [ ] api endpoints for annotation and prediction
- [ ] default TF-IDF naive bayes classifier
- [ ] integration tests
- [ ] quickstart docs
- [ ] proper config management
- [ ] basic JWT
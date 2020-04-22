import warnings
from typing import List
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from pydantic import BaseModel
from db import schemas
from sqlalchemy_utils import Ltree
from asyncpg.exceptions import UniqueViolationError
from dags import trainer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer


router = APIRouter()


@router.get("/")
async def root():
    return {"ack": "ok"}


class AnnotationCreate(BaseModel):
    class_label: str
    observation_hash: str
    status: str = "confirmed"


class AnnotationRead(BaseModel):
    id: int
    class_label: str
    observation_hash: str


@router.get("/annotations", response_model=List[AnnotationRead])
async def read_annotations(req: Request):
    db = req.app.state.db_client
    annotations = await db.fetch_all(schemas.annotations.select())
    return annotations


@router.post("/annotations", response_model=AnnotationRead, status_code=201)
async def create_annotation(
    anno: AnnotationCreate, req: Request, background_tasks: BackgroundTasks
):
    db = req.app.state.db_client

    try:
        query = schemas.annotations.insert().values(
            class_label=Ltree(anno.class_label),
            observation_hash=anno.observation_hash,
            status=anno.status,
        )
        last_record_id = await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="Annotation already exists.")

    # retrain the model
    background_tasks.add_task(trainer.main)
    return {**anno.dict(), "id": last_record_id}


class ObservationCreate(BaseModel):
    text: str


class ObservationRead(BaseModel):
    id: int
    text: str
    hash: str


@router.get("/observations", response_model=List[ObservationRead])
async def read_observations(req: Request):
    db = req.app.state.db_client
    # todo: paginate
    observations = await db.fetch_all(schemas.observations.select(limit=100))
    return observations


@router.post("/observations", response_model=ObservationRead, status_code=201)
async def create_observation(obs: ObservationCreate, req: Request):
    db = req.app.state.db_client
    obs_hash = await db.execute(f"select md5('{obs.text}')")

    try:
        query = schemas.observations.insert().values(text=obs.text, hash=obs_hash)
        last_record_id = await db.execute(query)
        return {**obs.dict(), "id": last_record_id, "hash": obs_hash}
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="Observation already exists.")


class PredictionCreate(BaseModel):
    text: str = None
    # new predictions will automatically be observed and annotated
    # as "predicted" if not disabled in the request
    disable_persist: bool = False


class PredictionRead(BaseModel):
    predictions: List[str]
    observation_hash: str = None


@router.post("/predictions/{class_type}", response_model=PredictionRead)
async def read_prediction(class_type: str, predict: PredictionCreate, req: Request):
    db = req.app.state.db_client
    model = req.app.state.model_latest
    count_vectorizer = model["count_vectorizer"]
    tfidf_transformer = model["tfidf_transformer"]
    word_count_vector = count_vectorizer.transform([predict.text])
    word_embeddings_tfidf = tfidf_transformer.transform(word_count_vector)
    predictions = model["model"].predict(word_embeddings_tfidf)
    response_predictions = []
    for doc, label in zip([predict.text], predictions):
        predicted_label = model["target_labels"][label]
        response_predictions.append(predicted_label)
        print("%r => %s" % (doc, predicted_label))

    if not predict.disable_persist:
        try:
            obs_create = ObservationCreate(text=predict.text)
            obs_hash = await db.execute(f"select md5('{obs_create.text}')")
            obs_query = schemas.observations.insert().values(
                text=obs_create.text, hash=obs_hash
            )
            obs_last_record_id = await db.execute(obs_query)
        except UniqueViolationError as exception:
            warnings.warn(f"Observation exists: {exception}", Warning)
        try:
            anno_create = AnnotationCreate(
                class_label=response_predictions[0],
                observation_hash=obs_hash,
                status="predicted",
            )
            anno_query = schemas.annotations.insert().values(
                class_label=Ltree(anno_create.class_label),
                observation_hash=anno_create.observation_hash,
                status=anno_create.status,
            )
            anno_last_record_id = await db.execute(anno_query)
        except UniqueViolationError as exception:
            warnings.warn(f"Persisting new annotation failed: {exception}", Warning)
    return {
        "predictions": response_predictions,
        "observation_hash": obs_hash,
    }

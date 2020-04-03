from typing import List
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from db import schemas
from dags import trainer

router = APIRouter()


@router.get("/")
async def root():
    return {"ack": "ok"}


class AnnotationCreate(BaseModel):
    class_id: int
    observation_id: int
    status: str = None


class AnnotationRead(BaseModel):
    id: int
    class_id: int
    observation_id: int


@router.get("/annotations", response_model=List[AnnotationRead])
async def read_annotations(req: Request):
    db = req.app.state.db_client
    annotations = await db.fetch_all(schemas.annotations.select())
    return annotations


@router.post("/annotations", response_model=AnnotationRead)
async def create_annotation(
    anno: AnnotationCreate, req: Request, background_tasks: BackgroundTasks
):
    db = req.app.state.db_client
    query = schemas.annotations.insert().values(
        class_id=anno.class_id, observation_id=anno.observation_id, status=anno.status
    )
    last_record_id = await db.execute(query)

    # retrain the model
    background_tasks.add_task(trainer.main)
    return {**anno.dict(), "id": last_record_id}


class ObservationCreate(BaseModel):
    text: str


class ObservationRead(BaseModel):
    id: int
    text: str


@router.get("/observations", response_model=List[ObservationRead])
async def read_observations(req: Request):
    db = req.app.state.db_client
    observations = await db.fetch_all(schemas.observations.select())
    return observations


@router.post("/observations", response_model=ObservationRead)
async def create_observations(obs: ObservationCreate, req: Request):
    db = req.app.state.db_client
    query = schemas.observations.insert().values(text=obs.text)
    last_record_id = await db.execute(query)
    return {**obs.dict(), "id": last_record_id}


class PredictionCreate(BaseModel):
    text: str = None
    observation_id: int = None


class PredictionRead(BaseModel):
    label: str
    annotation_id: int


@router.post("/predictions/{class_type}", response_model=PredictionRead)
async def read_prediction(class_type: str, predict: PredictionCreate, req: Request):
    db = req.app.state.db_client
    prediction = {"observation_id": 1}
    return prediction

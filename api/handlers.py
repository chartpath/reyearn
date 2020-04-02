from typing import List
from fastapi import APIRouter, Request
from pydantic import BaseModel
from db import schemas

router = APIRouter()


@router.get("/")
async def root():
    return {"ack": "ok"}


class AnnoIn(BaseModel):
    class_id: int
    observation_id: int


class Anno(BaseModel):
    id: int
    class_id: int
    observation_id: int


@router.get("/annotations", response_model=List[Anno])
async def read_annotations(req: Request):
    db = req.app.state.db_client
    annotations = await db.fetch_all(schemas.annotations.select())
    return annotations


@router.post("/annotations", response_model=Anno)
async def create_annotation(anno: AnnoIn, req: Request):
    db = req.app.state.db_client
    query = schemas.annotations.insert().values(
        class_id=anno.class_id, observation_id=anno.observation_id
    )
    last_record_id = await db.execute(query)
    return {**anno.dict(), "id": last_record_id}

from fastapi import APIRouter, Request
from db import schemas

router = APIRouter()


@router.get("/")
async def root():
    return {"ack": "ok"}


@router.get("/annotations")
async def read_annotations(req: Request):
    db = req.app.state.db_client
    annotations = await db.fetch_all(schemas.annotations.select())
    return annotations


@router.post("/annotations")
async def create_annotation(anno: dict, req: Request):
    db = req.app.state.db_client
    query = schemas.annotations.insert().values(
        class_id=anno["class_id"], observation_id=anno["observation_id"]
    )
    last_record_id = await db.execute(query)
    return {**anno, "id": last_record_id}

from starlette.responses import JSONResponse
from starlette.routing import Route
from db import repo


async def root(req):
    return JSONResponse({"ack": "ok"})


async def annotations(req):
    db = req.app.state.db_client
    if req.method == "POST":
        body = await request.json()
        if body.class_id and body.observation_id:
            new_annotation = await repo.create_annotations(db)
            print(new_annotation)
            return JSONResponse({"msg": "created"})
        else:
            return JSONResponse(
                {"msg": "class_id and observation_id required"}, status_code=400
            )
    elif req.method == "GET":
        annotations = await repo.fetch_annotations(db)
        print(annotations)
        return JSONResponse(annotations)


routes = [
    Route("/", root),
    Route("/annotations", annotations, methods=["GET", "POST"]),
]

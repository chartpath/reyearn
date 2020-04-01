from starlette.responses import JSONResponse
from starlette.routing import Route


async def root(req):
    print(req.app.state.db_schemas)
    return JSONResponse({"ack": "ok"})


routes = [
    Route("/", root),
]

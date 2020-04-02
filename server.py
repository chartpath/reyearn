from starlette.applications import Starlette
from fastapi import FastAPI
from api.handlers import routes
from db.client import db as db_client
import db.schemas as db_schemas
from dags import importer, trainer

DEBUG = True
# add importer.main, trainer.main to trigger dags on startup
# run them manually with `python -m dags.trainer` and `python -m dags.trainer`
debug_startup_events = [db_client.connect]

if DEBUG:
    app = FastAPI(
        debug=DEBUG,
        on_startup=debug_startup_events,
        on_shutdown=[db_client.disconnect],
        routes=routes,
    )
else:
    app = FastAPI(
        debug=DEBUG,
        on_startup=[db_client.connect],
        on_shutdown=[db_client.disconnect],
        routes=routes,
    )
app.state.db_client = db_client
app.state.db_schemas = db_schemas

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

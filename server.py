from fastapi import FastAPI, WebSocket
from api import handlers
import os, sys
from db.client import db as db_client
import db.schemas as db_schemas
from dags import importer, trainer
from joblib import load as joblib_load

DEBUG = os.getenv("DEBUG", False)
# add importer.main, trainer.main (or others) to trigger dags on startup
# run them manually with `python -m dags.trainer` and `python -m dags.trainer`
debug_startup_events = [db_client.connect]

if DEBUG:
    os.environ["PREFECT__LOGGING__LEVEL"] = "DEBUG"
    app = FastAPI(
        title="Reyearn API",
        debug=DEBUG,
        on_startup=debug_startup_events,
        on_shutdown=[db_client.disconnect],
    )
else:
    app = FastAPI(
        title="Reyearn API",
        debug=DEBUG,
        on_startup=[db_client.connect],
        on_shutdown=[db_client.disconnect],
    )
app.state.db_client = db_client
app.state.db_schemas = db_schemas

try:
    model_latest = joblib_load("./models/latest.joblib")
    app.state.model_latest = model_latest
except FileNotFoundError:
    print("No model trained yet, plase run this first: python -m dags.trainer")
    sys.exit(1)

app.include_router(handlers.router)

if __name__ == "__main__":
    import uvicorn

    if DEBUG:
        uvicorn.run(
            "server:app", host="0.0.0.0", port=8000, workers=1, reload=True,
        )
    else:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, workers=4)

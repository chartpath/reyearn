import logging
from fastapi import FastAPI, WebSocket
from api import handlers
import os, sys
from db.client import db as db_client
import db.schemas as db_schemas
from dags import importer, trainer
from joblib import load as joblib_load
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

DEBUG = os.getenv("DEBUG", False)
observer = Observer()

# add importer.main, trainer.main (or others) to trigger dags on startup
# run them manually with `python -m dags.trainer` and `python -m dags.trainer`
debug_startup_events = [db_client.connect, observer.start]

if DEBUG:
    os.environ["PREFECT__LOGGING__LEVEL"] = "DEBUG"
    app = FastAPI(
        title="Reyearn API",
        debug=DEBUG,
        on_startup=debug_startup_events,
        on_shutdown=[db_client.disconnect, observer.stop],
    )
else:
    app = FastAPI(
        title="Reyearn API",
        debug=DEBUG,
        on_startup=[db_client.connect, observer.start],
        on_shutdown=[db_client.disconnect, observer.stop],
    )
app.state.db_client = db_client
app.state.db_schemas = db_schemas

try:
    app.state.models = {}
    for dirpath, dirs, files in os.walk("./models"):
        for f in files:
            if ".joblib" in f:
                app.state.models[f.split(".joblib")[0]] = joblib_load(f"./models/{f}")
except FileNotFoundError:
    print("No models trained yet, plase run this first: python -m dags.trainer")
    sys.exit(1)


class ModelHotReloader(LoggingEventHandler):
    def on_modified(self, event):
        if ".joblib" in event.src_path:
            model_name = event.src_path.split(".joblib")[0].split("/")[2]
            app.state.models[model_name] = joblib_load(f"./models/{model_name}.joblib")
            logging.info(
                "Hot reloaded model: %s", app.state.models[model_name]["version"]
            )


event_handler = ModelHotReloader()
observer.schedule(event_handler, "./models")

app.include_router(handlers.router)

if __name__ == "__main__":
    import uvicorn

    if DEBUG:
        uvicorn.run(
            "server:app", host="0.0.0.0", port=8000, workers=1, reload=True,
        )
    else:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, workers=4)

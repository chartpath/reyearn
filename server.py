from starlette.applications import Starlette
from api.handlers import routes
from db.client import db as db_client
import db.schemas as db_schemas
from dags import importer

app = Starlette(
    debug=True,
    on_startup=[db_client.connect],
    on_shutdown=[db_client.disconnect],
    routes=routes,
)
app.state.db_client = db_client
app.state.db_schemas = db_schemas

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

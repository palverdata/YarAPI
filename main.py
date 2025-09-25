from fastapi import FastAPI
from yarapi.api.v1 import open_sea
from yarapi.api import router as index_router
from yarapi.utils.env import rename_envs
from yarapi.utils.swagger import register_custom_swagger

rename_envs()

app = FastAPI(
    title="Open Sea Search API",
    description="An API to search and process data from various social networks.",
)

app.include_router(open_sea.router, prefix="/v1", tags=["Open Sea Search"])
app.include_router(index_router, tags=["Index"])

app.openapi = lambda: register_custom_swagger(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)

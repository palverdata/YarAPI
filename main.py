from fastapi import FastAPI
from yarapi.api.v1 import search
from yarapi.api import router as index_router
from yarapi.utils.env import rename_envs

rename_envs()

app = FastAPI(
    title="Open Sea Search API",
    description="An API to search and process data from various social networks.",
)

app.include_router(search.router, prefix="/v1", tags=["Search"])
app.include_router(index_router, tags=["Index"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from yarapi.api.v1 import search

app = FastAPI(
    title="Open Sea Search API",
    description="An API to search and process data from various social networks.",
)

app.include_router(search.router, prefix="/v1", tags=["Search"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

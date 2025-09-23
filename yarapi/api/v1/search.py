from fastapi import APIRouter, HTTPException, status, Depends

from yarapi.models.schemas import SearchRequest, DataSource, SearchResponse
from yarapi.core.search_service import run_search
from yarapi.core.security import require_api_user

router = APIRouter()


class MyCache:
    _default_ttl: int

    def __init__(self, default_ttl=1800):
        self._default_ttl = default_ttl

    def exists(self, key):
        return key in self.__dict__

    def get(self, key):
        return self.__dict__.get(key, None)

    def set(self, key, value, ttl=None):
        print(f"Setting cache key: {key} with TTL: {ttl or self._default_ttl}")
        _ttl = ttl or self._default_ttl

        self.__dict__[key] = value
        # Note: TTL handling is not implemented in this simple example


global_cache = MyCache(default_ttl=3600)  # 1 hour TTL


@router.post(
    "/{datasource}/search",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
)
async def search_endpoint(
    datasource: DataSource,
    request: SearchRequest,
):
    global global_cache
    """
    Main endpoint to perform searches on different data sources.

    - **datasource**: The platform where the search will be performed (instagram, facebook, etc.).
    - **request body**: Contains the search parameters, such as queries, time range, and filters.
    """
    try:
        serialized_params = str(request.dict())

        if global_cache.exists(serialized_params):
            print("Returning cached results")
            cached_results = global_cache.get(serialized_params)

            return SearchResponse(
                results_count=len(cached_results),
                data=cached_results,
                headers={"X-Cache": "HIT"},
            )

        results = await run_search(datasource, request)

        global_cache.set(serialized_params, results)

        return SearchResponse(results_count=len(results), data=results)
    except Exception as e:
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return {"status": "ok"}

from fastapi import APIRouter, HTTPException, status, Depends, Response

from yarapi.models.schemas import (
    SearchRequest,
    DataSource,
    SearchResponse,
    ProfileInput,
    CommentsInput,
    TimeseriesInput,
)
from yarapi.core.search_service import (
    run_search,
    run_profile_search,
    run_comments_search,
    run_timeseries_search,
)
from yarapi.core.security import require_api_user
from yarapi.core.cache import cache

router = APIRouter()


@router.post(
    "/{datasource}/search",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
    summary="Searches for social media posts based on queries and filters.",
)
async def search_endpoint(
    datasource: DataSource,
    request: SearchRequest,
    response: Response,
):
    """
    Main endpoint to perform searches on different data sources.

    - **datasource**: The platform where the search will be performed (instagram, facebook, etc.).
    - **request body**: Contains the search parameters, such as queries, time range, and filters.
    """
    try:
        cache_key = f"{datasource.value}:search:{cache.serialize_key(request.dict())}"

        cached, ttl_left = cache.get_with_ttl(cache_key)

        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            response.headers["X-Cache-TTL-Remaining"] = str(ttl_left)
            response.headers["Cache-Control"] = f"public, max-age={ttl_left}"

            return SearchResponse(
                results_count=len(cached),
                data=cached,
            )

        results = await run_search(datasource, request)

        cache.set(cache_key, results)

        response.headers["X-Cache"] = "MISS"
        return SearchResponse(results_count=len(results), data=results)
    except Exception as e:
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{datasource}/profile",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
)
async def profile_endpoint(
    datasource: DataSource,
    request: ProfileInput,
    response: Response,
):
    """
    Retrieves a profile from a specific data source.

    - **datasource**: The platform to search on.
    - **identifier**: The username or URL of the profile.
    """
    try:
        cache_key = f"{datasource.value}:profile:{request.identifier}"
        cached, ttl_left = cache.get_with_ttl(cache_key)

        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            response.headers["X-Cache-TTL-Remaining"] = str(ttl_left)
            response.headers["Cache-Control"] = f"public, max-age={ttl_left}"
            return SearchResponse(
                results_count=1,
                data=cached,
            )

        result = await run_profile_search(datasource, request)
        cache.set(cache_key, result)

        response.headers["X-Cache"] = "MISS"
        return SearchResponse(results_count=1, data=result)
    except Exception as e:
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/{datasource}/comments",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
)
async def comments_endpoint(
    datasource: DataSource,
    request: CommentsInput,
    response: Response,
):
    """
    Retrieves comments from a post on a specific data source.

    - **datasource**: The platform to search on.
    - **identifier**: The post ID or URL.
    - **amount**: The number of comments to retrieve.
    """
    try:
        cache_key = f"{datasource.value}:comments:{request.identifier}:{request.amount}"
        cached, ttl_left = cache.get_with_ttl(cache_key)

        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            response.headers["X-Cache-TTL-Remaining"] = str(ttl_left)
            response.headers["Cache-Control"] = f"public, max-age={ttl_left}"
            return SearchResponse(
                results_count=len(cached),
                data=cached,
            )

        results = await run_comments_search(datasource, request)
        cache.set(cache_key, results)
        response.headers["X-Cache"] = "MISS"
        return SearchResponse(results_count=len(results), data=results)
    except Exception as e:
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/{datasource}/timeseries",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
)
async def timeseries_endpoint(
    datasource: DataSource,
    request: TimeseriesInput,
    response: Response,
):
    """
    Retrieves timeseries data for a profile on a specific data source.
    """
    try:
        cache_key = (
            f"{datasource.value}:timeseries:{cache.serialize_key(request.dict())}"
        )
        cached, ttl_left = cache.get_with_ttl(cache_key)

        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            response.headers["X-Cache-TTL-Remaining"] = str(ttl_left)
            response.headers["Cache-Control"] = f"public, max-age={ttl_left}"

            return SearchResponse(
                results_count=len(cached),
                data=cached,
            )

        results = await run_timeseries_search(datasource, request)
        cache.set(cache_key, results)

        response.headers["X-Cache"] = "MISS"
        return SearchResponse(results_count=len(results), data=results)
    except Exception as e:
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return {"status": "ok"}

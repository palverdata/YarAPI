from fastapi import APIRouter, HTTPException, status, Depends

from yarapi.models.schemas import SearchRequest, DataSource, SearchResponse
from yarapi.core.search_service import run_search
from yarapi.core.security import require_api_user

router = APIRouter()


@router.post(
    "/{datasource}/search",
    response_model=SearchResponse,
    dependencies=[Depends(require_api_user)],
)
async def search_endpoint(
    datasource: DataSource,
    request: SearchRequest,
):
    """
    Main endpoint to perform searches on different data sources.

    - **datasource**: The platform where the search will be performed (instagram, facebook, etc.).
    - **request body**: Contains the search parameters, such as queries, time range, and filters.
    """
    try:
        results = await run_search(datasource, request)
        return SearchResponse(results_count=len(results), data=results)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # In a production environment, log the error instead of printing it.
        print(f"Unexpected server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred.",
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return {"status": "ok"}

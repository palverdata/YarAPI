from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/",
    include_in_schema=False,
)
async def index_endpoint():
    return RedirectResponse(url="/docs", status_code=302)

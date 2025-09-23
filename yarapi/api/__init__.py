from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/")
async def index_endpoint():
    return RedirectResponse(url="/docs")

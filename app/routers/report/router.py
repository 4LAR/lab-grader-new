from fastapi import APIRouter

from .odt import odt

report_router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

report_router.add_api_route(
    "/odt",
    odt,
    methods=['POST']
)

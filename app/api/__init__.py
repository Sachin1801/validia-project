from fastapi import APIRouter

from .v1 import endpoints as v1_endpoints
from .v1 import bonus_endpoints

api_router = APIRouter()

# Prefix v1 endpoints with /v1
api_router.include_router(v1_endpoints.router, prefix="/v1")
api_router.include_router(bonus_endpoints.router, prefix="/v1")

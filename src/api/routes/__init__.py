from fastapi import APIRouter
from .analysis import router as analysis_router
from .vector_search import router as vector_router

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Document Analysis"])
router.include_router(vector_router, prefix="/api/v1/vector", tags=["Vector Search"]) 
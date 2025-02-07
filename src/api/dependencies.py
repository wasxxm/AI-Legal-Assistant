from fastapi import Request
from src.core.logging import setup_logging

logger = setup_logging()

async def get_request_logger(request: Request):
    """
    Dependency to log incoming requests
    
    Args:
        request (Request): FastAPI request object
    """
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    return logger 
import magic
from src.core.config import MAX_FILE_SIZE

async def validate_pdf(file_content: bytes) -> bool:
    """
    Validate if the uploaded file is a valid PDF and within size limits
    
    Args:
        file_content (bytes): Content of the uploaded file
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    if not file_content or len(file_content) == 0:
        return False
        
    if len(file_content) > MAX_FILE_SIZE:
        return False
    
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_content)
        return file_type == 'application/pdf'
    except Exception:
        return False 
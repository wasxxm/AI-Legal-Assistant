from fastapi import APIRouter, HTTPException, UploadFile, File
from src.domain.models.case import Case
from src.domain.services.document_analyzer import analyze_legal_document
from src.domain.services.pdf_validator import validate_pdf
from src.core.config import MAX_FILE_SIZE
from pydantic import BaseModel

router = APIRouter()

class ErrorResponse(BaseModel):
    detail: str
    code: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid file format. Only PDF files are supported.",
                "code": "INVALID_FILE_FORMAT"
            }
        }

@router.post("/", response_model=Case, responses={
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def analyze_case(file: UploadFile = File(...)):
    """
    Analyze a legal case document (PDF)
    
    - **file**: PDF file containing the legal case document
    
    Returns a structured analysis of the legal document including:
    - Basic case information (number, date, judges)
    - Court and bench details
    - Parties involved and their counsel
    - Procedural history and previous proceedings
    - Laws cited and their interpretation
    - Legal principles and precedents
    - Arguments and holdings
    - Constitutional provisions
    - Relief granted
    - Case summary and implications
    
    The analysis includes detailed information about:
    - Bench composition and special designations
    - Case classification and jurisdiction
    - Hearing dates and timeline
    - Constitutional and statutory provisions
    - Previous history and connected cases
    
    All dates are returned in ISO format (YYYY-MM-DD).
    Empty fields are returned as empty strings or arrays as appropriate.
    """
    # Validate file extension
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                detail="File must have .pdf extension",
                code="INVALID_FILE_FORMAT"
            ).dict()
        )
    
    try:
        contents = await file.read()
        
        # Validate file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    detail="File size exceeds maximum limit of 10MB",
                    code="FILE_TOO_LARGE"
                ).dict()
            )
        
        # Validate PDF format
        if not await validate_pdf(contents):
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    detail="Invalid PDF file format",
                    code="INVALID_FILE_FORMAT"
                ).dict()
            )
        
        analysis = await analyze_legal_document(contents)
        return analysis
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_msg = f"Error analyzing document: {str(e)}"
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=error_msg,
                code="INTERNAL_ERROR"
            ).dict()
        ) 
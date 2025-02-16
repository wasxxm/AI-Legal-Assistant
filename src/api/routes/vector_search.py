from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from src.domain.services.document_processor import DocumentProcessor
from src.domain.models.case import Case
from src.domain.models.vector_models import VectorCase, VectorCourt

router = APIRouter(tags=["Vector Search"])

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 10
    search_type: Optional[str] = "hybrid"

class SearchResult(BaseModel):
    case_number: str
    title: str
    court: str
    text_chunk: str
    similarity: float

def get_document_processor():
    processor = DocumentProcessor()
    try:
        yield processor
    finally:
        processor.close()

@router.post("/cases", response_model=dict)
async def create_case(
    case: VectorCase,
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Create a new case and generate its vector embeddings.
    
    Example request body:
    ```json
    {
        "case_number": "2023-ABC-123",
        "title": "Smith v. Jones",
        "date": "2023-01-01",
        "court": {
            "name": "Supreme Court",
            "jurisdiction": "Federal",
            "bench_type": "Constitutional"
        },
        "full_text": "This is the full text of the case...",
        "metadata": {
            "jurisdiction": "Federal",
            "category": "Civil"
        }
    }
    ```
    """
    try:
        case_id = await processor.process_document(case)
        return {"message": "Case created successfully", "case_id": case_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResult])
async def search_cases(
    query: SearchQuery,
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Search for similar cases using vector similarity.
    
    Example request body:
    ```json
    {
        "query": "contract breach damages calculation",
        "top_k": 10,
        "search_type": "hybrid"
    }
    ```
    
    The search_type can be either "hybrid" (combines vector and text search) 
    or "vector" (pure vector similarity search).
    """
    try:
        results = await processor.search_similar_cases(
            query=query.query,
            top_k=query.top_k,
            search_type=query.search_type
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=dict)
async def batch_process_cases(
    cases: List[VectorCase],
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Process multiple cases in batch.
    
    Example request body:
    ```json
    [
        {
            "case_number": "2023-ABC-123",
            "title": "Smith v. Jones",
            "date": "2023-01-01",
            "court": {
                "name": "Supreme Court",
                "jurisdiction": "Federal",
                "bench_type": "Constitutional"
            },
            "full_text": "Case 1 full text...",
            "metadata": {"jurisdiction": "Federal"}
        }
    ]
    ```
    """
    try:
        case_ids = await processor.batch_process_documents(cases)
        return {
            "message": f"Successfully processed {len(case_ids)} cases",
            "case_ids": case_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
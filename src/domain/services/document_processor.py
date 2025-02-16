from typing import List, Dict, Optional, Union
from datetime import datetime
from src.infrastructure.vector_store import VectorStore
from src.utils.text_chunking import TextChunker
from src.domain.models.vector_models import VectorCase

class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStore()
        self.text_chunker = TextChunker()

    async def process_document(self, case: VectorCase) -> int:
        """
        Process a legal document and store it in the vector database.
        Returns the case ID.
        """
        # Convert Pydantic models to dictionaries
        court_dict = case.court.model_dump() if case.court else {}
        metadata_dict = case.metadata.model_dump() if case.metadata else {}

        # Store the case basic information
        case_id = self.vector_store.store_case(
            case_number=case.case_number,
            title=case.title,
            date=case.date,  # date is already in the correct format
            court=court_dict,
            full_text=case.full_text,
            metadata=metadata_dict
        )

        # Create chunks with section awareness
        chunks = self.text_chunker.create_chunks(case.full_text)
        
        # Store section-aware chunks
        self.vector_store.store_embeddings(
            case_id=case_id,
            chunks=[chunk['text'] for chunk in chunks],
            embedding_type='section',
            chunk_metadata=[chunk['metadata'] for chunk in chunks]
        )

        # Create citation-aware chunks for specific sections
        citation_chunks = self.text_chunker.create_chunks_with_citations(case.full_text)
        
        # Store citation-aware chunks
        self.vector_store.store_embeddings(
            case_id=case_id,
            chunks=[chunk['text'] for chunk in citation_chunks],
            embedding_type='citation',
            chunk_metadata=[chunk['metadata'] for chunk in citation_chunks]
        )

        return case_id

    async def search_similar_cases(self, 
                                 query: str,
                                 top_k: int = 10,
                                 search_type: str = 'hybrid') -> List[Dict]:
        """
        Search for similar cases using either vector similarity or hybrid search.
        """
        if search_type == 'hybrid':
            return self.vector_store.hybrid_search(query, top_k)
        else:
            return await self.vector_store.similarity_search(query, top_k)

    async def batch_process_documents(self, cases: List[VectorCase]) -> List[int]:
        """
        Process multiple documents in batch.
        Returns list of case IDs.
        """
        case_ids = []
        for case in cases:
            case_id = await self.process_document(case)
            case_ids.append(case_id)
        return case_ids

    def close(self):
        """Close the vector store connection."""
        self.vector_store.close() 
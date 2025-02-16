from typing import List, Optional, Dict, Any
import psycopg2
import json
from psycopg2.extras import execute_values, Json
import numpy as np
from sentence_transformers import SentenceTransformer
from src.core.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.connection = self._create_connection()
        self._init_database()

    def _create_connection(self):
        return psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )

    def _init_database(self):
        with self.connection.cursor() as cursor:
            # Enable vector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    id SERIAL PRIMARY KEY,
                    case_number VARCHAR(100),
                    title TEXT,
                    date DATE,
                    court JSONB,
                    full_text TEXT,
                    metadata JSONB
                );
            """)
            
            # Create embeddings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_embeddings (
                    id SERIAL PRIMARY KEY,
                    case_id INTEGER REFERENCES cases(id),
                    embedding_type VARCHAR(50),
                    embedding vector(768),
                    text_chunk TEXT,
                    chunk_metadata JSONB
                );
            """)
            
            # Create HNSW index for fast similarity search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS case_embeddings_embedding_idx 
                ON case_embeddings 
                USING hnsw (embedding vector_cosine_ops);
            """)
            
        self.connection.commit()

    def store_case(self, case_number: str, title: str, date: str, court: Dict, 
                   full_text: str, metadata: Dict[str, Any]) -> int:
        """Store case information and return the case ID."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cases (case_number, title, date, court, full_text, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (case_number, title, date, Json(court), full_text, Json(metadata)))
            case_id = cursor.fetchone()[0]
            self.connection.commit()
            return case_id

    def store_embeddings(self, case_id: int, chunks: List[str], 
                        embedding_type: str = 'paragraph',
                        chunk_metadata: Optional[List[Dict]] = None):
        """Store embeddings for text chunks."""
        if chunk_metadata is None:
            chunk_metadata = [{}] * len(chunks)

        # Generate embeddings in batches
        embeddings = self.embedding_model.encode(chunks)
        
        with self.connection.cursor() as cursor:
            execute_values(cursor, """
                INSERT INTO case_embeddings 
                (case_id, embedding_type, embedding, text_chunk, chunk_metadata)
                VALUES %s;
            """, [
                (case_id, embedding_type, embedding.tolist(), chunk, meta)
                for embedding, chunk, meta in zip(embeddings, chunks, chunk_metadata)
            ])
        self.connection.commit()

    async def similarity_search(self, query: str, top_k: int = 10, 
                              similarity_threshold: float = 0.7) -> List[Dict]:
        """Perform similarity search for a query."""
        query_embedding = self.embedding_model.encode(query)
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.case_number,
                    c.title,
                    c.court->>'name' as court_name,
                    ce.text_chunk,
                    1 - (ce.embedding <=> %s) as similarity
                FROM 
                    cases c
                    JOIN case_embeddings ce ON c.id = ce.case_id
                WHERE 
                    1 - (ce.embedding <=> %s) > %s
                ORDER BY 
                    similarity DESC
                LIMIT %s;
            """, (query_embedding.tolist(), query_embedding.tolist(), 
                  similarity_threshold, top_k))
            
            results = cursor.fetchall()
            
            return [{
                'case_number': r[0],
                'title': r[1],
                'court': r[2],
                'text_chunk': r[3],
                'similarity': float(r[4])
            } for r in results]

    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Combine vector similarity search with full-text search."""
        query_embedding = self.embedding_model.encode(query)
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                WITH vector_results AS (
                    SELECT 
                        c.id,
                        c.case_number,
                        c.title,
                        c.court->>'name' as court_name,
                        ce.text_chunk,
                        1 - (ce.embedding <=> %s) as similarity
                    FROM 
                        cases c
                        JOIN case_embeddings ce ON c.id = ce.case_id
                    WHERE 
                        1 - (ce.embedding <=> %s) > 0.7
                ),
                text_results AS (
                    SELECT 
                        c.id,
                        c.case_number,
                        c.title,
                        c.court->>'name' as court_name,
                        c.full_text as text_chunk,
                        ts_rank_cd(to_tsvector('english', c.full_text), 
                                 plainto_tsquery('english', %s)) as similarity
                    FROM 
                        cases c
                    WHERE 
                        to_tsvector('english', c.full_text) @@ 
                        plainto_tsquery('english', %s)
                )
                SELECT * FROM (
                    SELECT * FROM vector_results
                    UNION
                    SELECT * FROM text_results
                ) combined
                ORDER BY similarity DESC
                LIMIT %s;
            """, (query_embedding.tolist(), query_embedding.tolist(), 
                  query, query, top_k))
            
            results = cursor.fetchall()
            
            return [{
                'case_number': r[1],
                'title': r[2],
                'court': r[3],
                'text_chunk': r[4],
                'similarity': float(r[5])
            } for r in results]

    def close(self):
        """Close the database connection."""
        self.connection.close() 
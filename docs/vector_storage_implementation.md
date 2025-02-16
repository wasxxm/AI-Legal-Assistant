# Vector Storage Implementation Documentation

## Overview
This document details the implementation of vector storage for legal documents in our system. The implementation uses PostgreSQL with pgvector extension for efficient similarity search and hybrid search capabilities.

## Components

### 1. Vector Store (`src/infrastructure/vector_store.py`)
The core component that handles all vector storage operations using PostgreSQL with pgvector.

#### Key Features:
- HNSW indexing for fast similarity search
- Hybrid search combining vector similarity and full-text search
- Efficient batch processing of embeddings
- Support for different embedding types (section-based, citation-based)

#### Database Schema:
```sql
-- Cases table storing document metadata
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(100),
    title TEXT,
    date DATE,
    court VARCHAR(100),
    full_text TEXT,
    metadata JSONB
);

-- Embeddings table storing vector representations
CREATE TABLE case_embeddings (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    embedding_type VARCHAR(50),
    embedding vector(768),
    text_chunk TEXT,
    chunk_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Text Chunking (`src/utils/text_chunking.py`)
Handles the intelligent splitting of legal documents into meaningful chunks.

#### Features:
- Section-aware chunking based on legal document structure
- Citation-aware chunking preserving legal references
- Configurable chunk size and overlap
- Rich metadata generation for chunks

#### Section Types:
- Facts
- Issues
- Arguments
- Analysis
- Holding
- Headnotes

### 3. Document Processor (`src/domain/services/document_processor.py`)
High-level service coordinating document processing and storage.

#### Capabilities:
- Single document processing
- Batch document processing
- Multiple embedding types per document
- Flexible search options

## Usage Examples

### 1. Processing a New Document
```python
from src.domain.services.document_processor import DocumentProcessor
from src.domain.models.case import Case

processor = DocumentProcessor()

case = Case(
    case_number="2023-ABC-123",
    title="Smith v. Jones",
    date="2023-01-01",
    court="Supreme Court",
    full_text="...",
    metadata={"jurisdiction": "Federal"}
)

case_id = await processor.process_document(case)
```

### 2. Searching Similar Cases
```python
# Hybrid search (vector + full-text)
results = await processor.search_similar_cases(
    query="contract breach damages",
    top_k=10,
    search_type="hybrid"
)

# Pure vector similarity search
results = await processor.search_similar_cases(
    query="contract breach damages",
    search_type="vector"
)
```

## Performance Optimization

### 1. Database Indexing
- HNSW index for approximate nearest neighbor search
- Full-text search index for hybrid search
- Regular B-tree indexes for metadata fields

### 2. Chunking Strategy
- Optimal chunk size: 500 tokens
- Overlap: 50 tokens
- Section-aware boundaries
- Citation preservation

### 3. Batch Processing
- Efficient batch insertion of embeddings
- Connection pooling
- Prepared statements

## Maintenance

### 1. Regular Tasks
- Index maintenance
- Statistics update
- Performance monitoring
- Database vacuuming

### 2. Monitoring Metrics
- Query response time
- Index size
- Cache hit ratio
- Storage usage

## Security Considerations

### 1. Data Protection
- Secure database connections
- Access control
- Input validation
- SQL injection prevention

### 2. Error Handling
- Connection error recovery
- Transaction management
- Data validation
- Logging and monitoring

## Future Improvements

### 1. Planned Enhancements
- Multi-model embedding support
- Cross-lingual search
- Dynamic chunk sizing
- Advanced relevance scoring

### 2. Scaling Considerations
- Sharding strategies
- Read replicas
- Connection pooling
- Caching layer

## Dependencies

### Required Packages
```
psycopg2-binary
pgvector
sentence-transformers
nltk
```

### System Requirements
- PostgreSQL 14+ with pgvector extension
- Python 3.8+
- Sufficient RAM for embedding generation
- SSD storage recommended

## Setup Instructions

### 1. Database Setup
```bash
# Install pgvector extension
CREATE EXTENSION vector;

# Create necessary tables
# (See schema above)
```

### 2. Python Environment
```bash
pip install -r requirements.txt
```

### 3. Configuration
Update `src/core/config.py` with database credentials and other settings:
```python
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legal_db
DB_USER=user
DB_PASSWORD=password
```

## Best Practices

### 1. Document Processing
- Validate input documents
- Handle different document formats
- Preserve document structure
- Maintain citation integrity

### 2. Search Optimization
- Use appropriate chunk sizes
- Balance precision vs. recall
- Implement caching
- Monitor search quality

### 3. Error Handling
- Implement retries
- Validate inputs
- Log errors
- Maintain transactions

## Troubleshooting

### Common Issues
1. Slow search performance
   - Check index health
   - Optimize chunk size
   - Update statistics

2. High memory usage
   - Batch processing
   - Connection pooling
   - Resource monitoring

3. Connection issues
   - Connection pool settings
   - Network configuration
   - Error handling 
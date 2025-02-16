from typing import List, Dict, Optional
import re
from nltk.tokenize import sent_tokenize
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _identify_section_boundaries(self, text: str) -> List[Dict[str, any]]:
        """Identify important sections in the legal document."""
        sections = []
        
        # Common section headers in legal documents
        section_patterns = {
            'facts': r'(?i)(brief\s+facts|statement\s+of\s+facts|factual\s+background)',
            'issues': r'(?i)(issues?(\s+involved)?|questions?\s+of\s+law)',
            'arguments': r'(?i)(arguments?|submissions?|contentions?)',
            'analysis': r'(?i)(analysis|discussion|reasoning)',
            'holding': r'(?i)(holding|conclusion|order|judgment|decree)',
            'headnotes': r'(?i)(headnotes?|syllabus|synopsis)'
        }

        for section_type, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in matches:
                sections.append({
                    'type': section_type,
                    'start': match.start(),
                    'text': match.group()
                })

        # Sort sections by their appearance in the text
        sections.sort(key=lambda x: x['start'])
        return sections

    def _get_section_chunks(self, text: str, section_type: str) -> List[Dict[str, str]]:
        """Create chunks from a specific section with appropriate metadata."""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Store the current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'section_type': section_type,
                        'length': current_length
                    }
                })
                
                # Start new chunk with overlap
                overlap_tokens = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_tokens + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add the last chunk if it exists
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'section_type': section_type,
                    'length': current_length
                }
            })

        return chunks

    def create_chunks(self, text: str) -> List[Dict[str, str]]:
        """Process the full text into semantic chunks with metadata."""
        sections = self._identify_section_boundaries(text)
        chunks = []

        # If no sections are identified, process the whole text as one section
        if not sections:
            return self._get_section_chunks(text, 'body')

        # Process each section
        for i, section in enumerate(sections):
            # Determine section text boundaries
            start = section['start']
            end = sections[i + 1]['start'] if i < len(sections) - 1 else len(text)
            
            # Extract and chunk the section text
            section_text = text[start:end]
            section_chunks = self._get_section_chunks(section_text, section['type'])
            chunks.extend(section_chunks)

        return chunks

    def create_chunks_with_citations(self, text: str) -> List[Dict[str, str]]:
        """Create chunks while preserving legal citations."""
        # Citation pattern matching common legal citation formats
        citation_pattern = r'(\d+\s+\w+\s+\d+|\[\d+\]\s+\w+\s+\d+)'
        
        # Split text at citation boundaries while preserving citations
        parts = re.split(f'({citation_pattern})', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        current_citations = []

        for part in parts:
            # Check if part is a citation
            is_citation = bool(re.match(citation_pattern, part.strip()))
            words = part.split()
            part_length = len(words)

            if is_citation:
                current_citations.append(part.strip())
                continue

            if current_length + part_length > self.chunk_size and current_chunk:
                # Store current chunk with its citations
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'citations': current_citations.copy(),
                        'length': current_length
                    }
                })
                
                # Reset for next chunk with overlap
                overlap_words = words[:self.overlap] if part_length > self.overlap else words
                current_chunk = overlap_words
                current_length = len(overlap_words)
                current_citations = []
            else:
                current_chunk.extend(words)
                current_length += part_length

        # Add the last chunk if it exists
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'citations': current_citations,
                    'length': current_length
                }
            })

        return chunks 
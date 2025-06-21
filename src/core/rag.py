import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from .vector_db import get_vector_db
from ..core.config import config

logger = logging.getLogger(__name__)

class RAGSystem:
    """A Retrieval Augmented Generation system for document processing and querying."""
    
    def __init__(self, collection_name: str = "documents"):
        """Initialize the RAG system.
        
        Args:
            collection_name: Name of the collection to use in the vector DB
        """
        self.collection_name = collection_name
        self.vector_db = get_vector_db()
        self.text_splitter = self._get_text_splitter()
    
    def _get_text_splitter(self):
        """Get a text splitter for chunking documents."""
        # Using a simple character-based splitter for now
        # Could be replaced with more sophisticated splitters like RecursiveCharacterTextSplitter
        class SimpleTextSplitter:
            def __init__(self, chunk_size=1000, chunk_overlap=200):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
            
            def split_text(self, text: str) -> List[str]:
                """Split text into chunks."""
                if not text:
                    return []
                
                # First, try to split on paragraphs
                chunks = []
                paragraphs = re.split(r'\n\s*\n', text)
                
                current_chunk = []
                current_length = 0
                
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                        
                    para_length = len(para)
                    
                    # If paragraph is too big, split it further
                    if para_length > self.chunk_size:
                        if current_chunk:
                            chunks.append("\n".join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        
                        # Split the large paragraph into sentences
                        sentences = re.split(r'(?<=[.!?])\s+', para)
                        sentence_chunk = []
                        chunk_len = 0
                        
                        for sentence in sentences:
                            sent_len = len(sentence)
                            if chunk_len + sent_len > self.chunk_size and sentence_chunk:
                                chunks.append(" ".join(sentence_chunk))
                                sentence_chunk = sentence_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                                chunk_len = sum(len(s) + 1 for s in sentence_chunk)
                            
                            sentence_chunk.append(sentence)
                            chunk_len += sent_len + 1
                        
                        if sentence_chunk:
                            chunks.append(" ".join(sentence_chunk))
                    else:
                        if current_length + para_length > self.chunk_size and current_chunk:
                            chunks.append("\n".join(current_chunk))
                            # Keep some overlap between chunks
                            current_chunk = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                            current_length = sum(len(p) + 2 for p in current_chunk)
                        
                        current_chunk.append(para)
                        current_length += para_length + 2
                
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                
                return chunks
        
        return SimpleTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    async def add_documents(self, documents: List[Dict[str, Any]], **kwargs) -> bool:
        """Add documents to the RAG system.
        
        Args:
            documents: List of dicts with 'text' and 'metadata' keys
            **kwargs: Additional arguments like 'chunk_size' and 'chunk_overlap'
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not documents:
            return False
            
        chunk_size = kwargs.get('chunk_size', 1000)
        chunk_overlap = kwargs.get('chunk_overlap', 200)
        
        processed_docs = []
        
        for doc in documents:
            text = doc.get('text', '').strip()
            if not text:
                continue
                
            metadata = doc.get('metadata', {})
            doc_id = doc.get('id')
            
            # Split the document into chunks
            chunks = self.text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}" if doc_id else f"chunk_{hash(chunk)}"
                processed_docs.append({
                    'id': chunk_id,
                    'text': chunk,
                    'metadata': {
                        **metadata,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'source': metadata.get('source', 'unknown')
                    }
                })
        
        # Add to vector DB
        if processed_docs:
            return self.vector_db.add_documents(processed_docs, self.collection_name)
        return False
    
    async def query(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None, **kwargs) -> List[Dict[str, Any]]:
        """Query the RAG system for relevant documents.
        
        Args:
            query: The search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
            **kwargs: Additional arguments for the search
            
        Returns:
            List of relevant document chunks with scores and metadata
        """
        try:
            results = self.vector_db.search(
                query=query,
                k=min(k, 10),  # Limit to 10 results max
                collection_name=self.collection_name,
                filter_metadata=filter_metadata
            )
            
            # Process and format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result['text'],
                    'metadata': result['metadata'],
                    'score': result.get('score', 0.0)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return []
    
    async def delete_collection(self) -> bool:
        """Delete the current collection."""
        return self.vector_db.delete_collection(self.collection_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection."""
        return self.vector_db.get_collection_stats(self.collection_name)


def get_rag_system(collection_name: str = "documents") -> RAGSystem:
    """Get a configured instance of RAGSystem."""
    return RAGSystem(collection_name=collection_name)

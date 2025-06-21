import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    """A wrapper around ChromaDB for vector storage and retrieval."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the vector database.
        
        Args:
            config: Configuration dictionary with 'type', 'path', and 'collection_name'
        """
        self.config = config
        self.client = self._init_client()
        self.embedding_function = self._init_embedding_function()
        self.collection = self._get_or_create_collection()
    
    def _init_client(self) -> chromadb.Client:
        """Initialize the ChromaDB client."""
        try:
            return chromadb.PersistentClient(
                path=self.config['path'],
                settings=Settings(anonymized_telemetry=False)
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
    
    def _init_embedding_function(self):
        """Initialize the embedding function."""
        # For now, we'll use the default all-MiniLM-L6-v2 model
        return embedding_functions.DefaultEmbeddingFunction()
    
    def _get_or_create_collection(self, name: Optional[str] = None) -> chromadb.Collection:
        """Get or create a collection in the database."""
        collection_name = name or self.config.get('collection_name', 'documents')
        try:
            return self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
        except Exception as e:
            logger.error(f"Failed to get or create collection '{collection_name}': {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], collection_name: Optional[str] = None) -> bool:
        """Add documents to the vector database.
        
        Args:
            documents: List of dicts with 'text', 'metadata', and optionally 'id' keys
            collection_name: Optional collection name (uses default if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not documents:
            return False
            
        try:
            collection = self._get_or_create_collection(collection_name)
            
            # Prepare batch data
            ids = []
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = doc.get('id', f"doc_{i}_{hash(doc['text'])}")
                ids.append(doc_id)
                texts.append(doc['text'])
                metadatas.append(doc.get('metadata', {}))
            
            # Add to collection
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector DB: {str(e)}")
            return False
    
    def search(self, query: str, k: int = 5, collection_name: Optional[str] = None, 
               filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database.
        
        Args:
            query: The search query
            k: Number of results to return
            collection_name: Optional collection name
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': results['distances'][0][i] if results.get('distances') else None
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector DB: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the database."""
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {str(e)}")
            return False
    
    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about a collection."""
        try:
            collection = self._get_or_create_collection(collection_name)
            return {
                'name': collection.name,
                'count': collection.count(),
                'metadata': collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}


def get_vector_db() -> VectorDB:
    """Get a configured instance of VectorDB."""
    from ..core.config import config
    return VectorDB({
        'type': config.VECTOR_DB_TYPE,
        'path': config.VECTOR_DB_PATH,
        'collection_name': 'default'
    })

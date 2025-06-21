import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.rag import get_rag_system
from src.core.config import config

def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "#"))
    print("=" * 80 + "\n")

async def test_rag_system():
    """Test the RAG system with sample documents and queries."""
    # Initialize RAG system
    print_header("Initializing RAG System")
    rag = get_rag_system("test_collection")
    
    # Sample documents
    documents = [
        {
            "text": """
            Helium AI is an advanced multi-agent system designed for comprehensive research analysis. 
            It consists of four specialized agents: Zane (Team Leader), Mira (Data Scientist), 
            Chloe (Financial Analyst), and Axel (Business Strategist).
            """,
            "metadata": {
                "source": "introduction.txt",
                "type": "overview"
            }
        },
        {
            "text": """
            The vector database is a core component of the RAG system, enabling efficient 
            semantic search and retrieval of relevant information. It stores document embeddings 
            and allows for similarity-based searches.
            """,
            "metadata": {
                "source": "tech_docs.txt",
                "type": "technical"
            }
        },
        {
            "text": """
            To use the RAG system, first add documents to the vector database, then query it 
            with natural language questions. The system will retrieve the most relevant 
            document chunks and use them to generate accurate responses.
            """,
            "metadata": {
                "source": "usage.txt",
                "type": "instruction"
            }
        }
    ]
    
    # Add documents to the RAG system
    print_header("Adding Documents to RAG System")
    success = await rag.add_documents(documents)
    print(f"Documents added successfully: {success}")
    
    # Perform some test queries
    test_queries = [
        "What is Helium AI?",
        "How does the vector database work?",
        "What are the main components of the system?",
        "How do I use the RAG system?"
    ]
    
    for query in test_queries:
        print_header(f"Query: {query}")
        results = await rag.query(query, k=2)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
            print(f"Source: {result['metadata'].get('source', 'unknown')}")
            print(f"Content: {result['content']}\n")
    
    # Print collection stats
    stats = rag.get_stats()
    print_header("Collection Statistics")
    print(f"Collection Name: {stats.get('name')}")
    print(f"Document Count: {stats.get('count', 0)}")
    
    # Clean up (optional)
    # await rag.delete_collection()
    # print("\nTest collection deleted.")

if __name__ == "__main__":
    asyncio.run(test_rag_system())

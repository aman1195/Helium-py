import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.rag import get_rag_system

def print_header(text):
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "#"))
    print("=" * 80 + "\n")

async def main():
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
            "metadata": {"source": "introduction.txt", "type": "overview"}
        },
        {
            "text": """
            The vector database is a core component of the RAG system, enabling efficient 
            semantic search and retrieval of relevant information. It stores document embeddings 
            and allows for similarity-based searches.
            """,
            "metadata": {"source": "tech_docs.txt", "type": "technical"}
        }
    ]
    
    # Add documents
    print_header("Adding Documents")
    success = await rag.add_documents(documents)
    print(f"Documents added: {success}")
    
    # Test query
    query = "What is Helium AI?"
    print_header(f"Query: {query}")
    results = await rag.query(query, k=1)
    
    if results:
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
            print(f"Source: {result['metadata'].get('source', 'unknown')}")
            print(f"Content: {result['content']}")
    else:
        print("No results found.")
    
    # Print stats
    stats = rag.get_stats()
    print_header("Collection Statistics")
    print(f"Collection Name: {stats.get('name', 'N/A')}")
    print(f"Document Count: {stats.get('count', 0)}")

if __name__ == "__main__":
    asyncio.run(main())

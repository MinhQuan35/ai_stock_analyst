"""
Test Qdrant vector store
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.utils import logger
from src.llm import get_embeddings_model
from src.rag.stores.qdrant_store import QdrantStore
from src.rag.loaders.directory_loader import DirectoryLoader
from src.rag.splitters.recursive_splitter import RecursiveTextSplitter
from src.rag.retrievers.similarity_retriever import SimilarityRetriever


def main():
    print("=" * 50)
    print("  Qdrant Vector Store Test")
    print("=" * 50)
    
    # 1. Connect to Qdrant
    print("\n[1] Connecting to Qdrant Cloud...")
    embeddings = get_embeddings_model()
    store = QdrantStore(embeddings)
    print(f"  Collection: {store.collection_name}")
    
    # 2. Load documents
    print("\n[2] Loading documents...")
    loader = DirectoryLoader(str(Path(__file__).parent.parent / settings.rag_data_dir))
    documents = loader.load()
    print(f"  Loaded {len(documents)} documents")
    
    # 3. Split
    print("\n[3] Splitting documents...")
    splitter = RecursiveTextSplitter()
    chunks = splitter.split(documents)
    print(f"  Created {len(chunks)} chunks")
    
    # 4. Index to Qdrant
    print("\n[4] Indexing to Qdrant Cloud...")
    store.create_from_documents(chunks)
    print(f"  Total points: {store.count()}")
    
    # 5. Test search
    print("\n[5] Test search...")
    store.load()  # Get store object
    retriever = SimilarityRetriever(store, k=3)
    
    queries = [
        "What is P/E ratio?",
        "When is RSI overbought?",
    ]
    
    for q in queries:
        print(f"\n  Q: {q}")
        results = retriever.retrieve(q)
        print(f"  Found {len(results)} docs")
        for i, doc in enumerate(results):
            print(f"    [{i+1}] {doc.page_content[:80]}...")
    
    print("\n" + "=" * 50)
    print("  TEST COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()

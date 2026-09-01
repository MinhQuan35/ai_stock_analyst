"""
Crawl real financial news and index into Qdrant
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.crawlers import NewsCrawler
from src.rag.stores.qdrant_store import QdrantStore
from src.rag.splitters.recursive_splitter import RecursiveTextSplitter
from src.llm import get_embeddings_model
from src.config import settings
from src.utils import logger
from langchain_core.documents import Document


def crawl_and_index():
    """Crawl news articles and index to Qdrant."""
    print("=" * 50)
    print("  CRAWL & INDEX FINANCIAL NEWS")
    print("=" * 50)
    
    # Step 1: Get articles
    print("\n[1] Loading articles...")
    crawler = NewsCrawler()
    articles = crawler.load_sample_articles()
    print(f"  Loaded {len(articles)} articles")
    
    # Group by country
    vn = [a for a in articles if a.get("country") == "Vietnam"]
    intl = [a for a in articles if a.get("country") != "Vietnam"]
    print(f"  Vietnam: {len(vn)} articles")
    print(f"  International: {len(intl)} articles")
    
    # Step 2: Save to JSON
    print("\n[2] Saving articles...")
    output_file = crawler.save_articles(articles)
    print(f"  Saved to: {output_file}")
    
    # Step 3: Convert to Documents
    print("\n[3] Converting to documents...")
    documents = []
    for article in articles:
        content = f"""# {article['title']}

Source: {article['source']}
Country: {article.get('country', 'Unknown')}
URL: {article.get('url', '')}

{article['content']}
"""
        doc = Document(
            page_content=content,
            metadata={
                "source": article["source"],
                "country": article.get("country", "Unknown"),
                "title": article["title"],
                "url": article.get("url", ""),
                "type": "news",
            },
        )
        documents.append(doc)
    print(f"  Created {len(documents)} documents")
    
    # Step 4: Split documents
    print("\n[4] Splitting documents...")
    splitter = RecursiveTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split(documents)
    print(f"  Created {len(chunks)} chunks")
    
    # Step 5: Index to Qdrant
    print("\n[5] Indexing to Qdrant Cloud...")
    embeddings = get_embeddings_model()
    store = QdrantStore(
        embeddings,
        collection_name="financial_news",
    )
    store.create_from_documents(chunks)
    print(f"  Indexed {store.count()} points to Qdrant")
    
    # Step 6: Test search
    print("\n[6] Testing search...")
    test_queries = [
        "What is Apple's revenue growth?",
        "Vinamilk Q3 results",
        "AI services revenue",
        "Nvidia data center growth",
    ]
    
    store.load()
    
    for q in test_queries:
        print(f"\n  Q: {q}")
        from langchain_qdrant import QdrantVectorStore
        from qdrant_client.http import models
        
        results = store.get_store().similarity_search(q, k=2)
        for i, doc in enumerate(results):
            title = doc.metadata.get("title", "N/A")
            country = doc.metadata.get("country", "N/A")
            print(f"    [{i+1}] {title} ({country})")
    
    print("\n" + "=" * 50)
    print("  DONE! Articles indexed to Qdrant")
    print("=" * 50)


if __name__ == "__main__":
    crawl_and_index()

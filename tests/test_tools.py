"""
Unit tests for Agent Tools (Loaders, Splitter, Crawler)
"""
import sys
import unittest
from pathlib import Path
from langchain_core.documents import Document

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import RecursiveTextSplitter, NewsCrawler


class TestTools(unittest.TestCase):
    """Test tools functionality."""
    
    def test_recursive_splitter(self):
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=10)
        doc = Document(page_content="This is a long financial sentence that needs to be split into chunks appropriately.")
        chunks = splitter.split([doc])
        self.assertTrue(len(chunks) >= 1)
    
    def test_news_crawler_sample_articles(self):
        crawler = NewsCrawler()
        articles = crawler.load_sample_articles()
        self.assertTrue(len(articles) > 0)
        self.assertIn("title", articles[0])


if __name__ == "__main__":
    unittest.main()

"""
News Crawler - Fetches financial news articles
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from src.utils import logger


class NewsCrawler:
    """Crawl financial news from various sources."""
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(self, output_dir: str = "./data/crawled"):
        """Initialize crawler."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
    
    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch HTML content from URL."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for elem in soup(["script", "style", "nav", "header", "footer", "aside"]):
            elem.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Remove excessive blank lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)
    
    def save_articles(self, articles: List[Dict]) -> Path:
        """Save articles to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"articles_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(articles)} articles to {output_file}")
        return output_file
    
    def load_articles(self, filepath: str) -> List[Dict]:
        """Load articles from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_sample_articles(self) -> List[Dict]:
        """Load sample articles for demo."""
        from src.rag.crawlers.sample_articles import SAMPLE_ARTICLES
        logger.info(f"Loaded {len(SAMPLE_ARTICLES)} sample articles")
        return SAMPLE_ARTICLES

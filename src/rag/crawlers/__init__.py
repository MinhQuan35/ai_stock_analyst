"""
Web Crawlers for financial news
"""
from .news_crawler import NewsCrawler
from .sample_articles import SAMPLE_ARTICLES

__all__ = ["NewsCrawler", "SAMPLE_ARTICLES"]

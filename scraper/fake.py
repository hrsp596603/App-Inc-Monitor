import datetime
from typing import List, Dict, Any
from utils.logger import setup_logger
from scraper.base import BaseScraper

logger = setup_logger(__name__)

class FakeScraper(BaseScraper):
    """
    用於開發初期測試的假資料搜集器
    """
    
    def fetch_data(self, query: str = "Apple", limit: int = 10) -> List[Dict[str, Any]]:
        logger.info(f"[FakeScraper] 正在抓取 '{query}' 相關的新聞 (上限: {limit})")
        
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        return [
            {
                "id": "news_001",
                "source": "TechDaily",
                "title": "Apple announces record-breaking Q4 earnings",
                "content": "Apple Inc. reported its highest revenue ever this quarter, driven by strong iPhone sales globally.",
                "url": "https://example.com/news/1",
                "published_at": now
            },
            {
                "id": "news_002",
                "source": "MarketWatch",
                "title": "Apple's new product launch faces unexpected delays",
                "content": "Supply chain constraints have caused Apple to push back the release of its highly anticipated VR headset by several months.",
                "url": "https://example.com/news/2",
                "published_at": now
            },
            {
                "id": "news_003",
                "source": "AppleInsider",
                "title": "New Apple store opens in downtown Tokyo",
                "content": "A brand new retail location featuring the latest design language has just opened its doors in Japan.",
                "url": "https://example.com/news/3",
                "published_at": now
            }
        ][:limit]

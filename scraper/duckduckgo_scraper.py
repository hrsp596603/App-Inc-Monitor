import os
import datetime
from typing import List, Dict, Any
from utils.logger import setup_logger
from scraper.base import BaseScraper
from scraper.fake import FakeScraper

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

logger = setup_logger(__name__)

class DuckDuckGoScraper(BaseScraper):
    """
    透過 DuckDuckGo 搜集即時新聞與內容 (免 API Key)
    """
    
    def __init__(self):
        self.fallback_scraper = FakeScraper()
        if DDGS is None:
            logger.warning("未安裝 ddgs，DuckDuckGoScraper 將自動退回使用 FakeScraper。")
            
    def fetch_data(self, query: str = "Apple Inc. latest news", limit: int = 5) -> List[Dict[str, Any]]:
        if DDGS is None:
            return self.fallback_scraper.fetch_data(query, limit)
            
        logger.info(f"[DuckDuckGoScraper] 正在使用 DuckDuckGo 網頁搜尋 '{query}' (上限: {limit})")
        
        try:
            ddgs_client = DDGS()
            # 搜尋新聞
            ddg_results = ddgs_client.news(query, max_results=limit)
            
            results = []
            for i, res in enumerate(ddg_results):
                # ddg_results 中的每筆資料包含的常見欄位: title, date, body, url, image, source
                results.append({
                    "id": f"ddg_{int(datetime.datetime.now().timestamp())}_{i}",
                    "source": res.get("source", "DuckDuckGo"),
                    "title": res.get("title", ""),
                    "content": res.get("body", ""),
                    "url": res.get("url", ""),
                    "image_url": res.get("image", ""),
                    "published_at": res.get("date", datetime.datetime.now(datetime.timezone.utc).isoformat())
                })
            
            logger.info(f"[DuckDuckGoScraper] 成功取得 {len(results)} 筆新聞資料。")
            return results
            
        except Exception as e:
            logger.error(f"[DuckDuckGoScraper] 搜尋時發生錯誤: {e}，自動退回使用假資料。")
            return self.fallback_scraper.fetch_data(query, limit)

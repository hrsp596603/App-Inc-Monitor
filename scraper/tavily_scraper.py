import os
import datetime
from typing import List, Dict, Any
from utils.logger import setup_logger
from scraper.base import BaseScraper
from scraper.fake import FakeScraper

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = setup_logger(__name__)

class TavilyScraper(BaseScraper):
    """
    透過 Tavily AI Search API 搜集真實的即時新聞與內容
    """
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.is_valid_key = (
            self.api_key is not None
            and isinstance(self.api_key, str)
            and TavilyClient is not None
            and not self.api_key.startswith("your_") 
            and len(self.api_key) > 5
        )
        
        self.fallback_scraper = FakeScraper()
        
        if self.is_valid_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("未設定有效的 TAVILY_API_KEY 或未安裝 tavily-python，TavilyScraper 將自動退回使用 FakeScraper。")
            
    def fetch_data(self, query: str = "Apple Inc. latest news", limit: int = 5) -> List[Dict[str, Any]]:
        if not self.client:
            return self.fallback_scraper.fetch_data(query, limit)
            
        logger.info(f"[TavilyScraper] 正在使用 Tavily 網頁搜尋 '{query}' (上限: {limit})")
        
        try:
            # 呼叫 Tavily API
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=limit,
                include_raw_content=False,
                include_images=True,
                topic="news"
            )
            
            results = []
            images_list = response.get("images", [])
            for i, res in enumerate(response.get("results", [])):
                img_url = res.get("image_url", "")
                if not img_url and images_list and i < len(images_list):
                    img_url = images_list[i]
                    
                results.append({
                    "id": f"tavily_{i}",
                    "source": res.get("url", "").split("/")[2] if "://" in res.get("url", "") else "Web Search",
                    "title": res.get("title", ""),
                    "content": res.get("content", ""),
                    "url": res.get("url", ""),
                    "image_url": img_url,
                    "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
            
            logger.info(f"[TavilyScraper] 成功取得 {len(results)} 筆真實新聞資料。")
            return results
            
        except Exception as e:
            logger.error(f"[TavilyScraper] 搜尋時發生錯誤: {e}，自動退回使用假資料。")
            return self.fallback_scraper.fetch_data(query, limit)

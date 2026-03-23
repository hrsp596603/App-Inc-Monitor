from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """
    資料搜集器基底類別 (Abstract Base Class)
    """
    
    @abstractmethod
    def fetch_data(self, query: str = "Apple", limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜集與查詢字串 (例如 "Apple Inc") 相關的新聞或社群內容
        回傳格式建議為:
        [
            {
                "id": "123",
                "source": "news_site_a",
                "title": "Apple releases new iPhone",
                "content": "...",
                "url": "https://...",
                "published_at": "2026-03-18T10:00:00Z"
            },
            ...
        ]
        """
        raise NotImplementedError

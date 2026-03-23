import os
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)

class NotificationManager:
    """
    通知總管，負責派送重要訊息到設定的頻道 (Line, Telegram)
    """
    def __init__(self):
        self.line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    def filter_and_notify(self, analyzed_items: List[Dict]):
        """
        過濾並發送通知，改作單一彙整推播報表
        """
        positive_items = []
        negative_items = []
        neutral_items = []
        
        for item in analyzed_items:
            sentiment = item.get("sentiment", "Neutral")
            if sentiment == "Positive":
                positive_items.append(item)
            elif sentiment == "Negative":
                negative_items.append(item)
            else:
                neutral_items.append(item)
                
        total_filtered = len(positive_items) + len(negative_items) + len(neutral_items)
        if total_filtered == 0:
            logger.info("無任何新聞資料，不觸發推播。")
            return
            
        # 組裝彙整訊息
        message = f"📊 [AppleInc 輿情日報彙整]\n"
        message += f"總計篩選重點新聞: {total_filtered} 篇\n"
        message += f"(🟢 正面: {len(positive_items)} 篇 / 🔴 負面: {len(negative_items)} 篇 / ⚪ 中立: {len(neutral_items)} 篇)\n\n"
        message += "【重點摘要整理】\n=================\n"
        
        items_to_notify = positive_items + negative_items + neutral_items
        for idx, item in enumerate(items_to_notify, 1):
            message += f"{idx}. {self._format_single_item(item)}\n\n"
            
        logger.info(f"觸發單一彙整推播，共涵蓋 {total_filtered} 篇文章")
        self._send_line(message)
        self._send_telegram(message)
                
    def _format_single_item(self, item: Dict) -> str:
        sentiment = item.get("sentiment", "Neutral")
        if sentiment == "Negative":
            emoji = "🔴"
        elif sentiment == "Positive":
            emoji = "🟢"
        else:
            emoji = "⚪"
            
        title = item.get("title_zh") or item.get("title", "無標題")
        content = item.get("content_zh") or item.get("content", "無內文")
        
        if len(content) > 60:
            content = content[:60] + "..."
        
        return f"{emoji} 標題: {title}\n" \
               f"   摘要: {content}\n" \
               f"   網址: {item.get('url', '')}"

    def _send_line(self, message: str):
        line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        line_user_id = os.getenv("LINE_USER_ID")
        
        if not line_token or not line_user_id:
            logger.debug(f"[Mock Line] 訊息已推播 (未設定 Token): \n{message}")
            return
            
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {line_token}"
        }
        payload = {
            "to": line_user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Line 推播發送成功")
            else:
                logger.error(f"❌ Line 推播失敗: API 回應 {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Line 發送發生例外錯誤: {e}")
        
    def _send_telegram(self, message: str):
        if not self.telegram_token or not self.telegram_chat_id:
            logger.debug(f"[Mock Telegram] 訊息已推播: \n{message}")
            return
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "disable_web_page_preview": False
        }
        
        try:
            import requests
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram 推播發送成功")
            else:
                logger.error(f"❌ Telegram 推播失敗: API 回應 {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Telegram 發送發生例外錯誤: {e}")

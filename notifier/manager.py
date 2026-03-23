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
        過濾並發送通知
        (目前實作邏輯: 發送「負面 Negative」 或「重大正向 Positive」的新聞)
        """
        for item in analyzed_items:
            sentiment = item.get("sentiment", "Neutral")
            
            # 定義推播規則：只推播非中立的新聞
            if sentiment in ["Negative", "Positive"]:
                message = self._format_message(item)
                logger.info(f"觸發推播 ({sentiment}): {item['title']}")
                
                self._send_line(message)
                self._send_telegram(message)
                
    def _format_message(self, item: Dict) -> str:
        emoji = "🔴" if item.get("sentiment") == "Negative" else "🟢"
        return f"{emoji} [AppleInc 監測通知]\n\n" \
               f"標題: {item['title']}\n" \
               f"情緒: {item.get('sentiment')}\n" \
               f"內容: {item['content']}\n" \
               f"連結: {item['url']}\n" \
               f"來源: {item['source']}"

    def _send_line(self, message: str):
        if not self.line_token:
            logger.debug(f"[Mock Line] 訊息已推播: \n{message}")
            return
        logger.info("TODO: 實作 Line Messaging API 串接")
        
    def _send_telegram(self, message: str):
        if not self.telegram_token or not self.telegram_chat_id:
            logger.debug(f"[Mock Telegram] 訊息已推播: \n{message}")
            return
        logger.info("TODO: 實作 Telegram Bot API 串接")

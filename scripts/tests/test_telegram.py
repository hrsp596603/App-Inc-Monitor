import os
from dotenv import load_dotenv
from notifier.manager import NotificationManager

# 載入 .env 變數
load_dotenv()

def test():
    manager = NotificationManager()
    
    # 檢查有沒有設定
    if not manager.telegram_token or manager.telegram_token == "your_bot_token":
        print("❌ 錯誤：尚未設定有效的 TELEGRAM_BOT_TOKEN")
        print("請確認您有在 .env 檔案中填寫並「儲存」檔案。")
        return
        
    if not manager.telegram_chat_id or manager.telegram_chat_id == "your_chat_id":
        print("❌ 錯誤：尚未設定有效的 TELEGRAM_CHAT_ID")
        print("請確認您有在 .env 檔案中填寫並「儲存」檔案。")
        return

    print("✅ 成功讀取 Token 與 ID！正在發送測試推播...")
    
    # 手動建立一筆假通知來測試
    mock_item = {
        "title": "🎉 Telegram 測試推播成功！",
        "content": "如果您在手機上收到這則訊息，代表您的 BotToken 與 ChatID 皆已設定正確，未來系統有新新聞都會自動傳送到這裡。",
        "sentiment": "Positive",
        "url": "https://example.com/success",
        "source": "AppleInc Monitor System"
    }
    
    message = manager._format_message(mock_item)
    manager._send_telegram(message)
    print("🚀 測試程式執行完畢！如果在手機上有收到訊息就代表大功告成了。")

if __name__ == "__main__":
    test()

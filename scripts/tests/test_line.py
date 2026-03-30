import os
from dotenv import load_dotenv
from notifier.manager import NotificationManager

# 載入 .env 變數
load_dotenv()

def test_line():
    manager = NotificationManager()
    
    line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_uid = os.getenv("LINE_USER_ID")
    
    # 檢查有沒有設定
    if not line_token or line_token == "your_channel_access_token":
        print("❌ 錯誤：尚未設定有效的 LINE_CHANNEL_ACCESS_TOKEN")
        return
        
    if not line_uid or line_uid == "your_user_id_for_push_notification":
        print("❌ 錯誤：尚未設定有效的 LINE_USER_ID")
        return

    print("✅ 成功讀取 Line 設定！正在發送測試推播...")
    
    message = "🎉 Line 測試推播成功！\n\n如果您在手機上收到這則訊息，代表您的 Line Token 與 User ID 皆已設定正確，未來系統有新新聞都會自動傳送到這裡。"
    
    manager._send_line(message)
    print("🚀 測試程式執行完畢！")

if __name__ == "__main__":
    test_line()

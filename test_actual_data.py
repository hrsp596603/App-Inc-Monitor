import json
import os
from dotenv import load_dotenv
from notifier.manager import NotificationManager

load_dotenv()

def send_existing_report():
    report_path = os.path.join(os.path.dirname(__file__), "web", "static", "latest_report.json")
    if not os.path.exists(report_path):
        print("❌ 找不到最新的報告檔案 latest_report.json。")
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        analyzed_items = json.load(f)
        
    print(f"✅ 成功讀取到 {len(analyzed_items)} 篇已儲存的文章報告。")
    print("開始執行真實文章的過濾與 Telegram 推播測試...")
    
    notifier = NotificationManager()
    notifier.filter_and_notify(analyzed_items)
    
    print("🚀 真實文章推播測試已送出！請檢查手機（可能有多則被判定為非中立的真實新聞）。")

if __name__ == "__main__":
    send_existing_report()

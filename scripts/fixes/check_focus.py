import json
import os
from dotenv import load_dotenv

load_dotenv()

from analyzer.sentiment import SentimentAnalyzer

def test_focus():
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    report_file = os.path.join(output_dir, "latest_report.json")
    
    if not os.path.exists(report_file):
        print("找不到 report 檔案")
        return
        
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    analyzer = SentimentAnalyzer()
    
    print("正在請求 Gemini API 生成新聞焦點...")
    focus_data = analyzer.generate_focus_summary(data)
    
    if "Apple 在產品線與核心技術發展上持續展現韌性" in focus_data["positive_focus"]:
        print("🔴 測試結果：目前依然受到 Gemini API 流量限制 (Rate Limit)。")
        print("系統已啟用優雅降級保護機制，目前回傳預設的焦點訊息以維持畫面版面。")
    elif "發生錯誤" in focus_data["positive_focus"]:
        print("🔴 遇到其他未預期錯誤，未能生成焦點。")
    else:
        print("✅ 測試結果：API 額度已恢復，成功生成全新，動態的新聞焦點！")
        print(json.dumps(focus_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_focus()

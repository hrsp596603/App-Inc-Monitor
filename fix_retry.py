import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

from analyzer.sentiment import SentimentAnalyzer
from utils.build_html import build_static_dashboard

def fix_summary():
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    report_file = os.path.join(output_dir, "latest_report.json")
    focus_file = os.path.join(output_dir, "focus_report.json")
    
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    analyzer = SentimentAnalyzer()
    
    for attempt in range(5):
        print(f"嘗試生成焦點 (Attempt {attempt+1})...")
        focus_data = analyzer.generate_focus_summary(data)
        
        if "發生錯誤" not in focus_data["positive_focus"] and "失敗" not in focus_data["positive_focus"]:
            with open(focus_file, "w", encoding="utf-8") as f:
                json.dump(focus_data, f, ensure_ascii=False, indent=2)
            print("已成功儲存焦點資訊")
            build_static_dashboard()
            print("✅ 網頁編譯與修復完成！")
            return
        else:
            print("依然遇到 Rate Limit，暫停 20 秒...")
            time.sleep(20)

if __name__ == "__main__":
    fix_summary()

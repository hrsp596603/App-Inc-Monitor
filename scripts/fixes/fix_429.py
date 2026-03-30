import os
import json
from dotenv import load_dotenv

load_dotenv()

from analyzer.sentiment import SentimentAnalyzer
from utils.build_html import build_static_dashboard

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def fix_summary():
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    report_file = os.path.join(output_dir, "latest_report.json")
    focus_file = os.path.join(output_dir, "focus_report.json")
    
    if not os.path.exists(report_file):
        print("FileNotFound:", report_file)
        return
        
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    analyzer = SentimentAnalyzer()
    
    # 強制改用 OpenAI 以避開 Gemini 的暫時性 Rate Limit 限制
    if OpenAI and os.getenv("OPENAI_API_KEY"):
        print("強制切換至 OpenAI API (以避開 Gemini Rate Limit)...")
        analyzer.provider = "openai"
    elif analyzer.provider == "gemini":
        print("使用 Gemini 嘗試重新生成 (請確認 Rate Limit 已恢復)...")
    
    print("重新呼叫生成焦點...")
    focus_data = analyzer.generate_focus_summary(data)
    
    if "發生錯誤" not in focus_data["positive_focus"] and "失敗" not in focus_data["positive_focus"]:
        with open(focus_file, "w", encoding="utf-8") as f:
            json.dump(focus_data, f, ensure_ascii=False, indent=2)
        print("已成功儲存焦點資訊")
        print("開始重新編譯靜態網頁...")
        build_static_dashboard()
        print("✅ 修復完成！")
    else:
        print("依然失敗:", focus_data)

if __name__ == "__main__":
    fix_summary()

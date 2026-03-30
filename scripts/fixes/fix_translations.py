import os
import json
import re
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

from analyzer.sentiment import SentimentAnalyzer
from utils.build_html import build_static_dashboard

def contains_mostly_english(text):
    # 簡單判斷：如果英文字母比例過高，或者沒有中文字，就代表沒翻譯好
    if not text:
        return False
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 只要有足夠中文字就算是有翻譯 (部分保留英文專有名詞是正常的)
    if chinese_chars < 5 and len(text) > 20: 
        return True
    return False

def fix_missing_translations():
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    report_file = os.path.join(output_dir, "latest_report.json")
    
    if not os.path.exists(report_file):
        print("FileNotFound:", report_file)
        return
        
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    analyzer = SentimentAnalyzer()
    
    # 強制切換為 OpenAI 以避開 Gemini 密集的測試 Rate Limit
    if os.getenv("OPENAI_API_KEY"):
        analyzer.provider = "openai"
    
    updated = False
    for i, item in enumerate(data):
        title_zh = item.get("title_zh", "")
        content_zh = item.get("content_zh", "")
        
        # 檢查是否沒有翻譯 (等於原文) 或沒有足夠中文字
        if title_zh == item["title"] or contains_mostly_english(title_zh) or contains_mostly_english(content_zh):
            print(f"[{i}] 重新翻譯文章: {item['title']}")
            res = analyzer._call_llm(item["title"], item["content"])
            item["sentiment"] = res.get("sentiment", item.get("sentiment", "Neutral"))
            item["title_zh"] = res.get("title_zh", title_zh)
            item["content_zh"] = res.get("content_zh", content_zh)
            updated = True
            
    if updated:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("已更新 latest_report.json，準備重新生成靜態網頁...")
        build_static_dashboard()
        print("✅ 翻譯修復完成！")
    else:
        print("🎉 所有文章皆已翻譯，無需修復。")

if __name__ == "__main__":
    fix_missing_translations()

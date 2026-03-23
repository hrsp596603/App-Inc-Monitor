import os
from dotenv import load_dotenv

from scraper.tavily_scraper import TavilyScraper
from analyzer.sentiment import SentimentAnalyzer
from notifier.manager import NotificationManager
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("MainPipeline")

def run_pipeline():
    logger.info("🚀 啟動 AppleInc 輿情監控系統 Pipeline")
    
    # 1. 搜集資料
    logger.info("[1] 正在搜集資料...")
    scraper = TavilyScraper()
    raw_data = scraper.fetch_data(query="Apple Inc. latest tech news", limit=5)
    
    # 2. 進行 LLM 分析
    logger.info("[2] 正在進行內容與情緒分析...")
    analyzer = SentimentAnalyzer()
    analyzed_data = analyzer.analyze(raw_data)
    
    # 3. 準備網頁報告 (由其他排程或指令啟動 Web Server)
    logger.info("[3] 彙整報告 (儲存以供 Web 讀取)...")
    # 將結果輸出到一個 JSON 讓網頁端能讀取
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    os.makedirs(output_dir, exist_ok=True)
    import json
    with open(os.path.join(output_dir, "latest_report.json"), "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
    logger.info("報告已存至 web/static/latest_report.json")
    
    # 4. 推播通知
    logger.info("[4] 檢查是否需推播通知...")
    notifier = NotificationManager()
    notifier.filter_and_notify(analyzed_data)

if __name__ == "__main__":
    run_pipeline()
    logger.info("✅ Pipeline 單次執行完成。")

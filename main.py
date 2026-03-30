import os
from dotenv import load_dotenv

from scraper.tavily_scraper import TavilyScraper
from scraper.duckduckgo_scraper import DuckDuckGoScraper
from analyzer.sentiment import SentimentAnalyzer
from notifier.manager import NotificationManager
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("MainPipeline")

def run_pipeline():
    logger.info("🚀 啟動 AppleInc 輿情監控系統 Pipeline")
    
    # 1. 搜集資料
    logger.info("[1] 正在搜集資料...")
    query = "Apple Inc. latest tech news"
    
    tavily_scraper = TavilyScraper()
    tavily_data = tavily_scraper.fetch_data(query=query, limit=5)
    
    ddg_scraper = DuckDuckGoScraper()
    ddg_data = ddg_scraper.fetch_data(query=query, limit=5)
    
    raw_data = tavily_data + ddg_data
    logger.info(f"總共收集到 {len(raw_data)} 筆新聞資料。")
    
    # 2. 進行 LLM 分析
    logger.info("[2] 正在進行內容與情緒分析...")
    analyzer = SentimentAnalyzer()
    analyzed_data = analyzer.analyze(raw_data)
    
    # 3. 準備網頁報告 (由其他排程或指令啟動 Web Server)
    logger.info("[3] 彙整報告 (儲存以供 Web 讀取)...")
    
    logger.info("正在生成新聞總結焦點...")
    focus_data = analyzer.generate_focus_summary(analyzed_data)

    # 將結果輸出到一個 JSON 讓網頁端能讀取
    output_dir = os.path.join(os.path.dirname(__file__), "web", "static")
    os.makedirs(output_dir, exist_ok=True)
    import json
    with open(os.path.join(output_dir, "latest_report.json"), "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(output_dir, "focus_report.json"), "w", encoding="utf-8") as f:
        json.dump(focus_data, f, ensure_ascii=False, indent=2)
        
    logger.info("報告已存至 web/static/latest_report.json 與 focus_report.json")
    
    # 4. 推播通知
    logger.info("[4] 檢查是否需推播通知...")
    notifier = NotificationManager()
    notifier.filter_and_notify(analyzed_data)

    # 5. 備份到 GitHub (新增)
    logger.info("[5] 備份本日報告至 GitHub 與本機特定資料夾...")
    from utils.github_backup import backup_to_github
    import datetime
    import shutil
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    history_dir = os.path.join(os.path.dirname(__file__), "docs", "history")
    os.makedirs(history_dir, exist_ok=True)
    
    # 使用者指定的額外本機備份目錄
    extra_backup_dir = "/Users/hongpeiyuan/Documents/Apple Inc. Monitor"
    os.makedirs(extra_backup_dir, exist_ok=True)
    
    source_file = os.path.join(output_dir, "latest_report.json")
    dest_file = os.path.join(history_dir, f"report_{date_str}.json")
    extra_dest_file = os.path.join(extra_backup_dir, f"report_{date_str}.json")
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, dest_file)
        shutil.copy2(source_file, extra_dest_file)  # 額外備份
        logger.info(f"已額外複製備份至: {extra_dest_file}")
        
        # 6. 生成 GitHub Pages 靜態儀表板 (新增)
        logger.info("[6] 正在轉譯靜態網頁準備部署 GitHub Pages...")
        try:
            from utils.build_html import build_static_dashboard
            build_static_dashboard()
        except Exception as e:
            logger.error(f"❌ 靜態網頁轉譯發生錯誤: {e}")
            
        backup_to_github(date_str)
    else:
        logger.warning(f"找不到最新報告 {source_file}，無法備份。")

if __name__ == "__main__":
    run_pipeline()
    logger.info("✅ Pipeline 單次執行完成。")

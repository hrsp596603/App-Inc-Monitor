import os
import sys
import time

try:
    import schedule
except ImportError:
    schedule = None

# 將上層目錄加入 path，方便引入 main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline
from utils.logger import setup_logger

logger = setup_logger(__name__)

def job():
    logger.info("🕒 排程觸發：開始執行 AppleInc Monitor 管線")
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"❌ 管線執行失敗: {e}")

def start_scheduler():
    if not schedule:
        logger.error("未安裝 schedule 套件，請執行 pip install -r requirements.txt")
        return
        
    interval_days = int(os.getenv("SCHEDULE_INTERVAL_DAYS", 1))
    
    # 預設排程 (例如每 X 天執行)
    if interval_days == 1:
        schedule.every().day.at("16:00").do(job)
    else:
        schedule.every(interval_days).days.do(job)
    
    logger.info(f"📅 排程已啟動，設定為每 {interval_days} 天（或每天16:00）執行一次。")
    logger.info("🕒 即將執行首次背景任務...")
    job() # 啟動時先跑一次
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()

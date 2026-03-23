import os
import subprocess
from utils.logger import setup_logger

logger = setup_logger(__name__)

def backup_to_github(date_str: str):
    """
    將產生的歷史 JSON 報告自動推送到 GitHub
    """
    logger.info(f"開始將 {date_str} 報告備份至 GitHub...")
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 將新的報告存檔與根目錄的生成的靜態網頁加入 git 追蹤
        subprocess.run(["git", "add", "index.html", "style.css", "docs/history/"], cwd=project_dir, check=True, capture_output=True)
        
        # 檢查是否有檔案變更，避免 git commit 報錯 (無更改時會 return 非 0 exit code)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True)
        if status.stdout.strip():
            msg = f"Auto-backup daily report for {date_str}"
            subprocess.run(["git", "commit", "-m", msg], cwd=project_dir, check=True, capture_output=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir, check=True, capture_output=True)
            logger.info("✅ 成功將本日報告推送到 GitHub Repository！")
        else:
            logger.info("ℹ️ GitHub 備份：沒有偵測到新的變更 (可能本日檔案內容與昨日相同)。")
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"❌ GitHub 備份失敗 (git 命令回傳錯誤): {error_msg}")
    except Exception as e:
        logger.error(f"❌ GitHub 備份發生例外錯誤: {e}")

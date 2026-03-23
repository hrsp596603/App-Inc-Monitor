import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)

def build_static_dashboard():
    """
    將 web/templates/index.html 轉譯為靜態 HTML (docs/index.html)
    供 GitHub Pages 讀取
    """
    logger.info("開始生成 GitHub Pages 靜態儀表板 (docs/index.html)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    static_dir = os.path.join(base_dir, "web", "static")
    templates_dir = os.path.join(base_dir, "web", "templates")
    
    os.makedirs(docs_dir, exist_ok=True)
    
    # 讀取資料
    report_path = os.path.join(static_dir, "latest_report.json")
    reports = []
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            reports = json.load(f)
            
    # 計算情緒統計
    stats = {"positive": 0, "negative": 0, "neutral": 0, "total": len(reports)}
    for r in reports:
        s = r.get("sentiment", "Neutral").lower()
        if s == "positive":
            stats["positive"] += 1
        elif s == "negative":
            stats["negative"] += 1
        else:
            stats["neutral"] += 1

    # 初始化 Jinja2 環境
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("index.html")
    
    # 渲染為純字串，只需傳入 reports 和 stats。
    html_content = template.render(reports=reports, stats=stats)
    
    # 將 /static/style.css 替換為相對路徑 ./style.css，使得能在 GitHub Pages 子路徑運作
    html_content = html_content.replace('href="/static/style.css"', 'href="./style.css"')
    
    # 儲存靜態檔案到根目錄 (為配合 GitHub Pages /root 設定)
    index_path = os.path.join(base_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # 同步拷貝 CSS 樣式表到根目錄
    src_css = os.path.join(static_dir, "style.css")
    dest_css = os.path.join(base_dir, "style.css")
    if os.path.exists(src_css):
        shutil.copy2(src_css, dest_css)
        
    logger.info("✅ 靜態網頁與樣式表已成功寫入專案根目錄。")

if __name__ == "__main__":
    build_static_dashboard()

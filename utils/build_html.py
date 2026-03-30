import os
import json
import shutil
import glob
import datetime
from jinja2 import Environment, FileSystemLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)

def parse_date_from_filename(filename):
    basename = os.path.basename(filename)
    date_str = basename.replace("report_", "").replace(".json", "")
    return date_str.replace("-", "/")

def get_stats(reports):
    stats = {"positive": 0, "negative": 0, "neutral": 0, "total": len(reports)}
    for r in reports:
        s = r.get("sentiment", "Neutral").lower()
        if s == "positive":
            stats["positive"] += 1
        elif s == "negative":
            stats["negative"] += 1
        else:
            stats["neutral"] += 1
    return stats

def render_page(template, reports, focus_data, current_date, history_files, selected_url, dest_path, css_path="./style.css"):
    stats = get_stats(reports)
    html_content = template.render(
        reports=reports, 
        stats=stats, 
        focus_data=focus_data, 
        current_date=current_date,
        history_files=history_files,
        selected_url=selected_url
    )
    html_content = html_content.replace('href="/static/style.css"', f'href="{css_path}"')
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def build_static_dashboard():
    logger.info("開始生成 GitHub Pages 靜態儀表板 (包含歷史頁面)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "web", "static")
    templates_dir = os.path.join(base_dir, "web", "templates")
    history_dir = os.path.join(base_dir, "docs", "history")
    archive_dir = os.path.join(base_dir, "archive")
    
    os.makedirs(archive_dir, exist_ok=True)
    
    # 解析出基礎清單 (不含路徑的 metadata)
    base_history = []
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_display = today_str.replace("-", "/")
    
    base_history.append({
        "label": f"{today_display} (最新)",
        "type": "latest",
        "raw_date": today_str + "9" 
    })
    
    if os.path.exists(history_dir):
        for f in glob.glob(os.path.join(history_dir, "report_*.json")):
            date_display = parse_date_from_filename(f)
            raw_date = os.path.basename(f).replace("report_", "").replace(".json", "")
            if raw_date != today_str: 
                base_history.append({
                    "label": date_display,
                    "type": "archive",
                    "filename": f"{raw_date}.html",
                    "raw_date": raw_date,
                    "file_path": f
                })
                
    base_history = sorted(base_history, key=lambda x: x["raw_date"], reverse=True)
    
    # 產生根目錄用的路由選單
    root_nav = []
    for item in base_history:
        url = "index.html" if item["type"] == "latest" else f"archive/{item['filename']}"
        root_nav.append({"label": item["label"], "url": url})
        
    # 產生 archive 目錄內用的路由選單
    archive_nav = []
    for item in base_history:
        url = "../index.html" if item["type"] == "latest" else item["filename"]
        archive_nav.append({"label": item["label"], "url": url})
    
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("index.html")

    # 1. 生成最新首頁 index.html
    latest_report_path = os.path.join(static_dir, "latest_report.json")
    latest_focus_path = os.path.join(static_dir, "focus_report.json")
    reports = []
    focus_data = None
    
    if os.path.exists(latest_report_path):
        with open(latest_report_path, "r", encoding="utf-8") as f:
            reports = json.load(f)
    if os.path.exists(latest_focus_path):
        with open(latest_focus_path, "r", encoding="utf-8") as f:
            focus_data = json.load(f)
            
    render_page(template, reports, focus_data, today_display, root_nav, "index.html", os.path.join(base_dir, "index.html"), css_path="./style.css")
    logger.info("已生成最新報告: index.html")
    
    # 2. 生成所有歷史頁面 (存入 archive/)
    for item in base_history:
        if item["type"] == "archive" and "file_path" in item:
            with open(item["file_path"], "r", encoding="utf-8") as f:
                hist_reports = json.load(f)
            
            dest_html = os.path.join(archive_dir, item["filename"])
            # url for this page in the archive menu is just its filename
            render_page(template, hist_reports, None, item["label"], archive_nav, item["filename"], dest_html, css_path="../style.css")
            logger.info(f"已生成歷史報告: archive/{item['filename']}")
            
    # 同步拷貝 CSS 樣式表
    src_css = os.path.join(static_dir, "style.css")
    dest_css = os.path.join(base_dir, "style.css")
    if os.path.exists(src_css):
        shutil.copy2(src_css, dest_css)
        
    logger.info("✅ 靜態網頁切換多頁面與樣式表已成功寫入專案根目錄與 archive/。")

if __name__ == "__main__":
    build_static_dashboard()

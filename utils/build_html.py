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

def render_page(template, reports, focus_data, current_date, history_files, selected_url, dest_path):
    stats = get_stats(reports)
    html_content = template.render(
        reports=reports, 
        stats=stats, 
        focus_data=focus_data, 
        current_date=current_date,
        history_files=history_files,
        selected_url=selected_url
    )
    html_content = html_content.replace('href="/static/style.css"', 'href="./style.css"')
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def build_static_dashboard():
    logger.info("開始生成 GitHub Pages 靜態儀表板 (包含歷史頁面)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "web", "static")
    templates_dir = os.path.join(base_dir, "web", "templates")
    history_dir = os.path.join(base_dir, "docs", "history")
    
    # 準備歷史清單
    history_files = []
    
    # 最新的一筆做為預設 index.html 選項 (使用今日日期)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_display = today_str.replace("-", "/")
    
    history_files.append({
        "label": f"{today_display} (最新)",
        "url": "index.html",
        "raw_date": today_str + "9" # 確保最新一定排在最上方
    })
    
    # 掃描 history 裡的所有歷史備份
    if os.path.exists(history_dir):
        for f in glob.glob(os.path.join(history_dir, "report_*.json")):
            date_display = parse_date_from_filename(f)
            raw_date = os.path.basename(f).replace("report_", "").replace(".json", "")
            if raw_date != today_str: # 避免如果當天已經備份過，會出現兩個當天項目
                history_files.append({
                    "label": date_display,
                    "url": f"{raw_date}.html",
                    "raw_date": raw_date,
                    "file_path": f
                })
                
    # 依日期遞減排序
    history_files = sorted(history_files, key=lambda x: x["raw_date"], reverse=True)
    
    # 初始化 Jinja2
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
            
    render_page(template, reports, focus_data, today_display, history_files, "index.html", os.path.join(base_dir, "index.html"))
    logger.info("已生成最新報告: index.html")
    
    # 2. 生成所有歷史頁面
    for item in history_files:
        if "file_path" in item:
            with open(item["file_path"], "r", encoding="utf-8") as f:
                hist_reports = json.load(f)
            
            dest_html = os.path.join(base_dir, item["url"])
            render_page(template, hist_reports, None, item["label"], history_files, item["url"], dest_html)
            logger.info(f"已生成歷史報告: {item['url']}")
            
    # 同步拷貝 CSS 樣式表
    src_css = os.path.join(static_dir, "style.css")
    dest_css = os.path.join(base_dir, "style.css")
    if os.path.exists(src_css):
        shutil.copy2(src_css, dest_css)
        
    logger.info("✅ 靜態網頁切換多頁面與樣式表已成功寫入專案根目錄。")

if __name__ == "__main__":
    build_static_dashboard()

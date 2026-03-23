import os
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# 初始化 FastAPI app
app = FastAPI(title="AppleInc Monitor")

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 設定模板引擎
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/")
async def read_root(request: Request):
    """
    讀取最新報告並渲染首頁，同時計算情緒統計
    """
    report_path = os.path.join(STATIC_DIR, "latest_report.json")
    reports = []
    
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reports = json.load(f)
        except Exception as e:
            print(f"無法讀取報告檔案: {e}")

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

    import datetime
    current_date = datetime.datetime.now().strftime("%Y/%m/%d")

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "reports": reports,
        "stats": stats,
        "current_date": current_date
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WEB_PORT", 8000))
    host = os.getenv("WEB_HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)

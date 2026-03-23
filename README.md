# AppleInc 輿情與新聞監控系統 (AppleInc Monitor)

> 自動化搜集 Apple Inc. 相關新聞，利用 LLM 判斷情緒，並在網頁顯示報表或推播通知。

## 系統架構

依據 `RULES.md` 的規劃，系統包含五個核心模組：
1. **Scraper (搜集)**：從社群及新聞網站抓取相關文章。
2. **Analyzer (分析)**：透過 LLM（例如 OpenAI API）分析新聞的情緒。
3. **Web (報告)**：使用 FastAPI + Jinja2 顯示視覺化新聞清單。
4. **Notifier (通知)**：高風險新聞透過 Line 或 Telegram 推播。
5. **Scheduler (排程)**：排程每日或定時自動化擷取並分析資料。

## 快速開始

1. 安裝套件：`pip install -r requirements.txt`
2. 複製環境變數設定檔：`cp .env.example .env` 並填入對應的 API Keys。
3. 手動測試管線一次：`python main.py`


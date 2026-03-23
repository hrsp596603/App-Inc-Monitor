# AppleInc 輿情監控系統實作計畫

## 工作目標 (Goal Description)
依據使用者的白板流程圖規劃，建構一個全自動化的「AppleInc 輿情監控系統」。
系統旨在定時搜集 Apple 相關的新聞與社群訊息，利用 LLM (大型語言模型) 判斷情緒（正、負、中立），最後將分析報告集中呈現於網頁，並針對重要資訊透過 Line 或 Telegram 發送推播通知。

## 待確認事項 (User Review Required)
> [!IMPORTANT]
> 系統架構細節需與您確認：
> 1. **開發語言 / 框架偏好**：請問您偏好使用哪種語言進行後端與爬蟲開發？（例如 Python 非常適合資料爬取與 LLM 整合；網頁前後端可選擇 Node.js 或是 Python FastAPI/Flask）。
> 2. **LLM 供應商**：您預計使用哪一家的 LLM API？（如 OpenAI, Anthropic, 或在地部署開源模型）。
> 3. **資料來源**：社群平台與網路新聞是否已有指定的 API 來源或目標網站？

## 系統架構規劃 (Proposed Changes)

我們預計將系統拆分為以下模組並建立目錄架構：

### 核心定義
#### [NEW] `AppleInc/RULES.md`(file:///Users/hongpeiyuan/Desktop/Brian/Programming%20Stuff/antiproject/AppleInc/RULES.md)
包含專案的核心工作流、開發規範與系統限制。

### 資料搜集與分析層
#### [NEW] `AppleInc/scraper/`
- 負責搜集社群平台、網路新聞與公開訊息的模組。
- 包含不同的搜集器子模組 (例如 `news_scraper`, `social_scraper`)。

#### [NEW] `AppleInc/analyzer/`
- LLM 分析模組，負責組合 Prompt 並呼叫 LLM 進行文本情緒分類（正、負、中/沒）。

### 報告與網頁層
#### [NEW] `AppleInc/web/`
- 提供視覺化呈現分析結果的網頁儀表板 (Dashboard)。
- 包含後端 API 伺服器與前端 UI。

### 通知與排程層
#### [NEW] `AppleInc/notifier/`
- 整合 Line Messaging API 與 Telegram Bot API，處理訊息推播邏輯。

#### [NEW] `AppleInc/scheduler/`
- 定時排程控制器，負責定時（如每日）觸發整體管線 (Pipeline)。

## 驗證計畫 (Verification Plan)

### 自動化測試 (Automated Tests)
- **搜集模組測試**：針對固定的測試目標網站或 Mock API 進行擷取測試，確認解析邏輯正確。
- **LLM 模組測試**：以預選的標準語句（包含明顯的正向與負向語句）測試 LLM 分類功能，驗證輸出是否為預期的 JSON 格式或列舉值。
- **通知模組測試**：Mock 外部通訊 API (Line/Telegram) 的呼叫，確認傳入不同訊息級別時，函式的觸發與 Payload 組合是否正確。

### 手動驗證 (Manual Verification)
- 準備一組測試環境用 API Key。
- 手動觸發一次 Pipeline 入口腳本，驗證：
  1.終端機能正常印出搜集與分析進度。
  2.網頁端有成功渲染出最新的假資料。
  3.開發者的 Line/Telegram 測試群組有收到預期的推播通知。

import os
import json
from typing import List, Dict, Any
from utils.logger import setup_logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None

logger = setup_logger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.provider = None
        self.client = None
        self.gemini_client = None
        self.openai_client = None
        
        # 檢查 Gemini API key
        is_valid_gemini = (
            self.gemini_api_key is not None
            and isinstance(self.gemini_api_key, str)
            and genai is not None
            and not self.gemini_api_key.startswith("your_")
            and len(self.gemini_api_key) > 5
        )
        
        # 檢查 OpenAI API key
        is_valid_openai = (
            self.openai_api_key is not None
            and isinstance(self.openai_api_key, str)
            and OpenAI is not None
            and not self.openai_api_key.startswith("your_")
            and len(self.openai_api_key) > 10
        )
        
        # 優先使用 Gemini，如果沒有則嘗試 OpenAI
        if is_valid_gemini:
            # Type checker might complain about strip being called on None, but we checked is_valid_gemini
            api_key = str(self.gemini_api_key).strip()
            self.gemini_client = genai.Client(api_key=api_key)
            self.provider = "gemini"
            logger.info("已設定使用 Gemini API 進行情緒分析。")
        elif is_valid_openai:
            api_key = str(self.openai_api_key).strip()
            self.openai_client = OpenAI(api_key=api_key)
            self.provider = "openai"
            logger.info("已設定使用 OpenAI API 進行情緒分析。")
        else:
            logger.warning("未設定有效的 GEMINI_API_KEY 或 OPENAI_API_KEY，將採用 Mock 分析模式。")
            
    def analyze(self, items: List[Dict]) -> List[Dict]:
        """
        將收集到的資料送入 LLM 確認情緒分類，同時翻譯成繁體中文。
        """
        results = []
        
        if not self.provider:
            return self._mock_analyze(items)
            
        for item in items:
            import time
            time.sleep(4)  # 避免 Gemini Free Tier Rate Limit (15 RPM)
            analysis = self._call_llm(item["title"], item["content"])
            enriched_item = item.copy()
            enriched_item["sentiment"] = analysis.get("sentiment", "Neutral")
            enriched_item["title_zh"] = analysis.get("title_zh", item["title"])
            enriched_item["content_zh"] = analysis.get("content_zh", item["content"])
            results.append(enriched_item)
            
        return results

    def _call_llm(self, title: str, content: str) -> Dict[str, str]:
        prompt = f"""請針對以下 Apple Inc. 相關的英文新聞，完成兩件事：
1. 情緒分析：分類為 'Positive'、'Negative' 或 'Neutral'。
2. 翻譯：務必將標題和內容「強制且完整地翻譯為繁體中文 (Traditional Chinese)」。不可保留英文原文（專有名詞如 Apple 等除外）。

這非常重要，請確保「title_zh」和「content_zh」兩者皆為繁體中文！

請以純 JSON 格式回覆(絕對不要加 markdown code block)：
{{"sentiment": "...", "title_zh": "...", "content_zh": "..."}}

標題: {title}
內容: {content}
"""
        raw = ""
        try:
            if self.provider == "gemini" and self.gemini_client and genai_types:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.0,
                    ),
                )
                raw = response.text
                if raw is None:
                    raw = ""
                raw = raw.strip()
                import re
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    raw = match.group(0)
                
            elif self.provider == "openai" and self.openai_client:
                response_openai = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful text sentiment analyzer and translator. Always respond in valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                raw_content = response_openai.choices[0].message.content
                if raw_content:
                    raw = raw_content.strip()
                    import re
                    match = re.search(r"\{.*\}", raw, re.DOTALL)
                    if match:
                        raw = match.group(0)

            # 嘗試解析 JSON
            result = json.loads(raw)
            return result
        except json.JSONDecodeError:
            logger.warning(f"LLM 回傳非 JSON 格式 ({self.provider}): {raw}")
            return {"sentiment": "Neutral", "title_zh": title, "content_zh": content}
        except Exception as e:
            logger.error(f"LLM 呼叫失敗 ({self.provider}): {e}")
            return {"sentiment": "Neutral", "title_zh": title, "content_zh": content}

    def _mock_analyze(self, items: List[Dict]) -> List[Dict]:
        """開發與測試用的模擬回傳（含假翻譯）"""
        mock_translations = {
            "Apple announces record-breaking Q4 earnings": {
                "title_zh": "Apple 公佈破紀錄的第四季營收",
                "content_zh": "Apple Inc. 報告了本季有史以來最高的營收，這得益於 iPhone 在全球的強勁銷售表現。"
            },
            "Apple's new product launch faces unexpected delays": {
                "title_zh": "Apple 新產品發表面臨意外延遲",
                "content_zh": "供應鏈限制迫使 Apple 將備受期待的 VR 頭戴式裝置延後數個月推出。"
            },
            "New Apple store opens in downtown Tokyo": {
                "title_zh": "Apple 新門市在東京市中心盛大開幕",
                "content_zh": "一間嶄新的零售店面以最新設計語言打造，剛剛在日本開門迎客。"
            }
        }
        
        results = []
        for item in items:
            enriched = item.copy()
            text = (item["title"] + " " + item["content"]).lower()
            if "record-breaking" in text or "strong" in text:
                enriched["sentiment"] = "Positive"
            elif "delay" in text or "constraint" in text:
                enriched["sentiment"] = "Negative"
            else:
                enriched["sentiment"] = "Neutral"
            
            translation = mock_translations.get(item["title"], {})
            enriched["title_zh"] = translation.get("title_zh", item["title"])
            enriched["content_zh"] = translation.get("content_zh", item["content"])
            results.append(enriched)
        return results

    def generate_focus_summary(self, items: List[Dict]) -> Dict[str, str]:
        """
        傳入所有已分析的文章，要求 LLM 統整出 正面、負面、中立 的核心焦點
        """
        if not self.provider:
            return {
                "positive_focus": "無顯著正面情報（開發模式模擬）。",
                "negative_focus": "無顯著負面情報（開發模式模擬）。",
                "neutral_focus": "無顯著中立情報（開發模式模擬）。"
            }
            
        # 準備內文給 LLM
        articles_text = ""
        for i, item in enumerate(items):
            s = item.get("sentiment", "Neutral")
            t = item.get("title_zh", item.get("title", ""))
            c = item.get("content_zh", item.get("content", ""))
            articles_text += f"[{i+1}] 情緒:{s} | 標題:{t} | 摘要:{c[:150]}\n"
            
        prompt = f"""請閱讀以下 Apple Inc. 相關的新聞列表，並分別總結出「正面焦點」、「負面焦點」與「中立焦點」。
如果某個面向完全沒有相關新聞（例如完全沒有正面新聞），請回覆「目前無顯著正面情報」。
每個焦點的總結大約 1 到 2 句話，務必精煉且直接切入重點。使用繁體中文回覆。

請務必以純 JSON 格式回覆(絕對不要加 markdown code block)：
{{"positive_focus": "...", "negative_focus": "...", "neutral_focus": "..."}}

新聞列表：
{articles_text}
"""
        raw = ""
        try:
            if self.provider == "gemini" and self.gemini_client and genai_types:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.0,
                    ),
                )
                raw = response.text
                if raw is None:
                    raw = ""
                raw = raw.strip()
                import re
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    raw = match.group(0)
                
            elif self.provider == "openai" and self.openai_client:
                response_openai = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful summarizer. Always respond in valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                raw_content = response_openai.choices[0].message.content
                if raw_content:
                    raw = raw_content.strip()
                    import re
                    match = re.search(r"\{.*\}", raw, re.DOTALL)
                    if match:
                        raw = match.group(0)

            result = json.loads(raw)
            return {
                "positive_focus": result.get("positive_focus", "分析失敗或無資料。"),
                "negative_focus": result.get("negative_focus", "分析失敗或無資料。"),
                "neutral_focus": result.get("neutral_focus", "分析失敗或無資料。"),
            }
        except Exception as e:
            logger.error(f"焦點總結生成失敗 ({self.provider}): {e}")
            return {
                "positive_focus": "生成焦點摘要時發生錯誤。",
                "negative_focus": "生成焦點摘要時發生錯誤。",
                "neutral_focus": "生成焦點摘要時發生錯誤。",
            }

import json
import os
from utils.build_html import build_static_dashboard

out_file = "web/static/latest_report.json"
with open(out_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if "iOS 26.4 adds more intelligence" in item["title"]:
        item["title_zh"] = "iOS 26.4 替符合條件的 Apple iPhone 增加更多智慧功能：更新教學"
        item["content_zh"] = "Apple 剛剛釋出 iOS 26.4 更新，為部分符合硬體條件的 iPhone 帶來深度人工智慧整合與多項智慧增強功能。"
        item["sentiment"] = "Positive"
        print("Patched 1")
    elif "Apple classifies two more iPhones as 'obsolete'" in item["title"]:
        item["title_zh"] = "Apple 將兩款 iPhone 正式列為「淘汰」產品：在此查看機型清單"
        item["content_zh"] = "依照 Apple 支援政策，又有兩款舊世代 iPhone 被正式歸類為停止硬體服務的淘汰產品清單中。"
        item["sentiment"] = "Neutral"
        print("Patched 2")

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Building HTML...")
build_static_dashboard()
print("Done.")

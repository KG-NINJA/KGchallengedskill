import os
import csv
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = os.getenv("GOOGLE_API_KEY")
CX_ID = os.getenv("GOOGLE_CX_ID")
KEYWORDS = ["KGNINJA", "KGNINJA AI", "FuwaCoco", "Psycho-Frame", "AIEO"]
LOG_FILE = "visibility_log.csv"
CHART_FILE = "visibility_chart.png"

def google_search(keyword):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": CX_ID, "q": keyword}
    res = requests.get(url, params=params)
    data = res.json()
    total = int(data.get("searchInformation", {}).get("totalResults", 0))
    items = data.get("items", [])
    top_results = [(i.get("title", ""), i.get("link", "")) for i in items[:3]]
    return total, top_results

def save_log(timestamp, keyword, total, top_results):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "keyword", "totalResults",
                             "top1_title", "top1_url", "top2_title", "top2_url", "top3_title", "top3_url"])
        row = [timestamp, keyword, total]
        for title, url in top_results:
            row += [title, url]
        while len(row) < 9:
            row.append("")
        writer.writerow(row)

def plot_visibility_chart():
    df = pd.read_csv(LOG_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    pivot_df = df.pivot(index="timestamp", columns="keyword", values="totalResults")

    plt.figure(figsize=(10, 6))
    for keyword in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[keyword], marker="o", label=keyword)

    plt.title("AIEO Visibility Tracker (KGNINJA AutoPulse)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Total Search Results")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ Chart saved as {CHART_FILE}")

def main():
    print("🚀 Running AIEO Visibility Pulse (Enhanced Mode)")
    if not API_KEY or not CX_ID:
        raise ValueError("❌ GOOGLE_API_KEY または GOOGLE_CX_ID が設定されていません")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for keyword in KEYWORDS:
        try:
            total, top_results = google_search(keyword)
            save_log(timestamp, keyword, total, top_results)
            print(f"✅ {keyword}: {total:,} hits ({[t[0] for t in top_results]})")
        except Exception as e:
            print(f"⚠️ {keyword} failed: {e}")

    plot_visibility_chart()
    print("🎯 Completed visibility tracking")

if __name__ == "__main__":
    main()

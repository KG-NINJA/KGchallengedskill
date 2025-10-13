import os
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = os.getenv("GOOGLE_API_KEY")
CX_ID = os.getenv("GOOGLE_CX")
KEYWORDS = ["KGNINJA", "KGNINJA AI", "FuwaCoco", "Psycho-Frame", "AIEO"]
LOG_FILE = "visibility_log.csv"
CHART_FILE = "visibility_chart.png"
GROWTH_CHART = "visibility_growth_rate.png"

KG_DOMAINS = [
    'kg-ninja.github.io',
    'kaggle.com/kgninja',
    'fiverr.com/kgninja'
]

# ヘッダーを定数として定義（重要！）
CSV_HEADER = [
    "timestamp", "keyword", "totalResults", "search_time",
    "kg_rank", "kg_url",
    "top1_title", "top1_url",
    "top2_title", "top2_url",
    "top3_title", "top3_url"
]


def google_search_with_retry(keyword, max_retries=3):
    """リトライ機能付き検索"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": CX_ID, "q": keyword}
    
    for attempt in range(max_retries):
        try:
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            total = int(data.get("searchInformation", {}).get("totalResults", 0))
            items = data.get("items", [])
            top_results = [(i.get("title", ""), i.get("link", "")) 
                          for i in items[:10]]
            
            search_time = res.elapsed.total_seconds()
            
            return total, top_results, search_time
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"⏳ Rate limited, waiting {wait_time}s...")
                import time
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
    
    raise Exception(f"Failed after {max_retries} attempts")


def track_kg_ranking(top_results):
    """KG-NINJAサイトの順位を検出"""
    for idx, (title, url) in enumerate(top_results, 1):
        for domain in KG_DOMAINS:
            if domain.lower() in url.lower():
                return idx, url
    return None, None


def save_log_enhanced(timestamp, keyword, total, top_results, search_time):
    """拡張ログ保存（修正版）"""
    kg_rank, kg_url = track_kg_ranking(top_results)
    
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # ヘッダー書き込み（ファイルが新規の場合のみ）
        if not file_exists:
            writer.writerow(CSV_HEADER)
        
        # データ行を構築
        row = [
            timestamp, 
            keyword, 
            total, 
            f"{search_time:.3f}",
            kg_rank or "", 
            kg_url or ""
        ]
        
        # Top 3の結果を追加
        for title, url in top_results[:3]:
            row.extend([title, url])
        
        # 不足分を空文字で埋める（修正：CSV_HEADERを使用）
        while len(row) < len(CSV_HEADER):
            row.append("")
        
        writer.writerow(row)


def plot_dual_axis_chart():
    """2軸グラフで異なるスケールを表示"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No log file to plot")
        return
    
    df = pd.read_csv(LOG_FILE)
    
    if df.empty:
        print("⚠️ Empty log file")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    pivot_df = df.pivot(index="timestamp", columns="keyword", values="totalResults")
    
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # 左軸：小規模キーワード
    small_kw = ["KGNINJA", "KGNINJA AI", "FuwaCoco"]
    colors1 = ['#2ecc71', '#e74c3c', '#f39c12']
    
    for keyword, color in zip(small_kw, colors1):
        if keyword in pivot_df.columns:
            ax1.plot(pivot_df.index, pivot_df[keyword], 
                    marker='o', label=keyword, linewidth=2.5, 
                    color=color, markersize=6)
    
    ax1.set_xlabel("Date", fontsize=13, fontweight='bold')
    ax1.set_ylabel("Search Results (Emerging)", fontsize=13, 
                   fontweight='bold', color='#2ecc71')
    ax1.tick_params(axis='y', labelcolor='#2ecc71')
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(True, alpha=0.2)
    
    # 右軸：大規模キーワード
    ax2 = ax1.twinx()
    large_kw = ["Psycho-Frame", "AIEO"]
    colors2 = ['#9b59b6', '#3498db']
    
    for keyword, color in zip(large_kw, colors2):
        if keyword in pivot_df.columns:
            ax2.plot(pivot_df.index, pivot_df[keyword], 
                    marker='s', label=keyword, linewidth=2.5, 
                    linestyle='--', alpha=0.8, color=color, markersize=6)
    
    ax2.set_ylabel("Search Results (Established)", fontsize=13, 
                   fontweight='bold', color='#9b59b6')
    ax2.tick_params(axis='y', labelcolor='#9b59b6')
    ax2.legend(loc='upper right', fontsize=11)
    
    plt.title("AIEO Visibility Tracker (KGNINJA AutoPulse)", 
             fontsize=17, fontweight='bold', pad=20)
    
    fig.tight_layout()
    plt.savefig(CHART_FILE, dpi=150, bbox_inches='tight')
    print(f"✅ Dual-axis chart saved as {CHART_FILE}")


def plot_growth_rate():
    """成長率グラフ"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No log file for growth rate")
        return
    
    df = pd.read_csv(LOG_FILE)
    
    if df.empty or len(df) < 2:
        print("⚠️ Insufficient data for growth rate")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    pivot_df = df.pivot(index="timestamp", columns="keyword", values="totalResults")
    
    # 日次成長率
    growth_df = pivot_df.pct_change() * 100
    
    plt.figure(figsize=(14, 6))
    for keyword in growth_df.columns:
        plt.plot(growth_df.index, growth_df[keyword], 
                marker='o', label=keyword, linewidth=2, alpha=0.8)
    
    plt.title("Daily Growth Rate (%)", fontsize=15, fontweight='bold')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Growth Rate (%)", fontsize=12)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(GROWTH_CHART, dpi=150)
    print(f"✅ Growth rate chart saved as {GROWTH_CHART}")


def main():
    """メイン処理"""
    print("🚀 Running AIEO Visibility Pulse (Ultra Enhanced Mode)")
    
    if not API_KEY or not CX_ID:
        raise ValueError("❌ GOOGLE_API_KEY または GOOGLE_CX が設定されていません")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for keyword in KEYWORDS:
        try:
            total, top_results, search_time = google_search_with_retry(keyword)
            save_log_enhanced(timestamp, keyword, total, top_results, search_time)
            
            kg_rank, _ = track_kg_ranking(top_results)
            rank_info = f" [🎯 Rank #{kg_rank}]" if kg_rank else ""
            
            print(f"✅ {keyword}: {total:,} hits{rank_info} ({search_time:.2f}s)")
            
            import time
            time.sleep(1)  # API制限回避
            
        except Exception as e:
            print(f"⚠️ {keyword} failed: {e}")
    
    plot_dual_axis_chart()
    plot_growth_rate()
    
    print("🎯 Completed visibility tracking with enhanced analytics")


if __name__ == "__main__":
    main()

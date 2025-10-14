#!/usr/bin/env python3
"""
AIEO Multi-Keyword Visibility Tracker (最適化版)
戦略的キーワードのみを追跡
"""

import os
import csv
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 環境変数から取得
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CX = os.environ.get('GOOGLE_CX')

# 監視するキーワードリスト（最適化版）
# 🎯 戦略: ニッチで独占可能なキーワードに集中
KEYWORDS = [
    "KGNINJA AI",           # 🏆 66.7% - 最強キーワード
    "KGNINJA",              # 🎯 38.1% - ブランド名
    "AIEO",                 # 📈 0% → 成長目標
    "Vibe Coding",          # 🆕 新規 - あなたの造語
    "KGNINJA Prototype",    # 🆕 新規 - さらにニッチ化
]

# 廃止したキーワード（参考）
# ❌ FuwaCoco - 既存コミュニティが強固（1,680件、0%可視性）
# ❌ Psycho-Frame - 競合が膨大（19,600,000件、0%可視性）

# ターゲットドメイン（自分のコンテンツ）
TARGET_DOMAIN = "github.com/KG-NINJA"

# ファイルパス
LOG_FILE = "visibility_log.csv"
CHART_FILE = "visibility_chart.png"
GROWTH_CHART_FILE = "visibility_growth_rate.png"


def google_search(query, api_key, cx, num=10):
    """
    Google Custom Search APIで検索を実行
    
    Args:
        query: 検索クエリ
        api_key: Google API Key
        cx: Custom Search Engine ID
        num: 取得する結果数（最大10）
    
    Returns:
        検索結果のJSONまたはNone
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': num
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Search error for '{query}': {e}")
        return None


def extract_top_results(results, count=3):
    """
    検索結果からTop N件を抽出
    
    Args:
        results: Google検索結果のJSON
        count: 抽出する件数
    
    Returns:
        タイトルとURLのリスト
    """
    if not results or 'items' not in results:
        return []
    
    top_results = []
    for item in results.get('items', [])[:count]:
        top_results.append({
            'title': item.get('title', 'N/A'),
            'url': item.get('link', 'N/A')
        })
    
    return top_results


def track_visibility():
    """
    キーワードごとの検索順位を追跡
    
    Returns:
        全データのリスト
    """
    print("📊 Starting AIEO Visibility Tracking (Optimized)...")
    print(f"🎯 Strategy: Focus on niche, high-impact keywords\n")
    
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        print("❌ Error: Google API credentials not found.")
        print("   Please set GOOGLE_API_KEY and GOOGLE_CX environment variables.")
        return []
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # 既存ログの読み込み
    data = []
    file_exists = os.path.exists(LOG_FILE)
    
    if file_exists:
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                # 廃止キーワードを除外（過去データのクリーンアップ）
                data = [row for row in data if row.get('keyword') not in ['FuwaCoco', 'Psycho-Frame']]
                print(f"✅ Loaded {len(data)} existing records (cleaned)")
        except Exception as e:
            print(f"⚠️  Could not read existing log: {e}")
    
    # 新規データの収集
    new_entries = []
    print(f"🔍 Tracking {len(KEYWORDS)} strategic keywords...\n")
    
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"[{i}/{len(KEYWORDS)}] 🔎 Searching: {keyword}")
        
        results = google_search(keyword, GOOGLE_API_KEY, GOOGLE_CX)
        
        if not results:
            print(f"   ❌ Failed to get results")
            continue
        
        # 検索結果数
        total_results = 'N/A'
        if 'searchInformation' in results:
            total_results = results['searchInformation'].get('totalResults', 'N/A')
        
        # Top3の結果を取得
        top_results = extract_top_results(results, count=3)
        
        # エントリー作成
        entry = {
            'timestamp': timestamp,
            'keyword': keyword,
            'totalResults': total_results,
        }
        
        # Top3のタイトルとURLを追加
        for j, result in enumerate(top_results, 1):
            entry[f'top{j}_title'] = result['title']
            entry[f'top{j}_url'] = result['url']
        
        # Top3に満たない場合は空文字で埋める
        for j in range(len(top_results) + 1, 4):
            entry[f'top{j}_title'] = ''
            entry[f'top{j}_url'] = ''
        
        new_entries.append(entry)
        
        # 結果の表示
        print(f"   📊 Total results: {total_results}")
        
        # 自分のコンテンツがTop3に入っているかチェック
        own_content_count = 0
        for result in top_results:
            url = result['url'].lower()
            if any(domain in url for domain in ['x.com/fuwacocoownerkg', 'github.com/kg-ninja', 
                                                  'pinterest.com/kgninja', 'instagram.com']):
                own_content_count += 1
        
        if own_content_count > 0:
            visibility = (own_content_count / 3) * 100
            print(f"   ✅ Your content: {own_content_count}/3 in Top 3 ({visibility:.1f}%)")
        else:
            print(f"   ⚠️  Your content: Not in Top 3")
        
        print()
    
    # データを結合
    data.extend(new_entries)
    
    # CSVに書き込み
    if data:
        fieldnames = ['timestamp', 'keyword', 'totalResults',
                     'top1_title', 'top1_url',
                     'top2_title', 'top2_url',
                     'top3_title', 'top3_url']
        
        try:
            with open(LOG_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ Saved {len(data)} total records to {LOG_FILE}")
            print(f"   ({len(new_entries)} new entries added)")
        except Exception as e:
            print(f"❌ Error saving log file: {e}")
    
    return data


def analyze_and_visualize(data):
    """
    データを分析してグラフを生成
    
    Args:
        data: 全データのリスト
    """
    if not data:
        print("⚠️  No data to analyze")
        return
    
    print("\n📈 Generating visualizations...")
    
    # DataFrameに変換
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['totalResults'] = pd.to_numeric(df['totalResults'], errors='coerce')
    
    # グラフ1: 検索結果数の推移
    plt.figure(figsize=(14, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for i, keyword in enumerate(KEYWORDS):
        kw_data = df[df['keyword'] == keyword].sort_values('timestamp')
        if not kw_data.empty and kw_data['totalResults'].notna().any():
            plt.plot(kw_data['timestamp'], kw_data['totalResults'], 
                    marker='o', label=keyword, linewidth=2, 
                    color=colors[i % len(colors)], markersize=6)
    
    plt.xlabel('Date', fontsize=12, fontweight='bold')
    plt.ylabel('Total Search Results', fontsize=12, fontweight='bold')
    plt.title('Search Results Volume - Strategic Keywords Only', 
             fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=10, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    try:
        plt.savefig(CHART_FILE, dpi=150, bbox_inches='tight')
        print(f"✅ Chart saved: {CHART_FILE}")
    except Exception as e:
        print(f"❌ Error saving chart: {e}")
    finally:
        plt.close()
    
    # 統計情報の表示
    print("\n" + "="*70)
    print("📊 STRATEGIC KEYWORDS PERFORMANCE")
    print("="*70)
    
    for keyword in KEYWORDS:
        kw_data = df[df['keyword'] == keyword].sort_values('timestamp')
        if not kw_data.empty:
            latest = kw_data.iloc[-1]
            
            print(f"\n🔑 {keyword}")
            
            if pd.notna(latest['totalResults']):
                print(f"   Search Volume: {int(latest['totalResults']):,}")
            
            # トレンド分析
            if len(kw_data) >= 2 and kw_data['totalResults'].notna().sum() >= 2:
                first = kw_data[kw_data['totalResults'].notna()].iloc[0]['totalResults']
                last = kw_data[kw_data['totalResults'].notna()].iloc[-1]['totalResults']
                change = ((last - first) / first * 100) if first > 0 else 0
                trend_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"   Trend: {trend_icon} {change:+.1f}%")
            
            print(f"   Total Checks: {len(kw_data)}")
            print(f"   Last Updated: {latest['timestamp']}")
    
    print("\n" + "="*70)


def print_strategy_summary():
    """戦略サマリーを表示"""
    print("\n" + "="*70)
    print("🎯 KEYWORD STRATEGY SUMMARY")
    print("="*70)
    
    print("\n✅ ACTIVE KEYWORDS (High Impact):")
    print("   1. KGNINJA AI       - 🏆 Primary brand (66.7% visibility)")
    print("   2. KGNINJA          - 🎯 Core brand (38.1% visibility)")
    print("   3. AIEO             - 📈 Growth target (0% → 30%+)")
    print("   4. Vibe Coding      - 🆕 Unique positioning")
    print("   5. KGNINJA Prototype - 🆕 Technical specialization")
    
    print("\n❌ RETIRED KEYWORDS (Low ROI):")
    print("   • FuwaCoco         - Removed (0% visibility, strong competition)")
    print("   • Psycho-Frame     - Removed (0% visibility, 19M+ results)")
    
    print("\n💡 RATIONALE:")
    print("   Focus on keywords where you can achieve 30%+ visibility")
    print("   Avoid generic terms with millions of competing results")
    print("   Build authority in niche, searchable terms")
    
    print("\n🎯 SUCCESS METRICS:")
    print("   • KGNINJA AI: Maintain 60%+ visibility")
    print("   • KGNINJA: Increase to 50%+ visibility")
    print("   • AIEO: Achieve 30%+ visibility in 30 days")
    print("   • New keywords: Establish 40%+ visibility")
    
    print("="*70)


def main():
    """メイン処理"""
    print("="*70)
    print("🌀 AIEO MULTI-KEYWORD VISIBILITY PULSE (OPTIMIZED)")
    print("="*70)
    print(f"⏰ Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🎯 Strategy: Focus on high-impact, niche keywords")
    print(f"🔍 Keywords tracked: {len(KEYWORDS)}")
    print("="*70 + "\n")
    
    # 戦略サマリー
    print_strategy_summary()
    
    # データ収集
    data = track_visibility()
    
    # 分析と可視化
    if data:
        analyze_and_visualize(data)
        print("\n✅ Tracking complete. Strategic keywords optimized!")
    else:
        print("\n❌ No data collected. Please check your API credentials.")
    
    print("\n" + "="*70)
    print("💡 Next Steps:")
    print("   1. Create more KGNINJA AI content")
    print("   2. Publish AIEO implementation guides")
    print("   3. Introduce 'Vibe Coding' concept widely")
    print("   4. Monitor visibility scores weekly")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

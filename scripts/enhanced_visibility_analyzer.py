#!/usr/bin/env python3
"""
Enhanced AIEO Visibility Analyzer
visibility_log.csvからより詳細な分析を行う
"""

import csv
import os
from datetime import datetime
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

LOG_FILE = "visibility_log.csv"
CHART_FILE = "visibility_detailed_analysis.png"

def load_and_clean_data():
    """CSVデータを読み込み、クリーニング"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ {LOG_FILE} not found")
        return None
    
    data = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 不正な行をスキップ（数値だけの行など）
            if row.get('keyword') and not row['keyword'].isdigit():
                data.append(row)
    
    return data

def analyze_keyword_performance(data):
    """キーワード別のパフォーマンス分析"""
    keyword_stats = defaultdict(lambda: {
        'checks': 0,
        'total_results': [],
        'top1_urls': [],
        'top2_urls': [],
        'top3_urls': [],
        'timestamps': []
    })
    
    for row in data:
        keyword = row['keyword']
        keyword_stats[keyword]['checks'] += 1
        keyword_stats[keyword]['timestamps'].append(row['timestamp'])
        
        # 検索結果数の記録
        try:
            total = int(row.get('totalResults', 0))
            keyword_stats[keyword]['total_results'].append(total)
        except (ValueError, TypeError):
            pass
        
        # Top URLsの記録
        for i in range(1, 4):
            url = row.get(f'top{i}_url', '')
            if url:
                keyword_stats[keyword][f'top{i}_urls'].append(url)
    
    return keyword_stats

def check_own_content(url, own_domains=['x.com/FuwaCocoOwnerKG', 'twitter.com/FuwaCocoOwnerKG', 
                                        'github.com/KG-NINJA', 'pinterest.com/kgninja', 
                                        'instagram.com/kgninja']):
    """自分のコンテンツかどうかチェック"""
    url_lower = url.lower()
    return any(domain.lower() in url_lower for domain in own_domains)

def calculate_visibility_score(stats):
    """可視性スコアを計算（自分のコンテンツがTop3に何回入ったか）"""
    own_content_count = 0
    total_checks = stats['checks'] * 3  # Top3 x チェック回数
    
    for i in range(1, 4):
        urls = stats[f'top{i}_urls']
        own_content_count += sum(1 for url in urls if check_own_content(url))
    
    return (own_content_count / total_checks * 100) if total_checks > 0 else 0

def print_detailed_analysis(keyword_stats):
    """詳細分析を表示"""
    print("\n" + "="*80)
    print("📊 DETAILED KEYWORD ANALYSIS")
    print("="*80)
    
    # スコアでソート
    sorted_keywords = sorted(
        keyword_stats.items(),
        key=lambda x: calculate_visibility_score(x[1]),
        reverse=True
    )
    
    for keyword, stats in sorted_keywords:
        visibility_score = calculate_visibility_score(stats)
        
        print(f"\n{'='*80}")
        print(f"🔑 {keyword}")
        print(f"{'='*80}")
        
        # 基本統計
        print(f"📈 Total Checks: {stats['checks']}")
        
        if stats['total_results']:
            avg_results = sum(stats['total_results']) / len(stats['total_results'])
            print(f"📊 Avg Search Results: {avg_results:,.0f}")
            
            # トレンド分析
            if len(stats['total_results']) >= 2:
                first = stats['total_results'][0]
                last = stats['total_results'][-1]
                change = ((last - first) / first * 100) if first > 0 else 0
                trend = "📈" if change > 0 else "📉"
                print(f"{trend} Results Trend: {change:+.1f}%")
        
        # 可視性スコア
        print(f"\n🎯 Visibility Score: {visibility_score:.1f}%")
        
        # 自分のコンテンツの出現頻度
        own_content_appearances = {
            'Top 1': sum(1 for url in stats['top1_urls'] if check_own_content(url)),
            'Top 2': sum(1 for url in stats['top2_urls'] if check_own_content(url)),
            'Top 3': sum(1 for url in stats['top3_urls'] if check_own_content(url))
        }
        
        print("\n📍 Your Content Appearances:")
        for position, count in own_content_appearances.items():
            percentage = (count / stats['checks'] * 100) if stats['checks'] > 0 else 0
            print(f"   {position}: {count}/{stats['checks']} ({percentage:.1f}%)")
        
        # 最も多く表示されたURL
        print("\n🔗 Most Common URLs:")
        for i in range(1, 4):
            urls = stats[f'top{i}_urls']
            if urls:
                # URLの出現回数をカウント
                url_counts = defaultdict(int)
                for url in urls:
                    url_counts[url] += 1
                
                # 最も多いURLを取得
                most_common = max(url_counts.items(), key=lambda x: x[1])
                url, count = most_common
                own_marker = "✅ (YOUR CONTENT)" if check_own_content(url) else ""
                print(f"   Top {i}: {url[:60]}... ({count}/{stats['checks']}) {own_marker}")
        
        # 期間
        if stats['timestamps']:
            print(f"\n📅 Period: {stats['timestamps'][0]} → {stats['timestamps'][-1]}")

def visualize_trends(data):
    """トレンドの可視化"""
    df = pd.DataFrame(data)
    
    # タイムスタンプをdatetimeに変換
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['totalResults'] = pd.to_numeric(df['totalResults'], errors='coerce')
    
    keywords = df['keyword'].unique()
    
    # 1つ目のグラフ: 検索結果数の推移
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # 検索結果数の推移
    ax1 = axes[0]
    for keyword in keywords:
        kw_data = df[df['keyword'] == keyword].sort_values('timestamp')
        if not kw_data.empty and kw_data['totalResults'].notna().any():
            ax1.plot(kw_data['timestamp'], kw_data['totalResults'], 
                    marker='o', label=keyword, linewidth=2, markersize=6)
    
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Search Results', fontsize=12, fontweight='bold')
    ax1.set_title('Search Results Volume Over Time', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 2つ目のグラフ: 可視性スコアの推移
    ax2 = axes[1]
    keyword_stats = analyze_keyword_performance(data)
    
    visibility_scores = []
    for keyword in keywords:
        score = calculate_visibility_score(keyword_stats[keyword])
        visibility_scores.append((keyword, score))
    
    visibility_scores.sort(key=lambda x: x[1], reverse=True)
    keywords_sorted = [k for k, _ in visibility_scores]
    scores = [s for _, s in visibility_scores]
    
    colors = ['#4CAF50' if s > 70 else '#FFC107' if s > 40 else '#F44336' for s in scores]
    bars = ax2.barh(keywords_sorted, scores, color=colors, alpha=0.7)
    
    ax2.set_xlabel('Visibility Score (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Keyword', fontsize=12, fontweight='bold')
    ax2.set_title('Visibility Score by Keyword (% of Your Content in Top 3)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim(0, 100)
    
    # 値をバーに表示
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax2.text(score + 2, i, f'{score:.1f}%', 
                va='center', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    
    try:
        plt.savefig(CHART_FILE, dpi=150, bbox_inches='tight')
        print(f"\n✅ Visualization saved: {CHART_FILE}")
    except Exception as e:
        print(f"\n❌ Error saving chart: {e}")
    finally:
        plt.close()

def generate_recommendations(keyword_stats):
    """改善提案を生成"""
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    # スコアでソート
    sorted_keywords = sorted(
        keyword_stats.items(),
        key=lambda x: calculate_visibility_score(x[1]),
        reverse=True
    )
    
    print("\n🏆 STRENGTHS (Keep doing what you're doing!):")
    for keyword, stats in sorted_keywords[:2]:
        score = calculate_visibility_score(stats)
        if score > 50:
            print(f"   ✅ {keyword}: {score:.1f}% visibility")
            print(f"      → Your content dominates this keyword")
    
    print("\n🎯 OPPORTUNITIES (Focus your efforts here):")
    for keyword, stats in sorted_keywords[-2:]:
        score = calculate_visibility_score(stats)
        if score < 50:
            print(f"   ⚠️  {keyword}: {score:.1f}% visibility")
            print(f"      → Create more content around this keyword")
            
            # 競合分析
            top_competitors = set()
            for i in range(1, 4):
                for url in stats[f'top{i}_urls']:
                    if not check_own_content(url):
                        # ドメイン抽出
                        if '//' in url:
                            domain = url.split('//')[1].split('/')[0]
                            top_competitors.add(domain)
            
            if top_competitors:
                print(f"      → Main competitors: {', '.join(list(top_competitors)[:3])}")

def main():
    """メイン処理"""
    print("="*80)
    print("🔍 ENHANCED AIEO VISIBILITY ANALYZER")
    print("="*80)
    print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # データ読み込み
    data = load_and_clean_data()
    if not data:
        return
    
    print(f"✅ Loaded {len(data)} records from {LOG_FILE}")
    
    # 分析
    keyword_stats = analyze_keyword_performance(data)
    print(f"✅ Analyzing {len(keyword_stats)} keywords\n")
    
    # 詳細分析を表示
    print_detailed_analysis(keyword_stats)
    
    # 可視化
    visualize_trends(data)
    
    # 推奨事項
    generate_recommendations(keyword_stats)
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80)

if __name__ == "__main__":
    main()

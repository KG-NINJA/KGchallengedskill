#!/usr/bin/env python3
"""
Enhanced AIEO Visibility Analyzer (最適化版)
戦略的キーワードのみを分析
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

# 戦略的キーワード（追跡対象）
STRATEGIC_KEYWORDS = [
    "KGNINJA AI",
    "KGNINJA",
    "AIEO",
    "Vibe Coding",
    "KGNINJA Prototype"
]

# 廃止したキーワード（分析から除外）
DEPRECATED_KEYWORDS = ["FuwaCoco", "Psycho-Frame"]


def load_and_clean_data():
    """CSVデータを読み込み、クリーニング"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ {LOG_FILE} not found")
        return None
    
    data = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keyword = row.get('keyword', '')
            # 戦略的キーワードのみを保持
            if keyword in STRATEGIC_KEYWORDS:
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
                                        'instagram.com']):
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
    print("📊 STRATEGIC KEYWORDS DETAILED ANALYSIS")
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
            
            # 競合レベルの評価
            if avg_results < 1000:
                competition = "🟢 Low (Excellent for ranking)"
            elif avg_results < 100000:
                competition = "🟡 Medium (Good opportunity)"
            else:
                competition = "🔴 High (Challenging)"
            print(f"🎯 Competition Level: {competition}")
            
            # トレンド分析
            if len(stats['total_results']) >= 2:
                first = stats['total_results'][0]
                last = stats['total_results'][-1]
                change = ((last - first) / first * 100) if first > 0 else 0
                trend = "📈" if change > 0 else "📉"
                print(f"{trend} Results Trend: {change:+.1f}%")
        
        # 可視性スコア
        print(f"\n🎯 Visibility Score: {visibility_score:.1f}%")
        
        # スコア評価
        if visibility_score >= 60:
            evaluation = "🏆 Excellent - Dominant position"
        elif visibility_score >= 40:
            evaluation = "✅ Good - Strong presence"
        elif visibility_score >= 20:
            evaluation = "⚠️  Fair - Needs improvement"
        else:
            evaluation = "❌ Poor - Requires action"
        print(f"   {evaluation}")
        
        # 自分のコンテンツの出現頻度
        own_content_appearances = {
            'Top 1': sum(1 for url in stats['top1_urls'] if check_own_content(url)),
            'Top 2': sum(1 for url in stats['top2_urls'] if check_own_content(url)),
            'Top 3': sum(1 for url in stats['top3_urls'] if check_own_content(url))
        }
        
        print("\n📍 Your Content Appearances:")
        for position, count in own_content_appearances.items():
            percentage = (count / stats['checks'] * 100) if stats['checks'] > 0 else 0
            marker = "✅" if count > 0 else "❌"
            print(f"   {marker} {position}: {count}/{stats['checks']} ({percentage:.1f}%)")
        
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
    
    keywords = [k for k in STRATEGIC_KEYWORDS if k in df['keyword'].values]
    
    # 2つのグラフ
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # グラフ1: 検索結果数の推移
    ax1 = axes[0]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for i, keyword in enumerate(keywords):
        kw_data = df[df['keyword'] == keyword].sort_values('timestamp')
        if not kw_data.empty and kw_data['totalResults'].notna().any():
            ax1.plot(kw_data['timestamp'], kw_data['totalResults'], 
                    marker='o', label=keyword, linewidth=2, markersize=6,
                    color=colors[i % len(colors)])
    
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Search Results', fontsize=12, fontweight='bold')
    ax1.set_title('Search Results Volume - Strategic Keywords', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # グラフ2: 可視性スコア
    ax2 = axes[1]
    keyword_stats = analyze_keyword_performance(data)
    
    visibility_scores = []
    for keyword in keywords:
        if keyword in keyword_stats:
            score = calculate_visibility_score(keyword_stats[keyword])
            visibility_scores.append((keyword, score))
    
    visibility_scores.sort(key=lambda x: x[1], reverse=True)
    keywords_sorted = [k for k, _ in visibility_scores]
    scores = [s for _, s in visibility_scores]
    
    colors = ['#4CAF50' if s >= 60 else '#FFC107' if s >= 40 else '#FF9800' if s >= 20 else '#F44336' for s in scores]
    bars = ax2.barh(keywords_sorted, scores, color=colors, alpha=0.8)
    
    ax2.set_xlabel('Visibility Score (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Keyword', fontsize=12, fontweight='bold')
    ax2.set_title('Visibility Score by Strategic Keyword', 
                 fontsize=14, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim(0, 100)
    
    # スコアの意味を凡例として追加
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4CAF50', label='60%+ Excellent'),
        Patch(facecolor='#FFC107', label='40-60% Good'),
        Patch(facecolor='#FF9800', label='20-40% Fair'),
        Patch(facecolor='#F44336', label='<20% Poor')
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
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


def generate_strategic_recommendations(keyword_stats):
    """戦略的推奨事項を生成"""
    print("\n" + "="*80)
    print("💡 STRATEGIC RECOMMENDATIONS")
    print("="*80)
    
    # スコアでソート
    sorted_keywords = sorted(
        keyword_stats.items(),
        key=lambda x: calculate_visibility_score(x[1]),
        reverse=True
    )
    
    print("\n🏆 MAINTAIN & AMPLIFY (Keep the momentum):")
    for keyword, stats in sorted_keywords:
        score = calculate_visibility_score(stats)
        if score >= 50:
            print(f"\n   ✅ {keyword}: {score:.1f}% visibility")
            print(f"      → Continue creating content with this keyword")
            print(f"      → Your dominant position is established")
            
            # 具体的なアクション
            if keyword == "KGNINJA AI":
                print(f"      → Action: Post weekly updates on X/Twitter with #KGNINJAAI")
                print(f"      → Action: Add 'KGNINJA AI Creator' to all profiles")
            elif keyword == "KGNINJA":
                print(f"      → Action: Cross-link between KGNINJA and KGNINJA AI content")
    
    print("\n🎯 BUILD & GROW (Focus here for quick wins):")
    for keyword, stats in sorted_keywords:
        score = calculate_visibility_score(stats)
        if 20 <= score < 50:
            print(f"\n   📈 {keyword}: {score:.1f}% visibility")
            print(f"      → Moderate presence, high growth potential")
            print(f"      → Recommended: 2-3 pieces of content per week")
    
    print("\n🚀 ESTABLISH & DOMINATE (New opportunities):")
    for keyword, stats in sorted_keywords:
        score = calculate_visibility_score(stats)
        if score < 20:
            avg_results = sum(stats['total_results']) / len(stats['total_results']) if stats['total_results'] else 0
            
            print(f"\n   🆕 {keyword}: {score:.1f}% visibility")
            
            if avg_results < 1000:
                print(f"      → Low competition ({avg_results:,.0f} results) - Excellent opportunity!")
                print(f"      → Action: Create 1 major piece of content (blog, video, or demo)")
                print(f"      → Expected: 40%+ visibility within 2 weeks")
            elif avg_results < 100000:
                print(f"      → Medium competition ({avg_results:,.0f} results)")
                print(f"      → Action: Publish comprehensive guide or

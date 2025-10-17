#!/usr/bin/env python3
"""
AIEO Resonance Indexer
共鳴スコアを計算し、可視化画像を生成
"""

import json
import os
from pathlib import Path
from datetime import datetime
import csv

# グラフ描画ライブラリ
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib import font_manager
    HAS_MATPLOTLIB = True
except ImportError:
    print("⚠ matplotlib がインストールされていません。画像生成をスキップします。")
    HAS_MATPLOTLIB = False

# データディレクトリ
DATA_DIR = Path("data")
VISIBILITY_LOG = Path("visibility_log.csv")
RESONANCE_OUTPUT = Path("resonance_snapshot.png")

def load_visibility_data() -> list:
    """可視性ログを読み込む"""
    if not VISIBILITY_LOG.exists():
        print("⚠ visibility_log.csv が見つかりません")
        return []
    
    data = []
    try:
        with open(VISIBILITY_LOG, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        print(f"✓ {len(data)} 件の可視性データを読み込み")
    except Exception as e:
        print(f"❌ CSV読み込みエラー: {e}")
    
    return data


def calculate_resonance_scores(visibility_data: list) -> dict:
    """
    共鳴スコアを計算
    
    共鳴スコア = ドメイン多様性(40点) + 言及頻度(40点) + 影響度(20点)
    """
    resonance_scores = {}
    
    for row in visibility_data:
        name = row.get('name', 'Unknown')
        
        # 各メトリクスを抽出
        try:
            github_followers = float(row.get('github_followers', 0))
            web_mentions = float(row.get('web_mentions', 0))
            domain_mentions = float(row.get('domain_mentions', 0))
        except ValueError:
            continue
        
        # 共鳴スコア計算
        # ドメイン多様性: 複数ドメインでの言及が多いほど高い
        domain_diversity = min(domain_mentions / 100, 40)
        
        # 言及頻度: Web言及数
        mention_frequency = min((web_mentions / 1000), 40)
        
        # 影響度: GitHub フォロワー
        impact = min(github_followers / 10, 20)
        
        total_resonance = domain_diversity + mention_frequency + impact
        
        resonance_scores[name] = {
            'resonance': round(total_resonance, 2),
            'domain_diversity': round(domain_diversity, 2),
            'mention_frequency': round(mention_frequency, 2),
            'impact': round(impact, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    return resonance_scores


def generate_resonance_visualization(resonance_scores: dict) -> None:
    """共鳴スコアを可視化"""
    if not HAS_MATPLOTLIB or not resonance_scores:
        print("⚠ 可視化スキップ")
        return
    
    try:
        # 日本語フォント設定
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # データの準備
        names = list(resonance_scores.keys())
        scores = [resonance_scores[name]['resonance'] for name in names]
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'][:len(names)]
        
        # グラフ生成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('AIEO Resonance Index', fontsize=16, fontweight='bold')
        
        # 左: 共鳴スコアの棒グラフ
        bars = ax1.barh(names, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Resonance Score', fontsize=12)
        ax1.set_title('Total Resonance by Person', fontsize=13, fontweight='bold')
        ax1.set_xlim(0, 100)
        
        # スコア値を表示
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax1.text(score + 2, i, f'{score:.1f}', va='center', fontsize=11, fontweight='bold')
        
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 右: 構成要素の積み上げ棒グラフ
        domain_vals = [resonance_scores[name]['domain_diversity'] for name in names]
        mention_vals = [resonance_scores[name]['mention_frequency'] for name in names]
        impact_vals = [resonance_scores[name]['impact'] for name in names]
        
        x_pos = range(len(names))
        ax2.bar(x_pos, domain_vals, label='Domain Diversity', color='#667eea', alpha=0.8, edgecolor='black', linewidth=1)
        ax2.bar(x_pos, mention_vals, bottom=domain_vals, label='Mention Frequency', color='#764ba2', alpha=0.8, edgecolor='black', linewidth=1)
        
        bottom_val = [d + m for d, m in zip(domain_vals, mention_vals)]
        ax2.bar(x_pos, impact_vals, bottom=bottom_val, label='Impact', color='#f093fb', alpha=0.8, edgecolor='black', linewidth=1)
        
        ax2.set_ylabel('Score', fontsize=12)
        ax2.set_title('Resonance Components', fontsize=13, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(names, rotation=45, ha='right')
        ax2.legend(loc='upper right', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(RESONANCE_OUTPUT, dpi=100, bbox_inches='tight', facecolor='white')
        print(f"✓ 可視化を保存: {RESONANCE_OUTPUT}")
        plt.close()
        
    except Exception as e:
        print(f"❌ グラフ生成エラー: {e}")


def save_resonance_report(resonance_scores: dict) -> None:
    """共鳴スコアをJSON形式で保存"""
    output_file = Path("resonance_report.json")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_entities": len(resonance_scores),
        "average_resonance": round(
            sum(s['resonance'] for s in resonance_scores.values()) / max(len(resonance_scores), 1),
            2
        ),
        "entities": resonance_scores
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ レポートを保存: {output_file}")
    except Exception as e:
        print(f"❌ レポート保存エラー: {e}")


def main():
    print("=" * 60)
    print("AIEO Resonance Indexer")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 可視性データを読み込む
    visibility_data = load_visibility_data()
    
    if not visibility_data:
        print("⚠ 処理するデータがありません")
        return
    
    # 共鳴スコアを計算
    resonance_scores = calculate_resonance_scores(visibility_data)
    print(f"\n✓ {len(resonance_scores)} 人物の共鳴スコアを計算")
    
    for name, score in resonance_scores.items():
        print(f"  {name}: {score['resonance']:.1f} "
              f"(Domain: {score['domain_diversity']:.1f}, "
              f"Mention: {score['mention_frequency']:.1f}, "
              f"Impact: {score['impact']:.1f})")
    
    # 可視化を生成
    generate_resonance_visualization(resonance_scores)
    
    # レポートを保存
    save_resonance_report(resonance_scores)
    
    print("\n" + "=" * 60)
    print("✓ 共鳴インデックス更新完了")
    print("=" * 60)


if __name__ == "__main__":
    main()

# scripts/aieo_composite_tracker.py
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ファイル確認
res_file = "resonance_log.csv"
vis_file = "visibility_log.csv"
output_chart = "aieo_composite_chart.png"
output_log = "aieo_composite_log.csv"

if not os.path.exists(res_file) or not os.path.exists(vis_file):
    print("必要なログファイルが存在しません。resonance_log.csv と visibility_log.csv を確認してください。")
    exit(1)

# データ読み込み
res_df = pd.read_csv(res_file)
vis_df = pd.read_csv(vis_file)

# タイムスタンプを揃える
res_df['timestamp'] = pd.to_datetime(res_df['timestamp'])
vis_df['timestamp'] = pd.to_datetime(vis_df['timestamp'])

merged = pd.merge_asof(
    res_df.sort_values('timestamp'),
    vis_df.sort_values('timestamp'),
    on='timestamp',
    direction='nearest',
    suffixes=('_resonance', '_visibility')
)

# 共鳴 × 可視性を掛け合わせた複合スコア
merged['AIEO_Index'] = merged['resonance_index'] * merged['visibility_index']

# スコアを0〜100スケールに正規化
merged['AIEO_Index'] = (merged['AIEO_Index'] / merged['AIEO_Index'].max()) * 100

# 保存
merged.to_csv(output_log, index=False)

# グラフ描画
plt.figure(figsize=(10,5))
plt.plot(merged['timestamp'], merged['AIEO_Index'], 'o-', color='gold', label='AIEO Index')
plt.xlabel('Timestamp (UTC)')
plt.ylabel('AIEO Index (0–100)')
plt.title('AIEO Resonance × Visibility Composite Index')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_chart, bbox_inches='tight')

print(f"{output_chart} と {output_log} を更新しました。")

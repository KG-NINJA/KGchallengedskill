import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# CSVファイル読み込み
vis_df = pd.read_csv('visibility_log.csv')
res_df = pd.read_csv('resonance_log.csv')

# 空チェック（安全スキップ）
if vis_df.empty or res_df.empty:
    print("空のデータが検出されました。AIEO効果の計算をスキップします。")
    exit(0)

# timestampをdatetime型に変換
vis_df['timestamp'] = pd.to_datetime(vis_df['timestamp'])
res_df['timestamp'] = pd.to_datetime(res_df['timestamp'])

# 両方のデータをtimestampで結合
merged = pd.merge_asof(
    vis_df.sort_values('timestamp'),
    res_df.sort_values('timestamp'),
    on='timestamp',
    direction='nearest'
)

# AIEO効果を計算（Visibility × Resonance）
merged['aieo_effect'] = merged['visibility_index'] * merged['resonance_index']

# ローリング平均でスムージング
merged['aieo_effect_smooth'] = merged['aieo_effect'].rolling(window=3, min_periods=1).mean()

# グラフ生成
plt.figure(figsize=(10, 5))
plt.plot(merged['timestamp'], merged['aieo_effect_smooth'], color='purple', marker='o', label='AIEO Effect (Smooth)')
plt.title("AIEO Effect Index (Visibility × Resonance)")
plt.xlabel("Timestamp (UTC)")
plt.ylabel("AIEO Effect Index (0–1)")
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("aieo_effect_chart.png")

# ログ保存
merged[['timestamp', 'aieo_effect_smooth']].to_csv("aieo_effect_log.csv", index=False)

print("✅ aieo_effect_chart.png と aieo_effect_log.csv を生成しました。")

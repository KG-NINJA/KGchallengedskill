import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

INPUT_FILE = "visibility_log.csv"
OUTPUT_LOG = "aieo_effect_log.csv"
CHART_FILE = "aieo_effect_chart.png"

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} が存在しません。Visibilityジョブを先に実行してください。")

    df = pd.read_csv(INPUT_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    pivot_df = df.pivot(index="timestamp", columns="keyword", values="totalResults")
    diff_df = pivot_df.diff().fillna(0)

    # 変化率を加重スコア化
    effect_df = (diff_df / pivot_df.shift(1)).fillna(0) * 100
    effect_df.to_csv(OUTPUT_LOG, encoding="utf-8")

    plt.figure(figsize=(10, 6))
    for keyword in effect_df.columns:
        plt.plot(effect_df.index, effect_df[keyword], marker="o", label=keyword)

    plt.title("AIEO Effect Analyzer (Visibility Change Rate)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Effect % Change")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ Chart saved as {CHART_FILE}")

if __name__ == "__main__":
    main()

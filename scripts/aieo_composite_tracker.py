import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

INPUT_FILE = "aieo_effect_log.csv"
OUTPUT_FILE = "aieo_resonance_log.csv"
CHART_FILE = "aieo_resonance_chart.png"

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} が存在しません。Effectジョブを先に実行してください。")

    df = pd.read_csv(INPUT_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 共鳴スコア = 各キーワードのEffect変化の標準偏差を反転＋平均
    df_numeric = df.select_dtypes(include="number")
    resonance_score = 100 - df_numeric.std(axis=1)
    composite_df = pd.DataFrame({"timestamp": df["timestamp"], "resonance_index": resonance_score})
    composite_df.to_csv(OUTPUT_FILE, index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(composite_df["timestamp"], composite_df["resonance_index"], color="purple", marker="o")
    plt.title("AIEO Resonance Index (Stability Composite)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Resonance Index (0–100)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ Chart saved as {CHART_FILE}")

if __name__ == "__main__":
    main()

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT_FILE = "aieo_effect_log.csv"
OUTPUT_FILE = "aieo_resonance_log.csv"
CHART_FILE = "aieo_resonance_chart.png"


def build_resonance_frame(df: pd.DataFrame) -> pd.DataFrame:
    """1本以上のEffect系列から0〜100の安定度スコアを生成する。"""
    if "timestamp" not in df.columns:
        raise ValueError("Effectログにtimestamp列がありません")

    timestamps = pd.to_datetime(
        df["timestamp"], format="mixed", errors="coerce", utc=True
    ).dt.tz_convert(None)
    numeric = df.drop(columns=["timestamp"]).apply(pd.to_numeric, errors="coerce")

    valid_rows = timestamps.notna() & numeric.notna().any(axis=1)
    dropped_rows = int((~valid_rows).sum())
    timestamps = timestamps.loc[valid_rows]
    numeric = numeric.loc[valid_rows]

    if numeric.empty or numeric.shape[1] == 0:
        raise ValueError("Effectログに有効な数値系列がありません")
    if dropped_rows:
        print(f"⚠️ 無効なEffect行を{dropped_rows}件除外しました")

    # ddof=0により、系列が1本でも分散0として有限値を維持する。
    dispersion = numeric.std(axis=1, ddof=0).replace([np.inf, -np.inf], np.nan)
    resonance_score = (100.0 - dispersion).clip(lower=0.0, upper=100.0).fillna(0.0)
    return pd.DataFrame(
        {
            "timestamp": timestamps.to_numpy(),
            "resonance_index": resonance_score.to_numpy(),
        }
    ).sort_values("timestamp")


def main() -> None:
    """Resonanceログとグラフを生成する。"""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"{INPUT_FILE} が存在しません。Effectジョブを先に実行してください。"
        )

    composite_df = build_resonance_frame(pd.read_csv(INPUT_FILE))
    composite_df.to_csv(OUTPUT_FILE, index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(
        composite_df["timestamp"],
        composite_df["resonance_index"],
        color="purple",
        marker="o",
    )
    plt.title("AIEO Resonance Index (Stability Composite)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Resonance Index (0–100)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()
    print(f"✅ {CHART_FILE}を生成しました")


if __name__ == "__main__":
    main()

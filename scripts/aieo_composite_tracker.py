import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT_FILE = "aieo_effect_log.csv"
OUTPUT_FILE = "aieo_resonance_log.csv"
CHART_FILE = "aieo_resonance_chart.png"


def build_resonance_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Build a bounded stability score from one or more effect series."""
    if "timestamp" not in df.columns:
        raise ValueError("effect log is missing column: timestamp")

    timestamps = pd.to_datetime(
        df["timestamp"], format="mixed", errors="coerce", utc=True
    ).dt.tz_convert(None)
    numeric = df.drop(columns=["timestamp"]).apply(pd.to_numeric, errors="coerce")

    valid_rows = timestamps.notna() & numeric.notna().any(axis=1)
    dropped_rows = int((~valid_rows).sum())
    timestamps = timestamps.loc[valid_rows]
    numeric = numeric.loc[valid_rows]

    if numeric.empty or numeric.shape[1] == 0:
        raise ValueError("effect log contains no valid numeric effect series")
    if dropped_rows:
        print(f"⚠️ Dropped {dropped_rows} invalid effect rows")

    # ddof=0 keeps a single effect series meaningful: its dispersion is zero.
    dispersion = numeric.std(axis=1, ddof=0).replace([np.inf, -np.inf], np.nan)
    resonance_score = (100.0 - dispersion).clip(lower=0.0, upper=100.0).fillna(0.0)
    return pd.DataFrame(
        {
            "timestamp": timestamps.to_numpy(),
            "resonance_index": resonance_score.to_numpy(),
        }
    ).sort_values("timestamp")


def main() -> None:
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
    print(f"✅ Chart saved as {CHART_FILE}")


if __name__ == "__main__":
    main()

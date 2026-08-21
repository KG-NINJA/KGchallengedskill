import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODERN_INPUT_FILE = Path("aieo_visibility_metrics.csv")
LEGACY_INPUT_FILE = Path("visibility_log.csv")
OUTPUT_LOG = "aieo_effect_log.csv"
CHART_FILE = "aieo_effect_chart.png"
MODERN_COLUMNS = {"timestamp", "name", "visibility_score"}
LEGACY_COLUMNS = {"timestamp", "keyword", "totalResults"}


def _normalize_source(df: pd.DataFrame) -> pd.DataFrame:
    """Convert either supported visibility schema to timestamp/keyword/value."""
    columns = set(df.columns)
    if MODERN_COLUMNS.issubset(columns):
        normalized = df[["timestamp", "name", "visibility_score"]].rename(
            columns={"name": "keyword", "visibility_score": "value"}
        )
        source_name = "modern metrics"
    elif LEGACY_COLUMNS.issubset(columns):
        normalized = df[["timestamp", "keyword", "totalResults"]].rename(
            columns={"totalResults": "value"}
        )
        source_name = "legacy visibility history"
    else:
        expected = sorted(MODERN_COLUMNS), sorted(LEGACY_COLUMNS)
        raise ValueError(
            "visibility log is missing columns for both supported schemas: "
            f"modern={expected[0]}, legacy={expected[1]}"
        )

    normalized = normalized.copy()
    normalized["timestamp"] = pd.to_datetime(
        normalized["timestamp"],
        format="mixed",
        errors="coerce",
        utc=True,
    ).dt.tz_convert(None)
    normalized["keyword"] = normalized["keyword"].astype("string").str.strip()
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")

    valid_rows = (
        normalized["timestamp"].notna()
        & normalized["keyword"].notna()
        & normalized["keyword"].str.len().gt(0)
        & normalized["value"].notna()
    )
    dropped_rows = int((~valid_rows).sum())
    normalized = normalized.loc[valid_rows]

    if normalized.empty:
        raise ValueError(f"{source_name} contains no valid rows")
    if dropped_rows:
        print(f"⚠️ Dropped {dropped_rows} invalid rows from {source_name}")
    print(f"✓ Using {source_name}: {len(normalized)} valid rows")
    return normalized


def build_effect_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage changes from modern or legacy visibility data."""
    normalized = _normalize_source(df)

    pivot_df = (
        normalized.pivot_table(
            index="timestamp",
            columns="keyword",
            values="value",
            aggfunc="last",
        )
        .sort_index()
    )

    previous = pivot_df.shift(1).replace(0, np.nan)
    return (
        pivot_df.diff()
        .div(previous)
        .mul(100)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )


def select_input_file() -> Path:
    """Prefer isolated modern metrics and fall back to historical legacy data."""
    for path in (MODERN_INPUT_FILE, LEGACY_INPUT_FILE):
        if path.exists() and path.stat().st_size > 0:
            return path
    raise FileNotFoundError(
        "No visibility data found. Run the visibility tracker before Effect Analyzer."
    )


def main() -> None:
    input_file = select_input_file()
    effect_df = build_effect_frame(pd.read_csv(input_file))
    effect_df.to_csv(OUTPUT_LOG, encoding="utf-8")

    plt.figure(figsize=(10, 6))
    for keyword in effect_df.columns:
        plt.plot(effect_df.index, effect_df[keyword], marker="o", label=keyword)

    plt.title("AIEO Effect Analyzer (Visibility Change Rate)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Effect % Change")
    if len(effect_df.columns):
        plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()
    print(f"✅ Chart saved as {CHART_FILE} from {input_file}")


if __name__ == "__main__":
    main()

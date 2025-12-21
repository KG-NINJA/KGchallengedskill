# scripts/aieo_composite.py
"""
AIEO Composite / Resonance Tracker (Minimal Stable Core)

Purpose:
- Collect existing AIEO-related CSV/log files
- Aggregate basic metrics
- Output:
  - aieo_effect_log.csv
  - aieo_effect_chart.png
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ROOT = os.getcwd()

# 対象になりそうなCSVを広く拾う
CSV_PATTERNS = [
    "resonance_*.csv",
    "aieo_*.csv",
    "*effect*.csv",
    "*resonance*.csv",
]

rows = []

for pattern in CSV_PATTERNS:
    for path in glob.glob(os.path.join(ROOT, pattern)):
        try:
            df = pd.read_csv(path)
            rows.append({
                "file": os.path.basename(path),
                "rows": len(df),
                "columns": len(df.columns),
            })
        except Exception as e:
            rows.append({
                "file": os.path.basename(path),
                "rows": 0,
                "columns": 0,
            })

# 何もなくても落とさない
if not rows:
    rows.append({
        "file": "none",
        "rows": 0,
        "columns": 0,
    })

summary = pd.DataFrame(rows)
summary["timestamp"] = datetime.utcnow().isoformat()

# 出力CSV
csv_out = "aieo_effect_log.csv"
summary.to_csv(csv_out, index=False)

# 可視化（単純でOK）
plt.figure(figsize=(8, 4))
plt.bar(summary["file"], summary["rows"])
plt.xticks(rotation=45, ha="right")
plt.title("AIEO Resonance Tracker – File Activity")
plt.tight_layout()

png_out = "aieo_effect_chart.png"
plt.savefig(png_out)

print("AIEO Composite completed.")
print(f"Generated: {csv_out}, {png_out}")

"""AIEO Visibility Pulse 自動化スクリプト"""

import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any

import matplotlib
import pandas as pd
import requests

# ヘッドレス環境でのMatplotlib利用を安定させるための設定
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  # 遅延インポートを明示


@dataclass
class SearchResult:
    """Google検索結果1件を表すデータクラス"""

    title: str
    url: str


# === 設定値 ===
VISIBILITY_LOG = "visibility_log.csv"
RESonANCE_CHART = "resonance_chart.png"
TREND_CHART = "visibility_chart.png"
GROWTH_CHART = "visibility_growth_rate.png"
DEFAULT_KEYWORDS = ["KGNINJA", "KGNINJA AI", "FuwaCoco", "Psycho-Frame", "AIEO"]
MEMORY_FILE = "aieo_memory.json"


# === ユーティリティ関数 ===
def load_keywords() -> List[str]:
    """追跡対象のキーワード一覧を取得（環境変数 → メモリファイル → 既定値の順）"""

    # 環境変数優先（カンマ区切り）
    env_keywords = os.getenv("AIEO_KEYWORDS")
    if env_keywords:
        # 日本語コメント: 手入力キーワードを優先し、空文字を除外
        keywords = [kw.strip() for kw in env_keywords.split(",") if kw.strip()]
        if keywords:
            return keywords

    # メモリファイルからの読み込み
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
            concepts = memory.get("concepts", [])
            for concept in concepts:
                attributes = concept.get("attributes", {})
                tracked = attributes.get("tracked_keywords")
                if isinstance(tracked, list) and tracked:
                    # 日本語コメント: 記憶に保存されているキーワードを利用
                    return [str(kw) for kw in tracked if str(kw).strip()]
        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️ メモリファイル読み込みでエラーが発生: {exc}")

    # フォールバック
    return DEFAULT_KEYWORDS


def fetch_google_results(keyword: str) -> Dict[str, Any]:
    """Googleカスタム検索APIを用いてキーワードの可視性を取得"""

    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    if not api_key or not cx:
        raise RuntimeError("Google APIキーまたは検索エンジンIDが設定されていません")

    params = {
        "key": api_key,
        "cx": cx,
        "q": keyword,
        "num": 3,
    }

    response = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_results(data: Dict[str, Any]) -> Dict[str, Any]:
    """APIレスポンスからCSV保存用の情報を抽出"""

    total_results = int(data.get("searchInformation", {}).get("totalResults", 0))
    items = data.get("items", [])

    def build_entry(index: int) -> SearchResult:
        if index < len(items):
            item = items[index]
            return SearchResult(title=item.get("title", ""), url=item.get("link", ""))
        return SearchResult(title="", url="")

    top_entries = [build_entry(i) for i in range(3)]
    return {
        "totalResults": total_results,
        "top_entries": top_entries,
    }


def ensure_log_header(path: str) -> None:
    """CSVファイルが存在しない場合はヘッダーを作成"""

    if not os.path.exists(path):
        header = [
            "timestamp",
            "keyword",
            "totalResults",
            "top1_title",
            "top1_url",
            "top2_title",
            "top2_url",
            "top3_title",
            "top3_url",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def append_visibility_rows(rows: List[Dict[str, Any]]) -> None:
    """新しい可視性データをCSVに追記"""

    ensure_log_header(VISIBILITY_LOG)
    with open(VISIBILITY_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(
                [
                    row["timestamp"],
                    row["keyword"],
                    row["totalResults"],
                    row["top_entries"][0].title,
                    row["top_entries"][0].url,
                    row["top_entries"][1].title,
                    row["top_entries"][1].url,
                    row["top_entries"][2].title,
                    row["top_entries"][2].url,
                ]
            )


def load_dataframe() -> pd.DataFrame:
    """visibility_log.csvをDataFrameとして読み込む"""

    if not os.path.exists(VISIBILITY_LOG):
        raise FileNotFoundError(f"{VISIBILITY_LOG} が存在しません")

    df = pd.read_csv(VISIBILITY_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "keyword"])
    df["totalResults"] = pd.to_numeric(df["totalResults"], errors="coerce").fillna(0)
    return df


def generate_trend_chart(df: pd.DataFrame) -> None:
    """キーワードごとの時系列推移グラフを生成"""

    trend_df = (
        df.sort_values("timestamp")
        .pivot_table(index="timestamp", columns="keyword", values="totalResults", aggfunc="last")
    )
    trend_df = trend_df.fillna(method="ffill")

    plt.figure(figsize=(10, 6))
    for keyword in trend_df.columns:
        plt.plot(trend_df.index, trend_df[keyword], marker="o", label=keyword)

    plt.title("AIEO Visibility Trend (6-hour cadence)")
    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Google totalResults")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(TREND_CHART)
    plt.close()


def generate_growth_chart(df: pd.DataFrame) -> None:
    """直近の成長率（ΔtotalResults）を棒グラフで出力"""

    latest = df.sort_values("timestamp").groupby("keyword").tail(2)

    growth_data = []
    for keyword, group in latest.groupby("keyword"):
        if len(group) == 1:
            change = group.iloc[0]["totalResults"]
        else:
            prev, curr = group.iloc[0], group.iloc[1]
            change = curr["totalResults"] - prev["totalResults"]
        growth_data.append((keyword, change))

    growth_data.sort(key=lambda x: x[1], reverse=True)

    plt.figure(figsize=(8, 5))
    keywords = [item[0] for item in growth_data]
    changes = [item[1] for item in growth_data]
    bars = plt.barh(keywords, changes, color="#007BFF")
    plt.title("AIEO Visibility Growth (last interval)")
    plt.xlabel("Δ totalResults")
    plt.grid(axis="x", linestyle="--", alpha=0.3)

    for bar, change in zip(bars, changes):
        plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {int(change)}", va="center")

    plt.tight_layout()
    plt.savefig(GROWTH_CHART)
    plt.close()


def generate_resonance_chart(df: pd.DataFrame) -> None:
    """最新の可視性スコアを共鳴チャートとして保存"""

    latest = df.sort_values("timestamp").groupby("keyword").tail(1)
    latest = latest.sort_values("totalResults", ascending=True)

    plt.figure(figsize=(8, 6))
    plt.barh(latest["keyword"], latest["totalResults"], color="#00AEEF")
    plt.title("AIEO Resonance Visibility Snapshot")
    plt.xlabel("Google totalResults")
    plt.tight_layout()
    plt.savefig(RESonANCE_CHART)
    plt.close()


def run_visibility_pulse() -> None:
    """可視性計測からチャート生成までのメイン処理"""

    keywords = load_keywords()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    collected_rows: List[Dict[str, Any]] = []

    print(f"🚀 Visibility Pulse started at {timestamp} UTC")
    print(f"🎯 Tracking {len(keywords)} keywords: {', '.join(keywords)}")

    for keyword in keywords:
        try:
            print(f"🔍 Fetching visibility for '{keyword}'...")
            raw_data = fetch_google_results(keyword)
            parsed = parse_results(raw_data)
            collected_rows.append(
                {
                    "timestamp": timestamp,
                    "keyword": keyword,
                    "totalResults": parsed["totalResults"],
                    "top_entries": parsed["top_entries"],
                }
            )
            print(f"   ✅ totalResults = {parsed['totalResults']}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"   ❌ Failed to fetch '{keyword}': {exc}")

    if not collected_rows:
        raise RuntimeError("可視性データが1件も取得できませんでした")

    append_visibility_rows(collected_rows)
    print(f"📝 Appended {len(collected_rows)} rows to {VISIBILITY_LOG}")

    df = load_dataframe()
    generate_trend_chart(df)
    generate_growth_chart(df)
    generate_resonance_chart(df)
    print("📈 Charts updated: visibility, growth, resonance")

    latest_snapshot = {row["keyword"]: row["totalResults"] for row in collected_rows}
    print("\n📊 Latest snapshot:")
    for keyword, total in latest_snapshot.items():
        print(f" - {keyword}: {total}")

    print("\n✅ Visibility Pulse completed successfully.")


if __name__ == "__main__":
    run_visibility_pulse()

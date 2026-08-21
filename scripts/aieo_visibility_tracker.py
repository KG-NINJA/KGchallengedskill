#!/usr/bin/env python3
"""AIEOの人物別可視性メトリクスを収集する。

リポジトリには別スキーマの旧版 ``visibility_log.csv`` も存在する。
人物別メトリクスは ``aieo_visibility_metrics.csv`` に分離し、
異なる形式のデータが同じCSVへ混入しないようにする。
"""

import csv
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX = os.getenv("GOOGLE_CX", "")

VISIBILITY_LOG = Path(
    os.getenv("AIEO_VISIBILITY_METRICS_LOG", "aieo_visibility_metrics.csv")
)
CONFIG_FILE = Path("config/users_to_track.json")
METRIC_FIELDS = [
    "timestamp",
    "name",
    "github_followers",
    "github_repos",
    "web_mentions",
    "domain_mentions",
    "visibility_score",
]


def utc_now_iso() -> str:
    """現在のUTC時刻をISO 8601形式で返す。"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class VisibilityTracker:
    """GitHub公開情報と検索結果から可視性メトリクスを収集する。"""

    def __init__(self) -> None:
        self.google_api_key = GOOGLE_API_KEY
        self.google_cx = GOOGLE_CX
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AIEO-Visibility-Tracker/1.0"})

    def search_google(self, query: str, num_results: int = 10) -> Dict:
        """Google Custom Searchから検索結果数を取得する。"""
        if not self.google_api_key or not self.google_cx:
            print("⚠ Google APIキーが設定されていません")
            return {"results": 0}

        try:
            response = self.session.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "num": min(num_results, 10),
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            total_results = int(
                data.get("queries", {})
                .get("request", [{}])[0]
                .get("totalResults", 0)
            )
            return {"results": total_results}
        except Exception as exc:
            print(f"⚠ Google Searchエラー: {exc}")
            return {"results": 0}

    def fetch_github_user(self, username: str) -> Dict:
        """GitHubユーザーの公開統計を取得する。"""
        try:
            response = self.session.get(
                f"https://api.github.com/users/{username}", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "public_repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0),
                    "public_gists": data.get("public_gists", 0),
                }
            print(f"⚠ GitHub APIがHTTP {response.status_code}を返しました")
        except Exception as exc:
            print(f"⚠ GitHub APIエラー: {exc}")
        return {}

    @staticmethod
    def calculate_visibility_score(
        github_repos: int,
        github_followers: int,
        web_mentions: int,
        domain_mentions: int,
    ) -> float:
        """各公開指標を0〜100の可視性スコアへ集約する。"""
        score = min((github_repos * 0.5) + github_followers, 50)
        if web_mentions > 0:
            score += min(math.log(web_mentions + 1) / math.log(10000), 1.0) * 30
        if domain_mentions > 0:
            score += min(math.log(domain_mentions + 1) / math.log(1000), 1.0) * 20
        return min(score, 100.0)

    def track_person(
        self, name: str, features: Dict, observed_at: str | None = None
    ) -> Dict:
        """1人分のメトリクスを共通観測時刻で収集する。"""
        print(f"\n📊 {name} を計測中...")
        metrics = {
            "name": name,
            "timestamp": observed_at or utc_now_iso(),
            "github_followers": 0,
            "github_repos": 0,
            "web_mentions": 0,
            "domain_mentions": 0,
            "visibility_score": 0.0,
        }

        github_username = features.get("github")
        if github_username:
            print(f"  • GitHub: @{github_username}")
            github_data = self.fetch_github_user(github_username)
            metrics["github_followers"] = github_data.get("followers", 0)
            metrics["github_repos"] = github_data.get("public_repos", 0)

        print(f"  • Web検索: '{name}'")
        metrics["web_mentions"] = self.search_google(f'"{name}"').get("results", 0)

        print("  • ドメイン言及を集計")
        metrics["domain_mentions"] = self._count_domain_mentions(name)
        metrics["visibility_score"] = self.calculate_visibility_score(
            metrics["github_repos"],
            metrics["github_followers"],
            metrics["web_mentions"],
            metrics["domain_mentions"],
        )
        print(f"  ✓ 可視性スコア: {metrics['visibility_score']:.1f}/100")
        return metrics

    def _count_domain_mentions(self, name: str) -> int:
        """主要ドメインでの検索結果数を合計する。"""
        total = 0
        for domain in ("github.com", "medium.com", "dev.to", "stackoverflow.com"):
            result = self.search_google(f'"{name}" site:{domain}', num_results=1)
            total += result.get("results", 0)
        return total


def load_users_config() -> List[Dict]:
    """追跡対象の設定を読み込む。"""
    if not CONFIG_FILE.exists():
        print(f"⚠ {CONFIG_FILE} が見つかりません")
        return []
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as exc:
        print(f"❌ JSON読み込みエラー: {exc}")
        return []
    return data if isinstance(data, list) else []


def _validate_existing_header(path: Path) -> None:
    """既存CSVが専用スキーマと一致することを確認する。"""
    if not path.exists() or path.stat().st_size == 0:
        return
    with path.open("r", encoding="utf-8", newline="") as file:
        header = next(csv.reader(file), [])
    if header != METRIC_FIELDS:
        raise ValueError(
            f"{path} のヘッダーが不正です: {header}; 期待値: {METRIC_FIELDS}"
        )


def save_visibility_log(metrics_list: List[Dict]) -> None:
    """旧版CSVへ触れず、人物別メトリクスだけを追記する。"""
    if not metrics_list:
        print("⚠ 保存する可視性データがありません")
        return

    _validate_existing_header(VISIBILITY_LOG)
    file_exists = VISIBILITY_LOG.exists() and VISIBILITY_LOG.stat().st_size > 0
    VISIBILITY_LOG.parent.mkdir(parents=True, exist_ok=True)

    with VISIBILITY_LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=METRIC_FIELDS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for metrics in metrics_list:
            writer.writerow({field: metrics.get(field, 0) for field in METRIC_FIELDS})

    print(f"\n✓ メトリクスを保存: {VISIBILITY_LOG}")


def main() -> None:
    """設定された全対象を同一観測時刻で計測する。"""
    print("=" * 60)
    print("AIEO Visibility Tracker")
    collection_timestamp = utc_now_iso()
    print(f"Started at: {collection_timestamp}")
    print("=" * 60)

    users = load_users_config()
    if not users:
        raise RuntimeError(f"追跡対象がありません: {CONFIG_FILE}")

    tracker = VisibilityTracker()
    all_metrics = [
        tracker.track_person(
            user.get("name", "Unknown"), user, observed_at=collection_timestamp
        )
        for user in users
    ]
    save_visibility_log(all_metrics)

    print("\n" + "=" * 60)
    print("✓ 可視性計測完了")
    print("=" * 60)


if __name__ == "__main__":
    main()

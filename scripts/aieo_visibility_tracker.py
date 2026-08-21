#!/usr/bin/env python3
"""AIEOの人物別可視性メトリクスを収集する。

リポジトリには別スキーマの旧版 ``visibility_log.csv`` も存在する。
人物別メトリクスは ``aieo_visibility_metrics.csv`` に分離し、
異なる形式のデータが同じCSVへ混入しないようにする。

外部プロバイダーの認証不足、quota超過、HTTP障害は検索結果0として
保存しない。失敗時は処理全体を停止し、直前の正常データを保持する。
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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

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


class ProviderError(RuntimeError):
    """外部データ提供元から信頼できる値を取得できなかったことを示す。"""


def utc_now_iso() -> str:
    """現在のUTC時刻をISO 8601形式で返す。"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_provider_message(response: requests.Response) -> str:
    """SecretやリクエストURLを含めず、APIエラー理由だけを返す。"""
    try:
        payload = response.json()
    except ValueError:
        return "応答本文がJSONではありません"

    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return "エラー理由を取得できません"

    parts = []
    status = error.get("status")
    message = error.get("message")
    details = error.get("errors")
    reason = None
    if isinstance(details, list) and details and isinstance(details[0], dict):
        reason = details[0].get("reason")

    for value in (status, reason, message):
        if value:
            text = str(value).replace("\n", " ").strip()
            if text and text not in parts:
                parts.append(text[:300])
    return " / ".join(parts) or "エラー理由を取得できません"


class VisibilityTracker:
    """GitHub公開情報と検索結果から可視性メトリクスを収集する。"""

    def __init__(self) -> None:
        self.google_api_key = GOOGLE_API_KEY
        self.google_cx = GOOGLE_CX
        self.github_token = GITHUB_TOKEN
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AIEO-Visibility-Tracker/1.1"})

    def search_google(self, query: str, num_results: int = 10) -> Dict:
        """Google Custom Searchから検索結果数を取得する。"""
        if not self.google_api_key or not self.google_cx:
            raise ProviderError(
                "Google Custom SearchのGOOGLE_API_KEYまたはGOOGLE_CXが設定されていません"
            )

        try:
            response = self.session.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "num": min(max(int(num_results), 1), 10),
                },
                timeout=15,
            )
        except requests.RequestException as exc:
            raise ProviderError(
                "Google Custom Searchへの接続に失敗しました "
                f"({type(exc).__name__})"
            ) from None

        if response.status_code != 200:
            reason = _safe_provider_message(response)
            raise ProviderError(
                f"Google Custom SearchがHTTP {response.status_code}を返しました: {reason}"
            )

        try:
            data = response.json()
        except ValueError:
            raise ProviderError("Google Custom Searchの成功応答がJSONではありません") from None

        search_information = data.get("searchInformation") if isinstance(data, dict) else None
        if not isinstance(search_information, dict) or "totalResults" not in search_information:
            raise ProviderError(
                "Google Custom Search応答にsearchInformation.totalResultsがありません"
            )

        try:
            total_results = int(search_information["totalResults"])
        except (TypeError, ValueError):
            raise ProviderError(
                "Google Custom SearchのtotalResultsが整数へ変換できません"
            ) from None

        if total_results < 0:
            raise ProviderError("Google Custom Searchが負の検索結果数を返しました")
        return {"results": total_results}

    def fetch_github_user(self, username: str) -> Dict:
        """GitHubユーザーの公開統計を取得する。"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        try:
            response = self.session.get(
                f"https://api.github.com/users/{username}",
                headers=headers,
                timeout=15,
            )
        except requests.RequestException as exc:
            raise ProviderError(
                f"GitHub APIへの接続に失敗しました ({type(exc).__name__})"
            ) from None

        if response.status_code != 200:
            raise ProviderError(f"GitHub APIがHTTP {response.status_code}を返しました")

        try:
            data = response.json()
            public_repos = int(data["public_repos"])
            followers = int(data["followers"])
            public_gists = int(data.get("public_gists", 0))
        except (KeyError, TypeError, ValueError):
            raise ProviderError("GitHub API応答に必要な公開統計がありません") from None

        if min(public_repos, followers, public_gists) < 0:
            raise ProviderError("GitHub APIが負の公開統計を返しました")
        return {
            "public_repos": public_repos,
            "followers": followers,
            "public_gists": public_gists,
        }

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
            metrics["github_followers"] = github_data["followers"]
            metrics["github_repos"] = github_data["public_repos"]

        print(f"  • Web検索: '{name}'")
        metrics["web_mentions"] = self.search_google(f'"{name}"')["results"]

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
            total += result["results"]
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
    try:
        all_metrics = [
            tracker.track_person(
                user.get("name", "Unknown"), user, observed_at=collection_timestamp
            )
            for user in users
        ]
    except ProviderError as exc:
        print(f"::error title=AIEO visibility provider error::{exc}")
        raise

    if all(
        metric["web_mentions"] == 0 and metric["domain_mentions"] == 0
        for metric in all_metrics
    ):
        print(
            "::warning title=Google visibility returned zero::"
            "API応答は成功しましたが、全対象のWeb・ドメイン言及が0でした。"
        )

    save_visibility_log(all_metrics)

    print("\n" + "=" * 60)
    print("✓ 可視性計測完了")
    print("=" * 60)


if __name__ == "__main__":
    main()

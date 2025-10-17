#!/usr/bin/env python3
"""
AIEO Visibility Tracker
可視性スコアを計測し、CSVログに記録
"""

import json
import os
import csv
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List

# Google Custom Search API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CX = os.getenv('GOOGLE_CX', '')

# ログファイル
VISIBILITY_LOG = Path("visibility_log.csv")
CONFIG_FILE = Path("config/users_to_track.json")

class VisibilityTracker:
    """可視性スコアを計測"""
    
    def __init__(self):
        self.google_api_key = GOOGLE_API_KEY
        self.google_cx = GOOGLE_CX
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AIEO-Visibility-Tracker/1.0'
        })
    
    def search_google(self, query: str, num_results: int = 10) -> Dict:
        """Google Custom Search で検索"""
        if not self.google_api_key or not self.google_cx:
            print("⚠ Google API キーが設定されていません")
            return {"results": 0}
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.google_api_key,
                'cx': self.google_cx,
                'num': min(num_results, 10)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            total_results = int(data.get('queries', {}).get('request', [{}])[0].get('totalResults', 0))
            return {"results": total_results}
        
        except Exception as e:
            print(f"⚠ Google Search エラー: {e}")
            return {"results": 0}
    
    def fetch_github_user(self, username: str) -> Dict:
        """GitHub API で公開情報を取得"""
        try:
            url = f"https://api.github.com/users/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "public_repos": data.get('public_repos', 0),
                    "followers": data.get('followers', 0),
                    "public_gists": data.get('public_gists', 0)
                }
            return {}
        
        except Exception as e:
            print(f"⚠ GitHub API エラー: {e}")
            return {}
    
    def calculate_visibility_score(self, 
                                  github_repos: int,
                                  github_followers: int,
                                  web_mentions: int,
                                  domain_mentions: int) -> float:
        """
        可視性スコアを計算（最大100点）
        
        GitHub: 50点
        Web言及: 30点
        ドメイン言及: 20点
        """
        score = 0.0
        
        # GitHub (最大50点)
        gh_score = (github_repos * 0.5) + (github_followers * 1.0)
        score += min(gh_score, 50)
        
        # Web言及 (最大30点)
        if web_mentions > 0:
            import math
            web_score = min(math.log(web_mentions + 1) / math.log(10000), 1.0) * 30
            score += web_score
        
        # ドメイン言及 (最大20点)
        if domain_mentions > 0:
            import math
            domain_score = min(math.log(domain_mentions + 1) / math.log(1000), 1.0) * 20
            score += domain_score
        
        return min(score, 100.0)
    
    def track_person(self, name: str, features: Dict) -> Dict:
        """人物の可視性を計測"""
        print(f"\n📊 {name} を計測中...")
        
        metrics = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "github_followers": 0,
            "github_repos": 0,
            "web_mentions": 0,
            "domain_mentions": 0,
            "visibility_score": 0.0
        }
        
        # GitHub情報を取得
        if features.get('github'):
            print(f"  • GitHub: @{features['github']}")
            github_data = self.fetch_github_user(features['github'])
            metrics["github_followers"] = github_data.get('followers', 0)
            metrics["github_repos"] = github_data.get('public_repos', 0)
        
        # Web全体での言及を検索
        print(f"  • Web検索: '{name}'")
        web_results = self.search_google(f'"{name}"')
        metrics["web_mentions"] = web_results.get('results', 0)
        
        # 人気ドメインでの言及を集計
        print(f"  • ドメイン言及を集計")
        domain_count = self._count_domain_mentions(name)
        metrics["domain_mentions"] = domain_count
        
        # スコアを計算
        metrics["visibility_score"] = self.calculate_visibility_score(
            metrics["github_repos"],
            metrics["github_followers"],
            metrics["web_mentions"],
            metrics["domain_mentions"]
        )
        
        print(f"  ✓ 可視性スコア: {metrics['visibility_score']:.1f}/100")
        
        return metrics
    
    def _count_domain_mentions(self, name: str) -> int:
        """人気ドメインでの言及数を集計"""
        domains = ['github.com', 'medium.com', 'dev.to', 'stackoverflow.com']
        total = 0
        
        for domain in domains:
            try:
                result = self.search_google(f'"{name}" site:{domain}', num_results=1)
                mentions = result.get('results', 0)
                total += mentions
            except:
                pass
        
        return total


def load_users_config() -> List[Dict]:
    """追跡対象ユーザーを読み込む"""
    if not CONFIG_FILE.exists():
        print(f"⚠ {CONFIG_FILE} が見つかりません")
        return []
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON読み込みエラー: {e}")
        return []


def save_visibility_log(metrics_list: List[Dict]) -> None:
    """可視性ログをCSVに追記"""
    try:
        file_exists = VISIBILITY_LOG.exists()
        
        with open(VISIBILITY_LOG, 'a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'name', 'github_followers', 'github_repos',
                'web_mentions', 'domain_mentions', 'visibility_score'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # ヘッダーがなければ書き込み
            if not file_exists:
                writer.writeheader()
            
            # データを追記
            for metrics in metrics_list:
                writer.writerow(metrics)
        
        print(f"\n✓ ログを保存: {VISIBILITY_LOG}")
    
    except Exception as e:
        print(f"❌ CSV保存エラー: {e}")


def main():
    print("=" * 60)
    print("AIEO Visibility Tracker")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 設定ファイルから追跡対象を読み込む
    users = load_users_config()
    
    if not users:
        print("⚠ 追跡対象ユーザーが設定されていません")
        print(f"   {CONFIG_FILE} を作成してください")
        return
    
    # トラッカーを初期化
    tracker = VisibilityTracker()
    
    # 各ユーザーの可視性を計測
    all_metrics = []
    for user in users:
        name = user.get('name', 'Unknown')
        metrics = tracker.track_person(name, user)
        all_metrics.append(metrics)
    
    # ログに保存
    save_visibility_log(all_metrics)
    
    print("\n" + "=" * 60)
    print("✓ 可視性計測完了")
    print("=" * 60)


if __name__ == "__main__":
    main()

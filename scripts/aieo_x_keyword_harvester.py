import os
import json
import re
import time
import feedparser
from datetime import datetime, timedelta
from typing import List, Set, Dict, Optional, Tuple

# Nitter インスタンス（複数のフォールバック）
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.unixfox.eu",
    "https://nitter.1d4.us"
]

# あなたのXユーザー名
X_USERNAME = "FuwaCocoOwnerKG"  # ← あなたのアカウント名に変更

# ファイルパス
MEMORY_FILE = "aieo_memory.json"
HARVESTED_KEYWORDS_FILE = "x_harvested_keywords.json"
CACHE_FILE = "x_posts_cache.json"
ERROR_LOG_FILE = "x_harvest_errors.log"

# 設定
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
REQUEST_TIMEOUT = 10  # 秒
CACHE_EXPIRY_DAYS = 7


class XKeywordHarvester:
    """XポストからAIEO用キーワードを抽出（堅牢版）"""
    
    def __init__(self, username: str):
        self.username = username
        self.harvested = self._load_harvested()
        self.error_log = []
    
    def _load_harvested(self) -> Dict:
        """既に取り込み済みのキーワードを読み込み"""
        if os.path.exists(HARVESTED_KEYWORDS_FILE):
            try:
                with open(HARVESTED_KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                self._log_error(f"Failed to load harvested keywords: {e}")
                return self._init_harvested_structure()
        return self._init_harvested_structure()
    
    def _init_harvested_structure(self) -> Dict:
        """初期化されたデータ構造を返す"""
        return {
            "keywords": [],
            "hashtags": [],
            "last_harvest": None,
            "total_posts_processed": 0,
            "harvest_history": []
        }
    
    def _save_harvested(self):
        """取り込み済みキーワードを保存"""
        try:
            with open(HARVESTED_KEYWORDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.harvested, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log_error(f"Failed to save harvested keywords: {e}")
    
    def _load_cache(self) -> Optional[List[Dict]]:
        """キャッシュからポストを読み込み"""
        if not os.path.exists(CACHE_FILE):
            return None
        
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # キャッシュの有効期限チェック
            cache_date = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_date > timedelta(days=CACHE_EXPIRY_DAYS):
                print("⏰ Cache expired")
                return None
            
            print(f"📦 Loaded {len(cache_data['posts'])} posts from cache")
            return cache_data['posts']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self._log_error(f"Failed to load cache: {e}")
            return None
    
    def _save_cache(self, posts: List[Dict]):
        """ポストをキャッシュに保存"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'posts': posts
            }
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cached {len(posts)} posts")
        except Exception as e:
            self._log_error(f"Failed to save cache: {e}")
    
    def _log_error(self, message: str):
        """エラーログを記録"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.error_log.append(log_entry)
        print(f"❌ {message}")
        
        try:
            with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass  # ログ記録失敗は無視
    
    def fetch_recent_posts(self, days: int = 7) -> List[Dict]:
        """最近のポストをRSS経由で取得（堅牢版）"""
        
        # まずキャッシュを試す
        cached_posts = self._load_cache()
        if cached_posts:
            return cached_posts
        
        print(f"🔍 Fetching posts from X (last {days} days)...")
        
        # 各Nitterインスタンスを試す
        for attempt, instance in enumerate(NITTER_INSTANCES, 1):
            print(f"   Attempt {attempt}/{len(NITTER_INSTANCES)}: {instance}")
            
            posts = self._fetch_from_instance(instance, days)
            
            if posts:
                # 成功したらキャッシュして返す
                self._save_cache(posts)
                return posts
            
            # 失敗したら少し待つ
            if attempt < len(NITTER_INSTANCES):
                time.sleep(RETRY_DELAY)
        
        # すべて失敗した場合、古いキャッシュでも使う
        print("⚠️ All instances failed, trying expired cache...")
        expired_cache = self._load_expired_cache()
        if expired_cache:
            print(f"📦 Using expired cache ({len(expired_cache)} posts)")
            return expired_cache
        
        self._log_error("All fetch attempts failed, no cache available")
        return []
    
    def _fetch_from_instance(self, instance: str, days: int) -> List[Dict]:
        """特定のNitterインスタンスから取得"""
        try:
            rss_url = f"{instance}/{self.username}/rss"
            
            # User-Agentを設定してブロックを回避
            feed = feedparser.parse(rss_url, agent='Mozilla/5.0')
            
            if not feed.entries:
                return []
            
            posts = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries:
                try:
                    # 日付パース
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    else:
                        # 日付がない場合は現在時刻
                        pub_date = datetime.now()
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    posts.append({
                        'title': entry.get('title', ''),
                        'content': entry.get('summary', ''),
                        'date': pub_date.isoformat(),
                        'link': entry.get('link', ''),
                        'source_instance': instance
                    })
                    
                except Exception as e:
                    self._log_error(f"Failed to parse entry: {e}")
                    continue
            
            if posts:
                print(f"   ✅ Found {len(posts)} posts")
                return posts
            
        except Exception as e:
            self._log_error(f"Failed to fetch from {instance}: {e}")
        
        return []
    
    def _load_expired_cache(self) -> Optional[List[Dict]]:
        """期限切れでもキャッシュを読み込む（緊急用）"""
        if not os.path.exists(CACHE_FILE):
            return None
        
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return cache_data.get('posts', [])
        except:
            return None
    
    def extract_keywords(self, posts: List[Dict]) -> Set[str]:
        """ポストからキーワードを抽出"""
        keywords = set()
        
        # パターン定義
        hashtag_pattern = re.compile(r'#(\w+)')
        proper_noun_pattern = re.compile(r'\b([A-Z][a-zA-Z]{2,}(?:[A-Z][a-z]+)*)\b')
        japanese_pattern = re.compile(r'[ァ-ヶー]{2,}|[一-龯]{2,}')
        url_pattern = re.compile(r'https?://\S+')
        
        for post in posts:
            # URLを除去
            text = url_pattern.sub('', post['content'])
            
            # ハッシュタグ抽出
            hashtags = hashtag_pattern.findall(text)
            for tag in hashtags:
                if 2 < len(tag) < 30:  # 長さ制限
                    keywords.add(f"#{tag}")
                    if tag not in self.harvested["hashtags"]:
                        self.harvested["hashtags"].append(tag)
            
            # 固有名詞抽出（英語）
            proper_nouns = proper_noun_pattern.findall(text)
            for noun in proper_nouns:
                # 除外リスト
                if noun in ['This', 'That', 'From', 'With', 'Have', 'Will', 'Been']:
                    continue
                if 3 < len(noun) < 30:
                    keywords.add(noun)
            
            # 日本語キーワード抽出
            japanese_words = japanese_pattern.findall(text)
            for word in japanese_words:
                if 2 < len(word) < 20:
                    keywords.add(word)
        
        return keywords
    
    def filter_relevant_keywords(self, keywords: Set[str]) -> List[str]:
        """AIEO関連のキーワードのみをフィルタ"""
        
        # 除外リスト（一般的すぎる語）
        exclude = {
            'RT', 'Twitter', 'Tweet', 'Follow', 'Like', 'Share', 'Click',
            'Link', 'Post', 'Reply', 'Retweet', 'Comment', 'Thread',
            'ツイート', 'リツイート', 'フォロー', 'いいね', 'リプ'
        }
        
        # 優先リスト（必ず取り込む）
        priority_keywords = {
            # 固有名詞
            'KGNINJA', 'AIEO', 'PsychoFrame', 'NOROSHI', 'FuwaCoco',
            'AutoKaggler', 'SceneMixer',
            
            # プラットフォーム
            'Kaggle', 'GitHub', 'Fiverr',
            
            # 技術スタック
            'Python', 'JavaScript', 'n8n', 'Claude', 'ChatGPT',
            'Windsurf', 'Devin', 'OpenHands',
            
            # コンセプト
            'AIEO', 'Beacon', 'Pulse', 'Resonance', 'Memory',
            
            # 成果
            'OpenAI', 'Challenge', 'Hackathon', 'Competition'
        }
        
        filtered = []
        
        for kw in keywords:
            # 除外リストチェック
            if kw in exclude or kw.lower() in [e.lower() for e in exclude]:
                continue
            
            # 優先リストは必ず追加
            if kw in priority_keywords or kw.lower() in [p.lower() for p in priority_keywords]:
                filtered.append(kw)
                continue
            
            # ハッシュタグは基本的に取り込む
            if kw.startswith('#'):
                filtered.append(kw)
                continue
            
            # 既存のメモリに含まれているかチェック
            if self._is_already_in_memory(kw):
                continue
            
            # 長さチェック
            if 3 <= len(kw) <= 30:
                filtered.append(kw)
        
        # 重複削除して返す
        return list(set(filtered))
    
    def _is_already_in_memory(self, keyword: str) -> bool:
        """既にメモリに存在するキーワードか"""
        existing = [k.lower() for k in self.harvested["keywords"]]
        return keyword.lower() in existing
    
    def update_memory(self, keywords: List[str], posts_count: int):
        """AIEOメモリに新しいキーワードを追加"""
        
        # メモリファイルを読み込み
        if not os.path.exists(MEMORY_FILE):
            print("⚠️ aieo_memory.json not found, will be created by memory engine")
            return
        
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        except json.JSONDecodeError as e:
            self._log_error(f"Failed to load memory: {e}")
            return
        
        # 新規キーワードのみ抽出
        new_keywords = [kw for kw in keywords if kw not in self.harvested["keywords"]]
        
        if not new_keywords and not keywords:
            print("📭 No new keywords to add")
            return
        
        # 履歴に追加
        self.harvested["keywords"].extend(new_keywords)
        self.harvested["last_harvest"] = datetime.now().isoformat()
        self.harvested["total_posts_processed"] += posts_count
        
        # 今回の収穫を記録
        harvest_record = {
            "timestamp": datetime.now().isoformat(),
            "posts_processed": posts_count,
            "new_keywords_count": len(new_keywords),
            "new_keywords": new_keywords[:10]  # 最初の10件のみ
        }
        self.harvested["harvest_history"].append(harvest_record)
        
        # 履歴が長すぎる場合は古いものを削除（最新30件のみ保持）
        if len(self.harvested["harvest_history"]) > 30:
            self.harvested["harvest_history"] = self.harvested["harvest_history"][-30:]
        
        # X由来のキーワード概念を検索
        x_concept_idx = None
        for i, concept in enumerate(memory["concepts"]):
            if concept["concept_id"] == "kg_x_keyword_evolution":
                x_concept_idx = i
                break
        
        # メモリ概念を更新
        concept_data = {
            "concept_id": "kg_x_keyword_evolution",
            "category": "dynamic_vocabulary",
            "attributes": {
                "harvested_keywords": list(set(self.harvested["keywords"]))[-50:],  # 最新50件（重複排除）
                "total_unique_keywords": len(set(self.harvested["keywords"])),
                "recent_hashtags": list(set(self.harvested["hashtags"]))[-20:],
                "last_harvest": self.harvested["last_harvest"],
                "total_posts_analyzed": self.harvested["total_posts_processed"],
                "harvest_count": len(self.harvested["harvest_history"]),
                "source": "X (Twitter) timeline via RSS"
            },
            "confidence": min(0.95, 0.7 + (len(self.harvested["harvest_history"]) * 0.01)),
            "last_updated": datetime.now().isoformat()
        }
        
        if x_concept_idx is not None:
            memory["concepts"][x_concept_idx] = concept_data
            print(f"📝 Updated existing X keyword concept")
        else:
            memory["concepts"].append(concept_data)
            print(f"✨ Created new X keyword concept")
        
        # メモリを保存
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
            print(f"✅ Memory updated successfully")
        except Exception as e:
            self._log_error(f"Failed to save memory: {e}")
        
        # 収穫データを保存
        self._save_harvested()
        
        # 新規キーワードを表示
        if new_keywords:
            print(f"\n🎯 Added {len(new_keywords)} new keywords:")
            display_count = min(15, len(new_keywords))
            for kw in new_keywords[:display_count]:
                print(f"   - {kw}")
            if len(new_keywords) > display_count:
                print(f"   ... and {len(new_keywords) - display_count} more")
    
    def generate_summary(self) -> str:
        """収穫サマリーを生成"""
        total_keywords = len(set(self.harvested["keywords"]))
        total_hashtags = len(set(self.harvested["hashtags"]))
        total_posts = self.harvested["total_posts_processed"]
        harvests = len(self.harvested["harvest_history"])
        
        summary = f"""
╔════════════════════════════════════════════════════════╗
║         🐦 X KEYWORD HARVEST SUMMARY                   ║
╠════════════════════════════════════════════════════════╣
║ Total Unique Keywords: {total_keywords:>4}                          ║
║ Total Hashtags:        {total_hashtags:>4}                          ║
║ Total Posts Analyzed:  {total_posts:>4}                          ║
║ Harvest Count:         {harvests:>4}                          ║
║ Last Harvest:          {self.harvested['last_harvest'][:19] if self.harvested['last_harvest'] else 'Never':>19} ║
╚════════════════════════════════════════════════════════╝
"""
        return summary


def main():
    """メイン処理"""
    print("="*60)
    print("🐦 AIEO X Keyword Harvester (Robust Edition)")
    print("="*60)
    
    # 初期化
    harvester = XKeywordHarvester(X_USERNAME)
    
    # ポスト取得
    print(f"\n📡 Fetching posts for @{X_USERNAME}...")
    posts = harvester.fetch_recent_posts(days=7)
    
    if not posts:
        print("\n⚠️ No posts found")
        print("   Possible reasons:")
        print("   - All Nitter instances are down")
        print("   - No recent posts in the last 7 days")
        print("   - Username might be incorrect")
        print("\n💡 System will retry on next scheduled run")
        
        # エラーログがあれば表示
        if harvester.error_log:
            print("\n📋 Error Log:")
            for log in harvester.error_log[-5:]:  # 最新5件
                print(f"   {log}")
        
        return
    
    print(f"✅ Successfully fetched {len(posts)} posts")
    
    # キーワード抽出
    print(f"\n🔍 Extracting keywords...")
    raw_keywords = harvester.extract_keywords(posts)
    print(f"   Found {len(raw_keywords)} raw keywords")
    
    # フィルタリング
    print(f"\n🎯 Filtering relevant keywords...")
    filtered = harvester.filter_relevant_keywords(raw_keywords)
    print(f"   Filtered to {len(filtered)} relevant keywords")
    
    # メモリ更新
    print(f"\n🧠 Updating AIEO memory...")
    harvester.update_memory(filtered, len(posts))
    
    # サマリー表示
    print(harvester.generate_summary())
    
    print("="*60)
    print("✅ X Keyword Harvest Complete")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

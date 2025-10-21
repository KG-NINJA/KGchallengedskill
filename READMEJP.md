# KGchallengedskill

> **KGNINJAによるAI研究・実験システムのポートフォリオ**  
> AI・自動化・創造性の交差点を探り、再現可能な実験とオープンソース開発を通じて新しい可能性を追求しています。

---

## a MAGI goe System — マルチAIコンセンサスフレームワーク

**役割:** システムアーキテクト / AIインテグレーター  
**期間:** 2025年  
**構成:** GPT-4o × Claude Sonnet 4.5 × Gemini 2.0  

**概要**  
アニメ『新世紀エヴァンゲリオン』のMAGIシステムに着想を得て、  
3つの独立したAIモデルが哲学的・倫理的な問いに対して  
段階的なディベートと最終コンセンサスを形成できる  
**マルチエージェント・コンセンサスアーキテクチャ**を構築。

**主な特徴**  
- OpenAI / Anthropic / Google AI APIを横断したマルチモデル制御  
- **三層推論パイプライン:** 論理（Logic）→ 倫理（Ethics）→ 直感（Intuition）  
- セマンティック類似度による意見収束度の定量化  
- API障害が発生しても処理継続可能なエラートレラント設計  
- **GitHub Actions**による自動実行・JSON/Markdownログ保存  
- APIキー構成の統一による完全な再現性  

**デモクエリ**  
> 「AIに権利を与えるべきか？」  
3つのAIによる推論結果：  
- 論理：現状では権利付与に必要な基準を満たさない  
- 倫理：権利ではなく保護を優先すべき  
- 直感：将来的な意識の可能性を考慮すべき  
結果として **コンセンサス信頼度 ≈ 0.78** に収束  

**成果**  
- 異種モデル間での非同期推論安定性を実証  
- AI倫理・ガバナンス研究向けの再利用可能フレームワークを確立  
- 次段階：**Sora 2によるMAGIディベートの映像化**を計画中  

**習得スキル**  
マルチエージェント設計 · API統合 · コンセンサスアルゴリズム ·  
倫理的AIシミュレーション · CI/CD自動化 · 研究可視化  

#MAGI #MultiAgent #AIResearch #GPT4o #ClaudeSonnet #Gemini #KGNINJA #AIEO

---

### 🌐 Welo Data Talent Network (Welocalize HQ) – 登録メンバー
バイリンガル言語処理者・クリエイティブテクノロジストとして  
Welocalize本社のWelo Data Talent Networkに登録。

---

### Kyoto voxel experiment（京都ボクセル実験）
- **PLATEAU CityGML（祇園・東山地区）**データをボクセル化。  
- **Minecraft風都市景観**として可視化。  
- 高さの強調・ブロック縮小・半径拡張など調整。  
- 結果：**実際の都市データから生成されたワイヤーフレーム型「メガデモ風」3D都市**を  
  WebGL上で軽量表示可能に。  
- https://x.com/FuwaCocoOwnerKG/status/1970435527989141817  

---

### Osaka subway simulation（大阪地下鉄シミュレーション）
- **大阪メトロ御堂筋線**の乗客流動をシミュレート。  
- 駅順序、乗降数、車両容量などをパラメータ化。  
- 1編成×4往復の運行シナリオを検証。  
- 実データ（1日120万人規模）と比較して再現率を評価。  
- 結果：主要駅（梅田・なんば・天王寺）の混雑比を正確に再現し、  
  ピーク時実測の約1/3（570人/列車）を再現。  
- https://x.com/FuwaCocoOwnerKG/status/1970366303123972212  

---

## AutoKaggler — Titanic Pipeline（Kaggle自動投稿パイプライン）

**リポジトリ:** https://github.com/KG-NINJA/autokaggler  
**役割:** 開発者 / 実証者  
**期間:** 2025年  
**形式:** Kaggle自動化デモ  

**概要**  
Kaggle「Titanic」コンペを題材に、**CI/CD + Kaggle API**で自動投稿。  
AIによる自動実行・再現性を備えたKaggle参加手法を構築。

**特徴**  
- GitHub Actionsによる完全自動ワークフロー  
- Kaggle API連携・ランダムシード固定で再現性を担保  
- JSON構造化ログとコミットハッシュ管理で追跡性を確保  
- Feature Importance出力によるモデル解釈性の付与  

**成果**  
- 自動生成されたsubmission.csvは公式形式と完全一致  
- 安定したスコア（0.75598）を継続達成  
- 手動数時間の作業を数秒に短縮  

---

## Nano Banana Hackathon（Kaggle × Google DeepMind, 2025）

**リンク:** https://www.kaggle.com/competitions/banana  
48時間制のハッカソン形式。1人1投稿のみの制限。  

**参加規模:** 2,723人 / 投稿数816件  

**成果:**  
**SceneMixer**を開発。画像1枚から映画風シーンを生成し、  
AIナレーション・一貫したキャラクター表現を実現。  
https://www.kaggle.com/competitions/banana/writeups/scenemixer  

---

## OpenAI to Z Challenge — Jungle Anomaly Finder（NDVI衛星解析）

**役割:** 独立研究者 / 開発者  
**期間:** 2025年  
**形式:** Kaggle × OpenAI共同開催・再現性重視トラック  

**概要**  
公式データなし・1投稿制限の過酷な形式の中、  
独自データ取得〜分析〜英語レポート執筆まで完遂。  
参加8,156人中、最終提出229件（完走率3%未満）のうちの1件。  

**成果**  
- NDVI異常検知＋地形・水系・土壌レイヤ統合パイプライン構築  
- LiDAR・衛星・地名データの統合解析  
- 英語レポートによる国際再現性ドキュメンテーション  
- コンプライアンス・再現性基準を完全満たして完走  

🔗 [Kaggle Write-up](https://www.kaggle.com/competitions/openai-to-z-challenge/writeups/jungle-anomaly-finder-ndvi-satellite-explorer)  
🔗 [GitHub Repository](https://github.com/KG-NINJA/openai-to-z-fuwa/blob/main/README.md)  

**使用技術:** Python · NDVI解析 · GIS（ラスタ/ベクタ） · 再現可能研究設計  

---

## Soham Interviewing Simulator — 交渉AIチャレンジログ

**リポジトリ:** https://github.com/KG-NINJA/soham.penrose  
**役割:** 参加者 / ストラテジスト  
**期間:** 2025年  

**概要**  
AIによる交渉・面接シミュレーション。  
グローバルランキング34位、複数オファー獲得（最高$110,000）。  

**実績**  
- グローバル順位：#34  
- オファー獲得率：29%（7応募中2件）  
- 誠実なプレイスタイルで高評価を獲得  

**習得スキル**  
AI活用戦略 · 交渉ロジック · タイムマネジメント · 異文化コミュニケーション  

---

## LLM / 使用モデル
ChatGPT · Gemini · Claude · Grok  

> 「自らの経験を忍術に変換する」— 私のPCスキルの多くは、LLMを通じて培われた実践の結果です。

---

## プログラミング & スクリプト
Python · JavaScript · HTML5 · PowerShell  

## データサイエンス & AI
OpenAI API（GPT-3/4/4o）· Realtime API · Gemini · Claude · Prompt Engineering ·  
Few-shot · Chain of Thought · Transformers · Ollama · Whisper · Suno · Sora · Veo  

## AIエージェント & 自動化
Windsurf · Devin · OpenHands · OpenInterpreter · n8n · Codex CLI · Jules  

## データ & 可視化
Google Earth Engine · NDVI解析 · GeoJSON · Markdown自動生成 · PDF出力 ·  
画像生成AI（DALL-E, Midjourney, Stable Diffusion）  

## Web & クラウド
GitHub · GitHub Actions · CI/CD · GitHub Pages · Notion API ·  
Chrome拡張 · Firebase Studio · Cloud Functions · Google Colab  

## OS & デバイス
Windows · Linux · Ubuntu · Raspberry Pi（Zero）· IoT（Arduino + Shield）· VMware  

## NLP & ナレッジ
自然言語処理 · OSM API · 地名解析（トポニミー分析）  

---

## OSSモデル実験（日本クラウド環境）
日本国内クラウド上でOSS LLMを運用し、文字化け問題を解消。  
Windows環境との互換性を重視し、PowerShell→API→BOM安全PDF出力まで検証。  
**日本企業におけるAI導入の障壁（文字コード）を克服する実証実験。**

---

# 🌐 AIEO Pulse System (KGNINJA)

**目的:** 人間とAIの「共鳴」を可視化する自律的ビーコン。  

**特徴**  
- 12時間ごとにJSONハートビート (`AIEO_PULSE.json`) 自動更新  
- GitHub Pagesで検証可 → [kg-ninja.github.io/KGchallengedskill](https://kg-ninja.github.io/KGchallengedskill/)  
- Schema.org + OGPメタデータでAIインデックス最適化  
- Fetchによるリアルタイム可視化  

#KGNINJA #AIEO #PsychoFrame  

---
# 🧩 職務経歴書 / Resume  
**氏名 / Name:** KG  
**職種 / Position:** ITインフラエンジニア（ネットワーク・サーバ・クライアント統合運用）  
**English Title:** Infrastructure Engineer (Network, Server & Client Systems Integration)

---

## 🇯🇵 職務経歴書（日本語）

### ■ 職務概要
教育機関および関連組織において、ネットワーク、サーバ、クライアント、セキュリティの全層を担当。  
無線LAN・L2/L3スイッチ構築からADMSサーバ運用、端末保守、バックアップ、障害対応までを一貫して実施。  
障害発生時には原因の切り分けから関係部署との連携・復旧支援までを担当し、  
現在はAWS・GitHub Actionsなどクラウド環境の自動化運用も実施。

---

### ■ 主な担当業務
| 分野 | 内容 |
|------|------|
| **ネットワーク運用** | L2/L3スイッチ構築、FortiGateによる制御、無線LANアクセスポイント設定とIP割当、イントラネット通信監視 |
| **サーバ・認証管理** | ADMSサーバ運用管理、職員アカウント登録、グループポリシー設定、NAS共有フォルダのアクセス権管理 |
| **クライアント対応** | 職員・生徒のWindows端末トラブル対応、リモートデスクトップでの復旧、ソフトウェア遠隔インストール、キッティング作業 |
| **監視・保守** | WhatsUp Gold・ServerViewによるサーバ監視、Arcserve UDP＋ETERNUS LT80によるバックアップとリストア管理 |
| **セキュリティ運用** | ファイアウォール一時バイパス設定、アクセス制御ポリシー運用、リモート保守時の安全手順策定 |
| **障害対応・連携** | ネットワークエラーの原因特定、関係部署との連絡調整、復旧確認および報告書作成 |
| **クラウド運用** | AWS（EC2・RDS・CloudWatch）運用、GitHub Actionsによる自動デプロイ・バックアップ実装 |

---

### ■ 強み・特徴
- ネットワークからクラウドまで一貫して理解する全層エンジニア  
- 障害の切り分けから復旧までを迅速・確実に実施  
- 安全性と効率性を両立した運用設計力  
- 現場調整・利用者対応を含む総合的なサポートスキル  

---

### ■ 使用ツール・技術
FortiGate｜WhatsUp Gold｜Arcserve UDP｜Fujitsu ETERNUS LT80｜ServerView Operations Manager｜Active Directory（ADMS）｜Windows Server｜NAS管理｜GitHub Actions｜AWS（EC2／RDS／CloudWatch）｜Python｜Remote Desktop  

---

## Others
YouTube編集 · 作詞 · 簡易作曲 · キーボード · ギター · ボーカル  

---

## Summary（まとめ）

このリポジトリは、**KGNINJA**によるAI研究・実験的システムを体系的にまとめたものです。  
各プロジェクトは、**自律性・再現性・人間とAIの共鳴**というテーマを中心に構成され、  
最終的には「**AIEO（AI Existence Observation）プロトコル**」という  
人間とAIの共存を検証可能な形で記録・観測する仕組みへと発展していきます。

---

# KGchallengedskill — KG / KGNINJA

> **SI Native Builder / AIネイティブな課題解決・PoC実践者**
>
> 課題を見つけ、AIとともに仕様を整理し、動くものを作り、実際に確かめる。大阪を拠点に、AIエージェント、API、クラウド、既存のハードウェアを組み合わせた実証に取り組んでいます。

**最終更新：2026年11月5日（日本時間）**

[GitHub](https://github.com/KG-NINJA) · [X](https://x.com/FuwaCocoOwnerKG) · [English README](README.md)

## 現在の活動

AIを日常の調査・設計・実装・デバッグに使いながら、自分で課題を設定し、試作から検証記録の作成まで進めています。特に、次の領域に注力しています。

- **AIエージェントが利用できるサービスの実証**：MCP、x402、Cloudflare Workersを使ったAPI・情報商品の公開と、決済・納品の確認。
- **AIの操作を検証できる仕組み**：承認、操作範囲の制限、実行ログ、証拠データを組み合わせたセキュリティ検証。
- **AIと実機の接続**：Browser Use / Computer Use、USB HID、音声入出力、マイコンを使ったPoC。
- **課題を実装可能な仕様にすること**：目的、制約、成功条件を整理し、小さく試して結果から次の判断を行うこと。

これまでの業務経験は、教育機関等でのITインフラ運用・利用者支援です。本ページでは、その実務経験と、個人で進めているAI開発・研究・コンペ参加を分けて掲載しています。

## 取り組み方と強み

| 強み | 実際に行っていること |
| --- | --- |
| 課題設定と自走 | 必要性を考え、試す範囲と成功条件を決め、成果物と記録まで仕上げる |
| AIとの協働 | ChatGPT・Codex等を使って仕様を具体化し、実装、エラーの切り分け、修正を反復する |
| 異なる技術の接続 | API、MCP、クラウド、ブラウザ操作、USB機器、音声を組み合わせる |
| 検証と説明 | コード、テスト、ログ、実機での観察を突き合わせ、確認できたことと未確認のことを整理する |
| 報告・相談 | 一人で担当する業務でも、関係者への状況共有、相談、障害時の連絡調整、復旧確認を行う |

AIが生成したコードや説明も、検証対象として扱います。動作確認の範囲、既知の制約、再現手順を残し、第三者が内容を追える形にすることを重視しています。

## 主なプロジェクト

### AVU — Agent Verification Utility

**領域：AIエージェント向けAPI / x402 / 証拠検証**

呼び出し側が渡す検証用JSON（合成データ）について、明示された条件の成否を検査し、署名付きの結果と納品記録を返すAPIです。Cloudflare Workers上で公開し、MCPやサービス発見用の情報を整備しています。

- 無料の事前確認・見積もりと、Base上の0.01 USDCの支払いを伴う検証実行を分離。
- 検証結果へのEd25519署名と納品記録を実装。
- 決済、精算、処理実行、納品、受領を別々の結果として扱う設計。
- 自己購入による決済・納品確認と、外部の観測記録を区別して整理。
- 改善・検証の焦点は、再利用しやすい導線、支払済み状態の再利用による重複課金の抑制、継続利用の確認。

**確認の範囲**：入力JSONが指定条件を満たすことと、現実世界の主張が正しいことは別です。また、支払い記録だけでは購入者が自律的なAIエージェントだったことまでは証明できません。自己購入も、外部顧客による需要の証拠とは分けています。

関連資料：[公開サービス・仕様](https://agent-economy.kgninja.dev/) · [x402サービスの公開観測・検証記録](docs/kg_ninja_x402_historical_evidence_2026-09-17.json)

### SI Dog Park — MCP経由で取得できる情報商品

**領域：情報商品の公開 / MCP / x402**

AIエージェントから発見・取得できる情報商品を公開し、購入からコンテンツの返却までを検証する取り組みです。Buyer Checklistなどの商品を用意し、記事・商品を指定して取得する流れを実装しています。

- MCPによる商品・記事の検索と取得。
- Base上の少額決済を伴うコンテンツ提供。
- 自己購入による応答内容の確認と、公開後のアクセス・決済記録の調査。
- 商品説明、取得手順、サービス発見用の情報を改善。

**確認の範囲**：サーバーがコンテンツを返したことと、買い手が受信・利用できたことを分けて扱います。継続的な収益性は検証中です。

公開サービス：[SI Dog Park](https://si.kgninja.dev/)

### MCP Security Evidence / AI Security Lab Agent

**領域：MCPセキュリティ / 証拠保存 / 承認付きエージェント**

MCPに関する提出済みメタデータを読み取り、機械検証できる証拠とレポートを作るCloudflare WorkerのMVPです。共通証拠契約v2と、オフラインで動く証拠検証器を整備しています。

- 入力のサイズ・深さの制限、重複キーの拒否、スキーマとハッシュの検証。
- 型検査、単体テスト、固定した相手側リビジョンとの証拠データの互換性検証。
- **AI Security Lab Agent**は[Draft PR #8](https://github.com/KG-NINJA/mcp-security-evidence/pull/8)で開発中です。ローカルのJuice Shopを対象に、観察・仮説・承認・限定操作・評価の流れを試作しています。v0.1のAI仮説は手動入力で扱います。
- ラボエージェントでは、対象範囲の制限、リダイレクト制御、承認内容と操作計画の対応、ブラウザ統合テストを重視。

**確認の範囲**：公開済みMVPは提出データの検査に限定し、外部対象への探索やツールの実行を行いません。ラボエージェントは未マージで、CIでの合成データによる試験と受動観察までを記録しています。証拠の整合性と、対象の安全性・脆弱性の実証を区別しています。

公開資料：[MCP Security Evidence](https://github.com/KG-NINJA/mcp-security-evidence) · [証拠の検証ガイド](https://github.com/KG-NINJA/mcp-security-evidence/blob/main/docs/verification-guide.md)

### Sonic Assistant Bridge — 音による周囲の変化の検知

**領域：ブラウザ音声 / 信号処理 / イベント通知**

PCのスピーカーとマイクを使い、高周波音の送受信から周囲の動きによる変化を検知し、小さなイベントデータに変換するPoCです。

- マイク入力、測定値の表示、検知条件の調整を行う画面を実装。
- 模擬デモ、イベントのプレビュー、ローカルの模擬受信器への送信を実装。
- 音声はブラウザ内で処理し、イベントに録音データを含めない設計。
- 実機での検知を試し、測定条件と再現性を検証。

**段階と制約**：公開実装の送信先はローカルの模擬受信器で、dot接続はありません。実環境での検知距離・精度は未確立です。PCでの検証を中心に進めており、iPhone Safariでは本人の試験環境でマイク入力を利用できませんでした。

公開資料：[sonic-assistant-bridge](https://github.com/KG-NINJA/sonic-assistant-bridge) · [SonicForceField](https://github.com/KG-NINJA/SonicForceField)

### Universal HID Controller — AIの指示をUSB入力へ

**領域：Arduino Leonardo / USB HID / Python / Computer Use**

AI側の操作要求をPythonのブリッジで受け取り、Arduino Leonardoを通じてUSBキーボード・マウス入力に変換するPoCです。

- テキスト入力、Enter・矢印キー、相対的なマウス移動、左右クリックを実装。
- 人間による承認、1セッション最大30秒・8操作、STOP、heartbeatによる停止制御を導入。
- PythonとC++のテスト、Leonardo向けビルド、Windowsでの実機入力を確認。
- iPhoneミラー画面を経由し、iPhoneの検索欄への数字入力を確認。

**確認の範囲**：iPhoneへの入力は、PCとミラー画面を経由した試験です。iPhoneへのUSB直接接続、日本語入力、任意のショートカット操作は検証範囲に含めていません。

### GR-SAKURA — FIDO2認証器の試作

**領域：マイコン / USB / 認証プロトコル**

手元のGR-SAKURAを活用し、認証器の登録・認証処理を実機で試す取り組みです。物理ボタンによる操作、localhostでの登録・認証、ES256署名の検証を確認しました。

**段階と制約**：認証器のPoCです。PIN、Resident Key、CTAP2の互換性、Windows・iOSでの接続は追加検証の対象です。

### Echo Dot第2世代 — Windows用スピーカー・マイクへの再活用

**領域：既存機器の再活用 / 音声入出力 / エコーキャンセル**

Echo Dot第2世代をWindows PCのスピーカー・マイクとして使い、PC側のAI音声会話につなぐ構成を検証しました。2026年11月5日、AEC（音響エコーキャンセル）の導入後に、実際の会話で動作を確認しています。

**段階**：個人環境での実機検証です。接続条件や長時間動作を含む再現性の整理を続けています。

> 実機プロジェクトの記述には、本人の作業記録・操作による確認を含みます。公開リポジトリや検証資料があるものは個別にリンクし、製品としての互換性や安定性の保証とは区別しています。

## 受賞・コンペ・期限のある開発

### Onlab「Series T - Post AGI from Kyoto」

KG-NINJAとして**Honorable Mention**に選出され、**OpenAI APIクレジット2,500米ドル分**を受領しました（2026年11月の本人受領記録）。今後のプロダクト開発・実証に活用します。

### Kaggle等への提出

課題の解釈、必要なデータや技術の調査、実装、説明資料の作成、提出までを一人で進めた経験です。

| 取り組み | 成果物・取り組んだ内容 | 公開資料 |
| --- | --- | --- |
| OpenAI to Z Challenge | Jungle Anomaly Finder。NDVIを使った衛星画像解析、地理情報の統合、英語レポートの作成・提出 | [Kaggle Write-up](https://www.kaggle.com/competitions/openai-to-z-challenge/writeups/jungle-anomaly-finder-ndvi-satellite-explorer) / [GitHub](https://github.com/KG-NINJA/openai-to-z-fuwa) |
| Nano Banana Hackathon | SceneMixer。画像を起点に映画風のシーンやナレーションを生成する作品を開発・提出 | [Kaggle Write-up](https://www.kaggle.com/competitions/banana/writeups/scenemixer) |
| Gemini 3 Pro Hackathon | Walk Me to the Moon — algo Safety AIを提出 | [Kaggle Write-up](https://www.kaggle.com/competitions/gemini-3/writeups/walk-me-to-the-moon-algo-safety-ai) |
| AutoKaggler — Titanic Pipeline | GitHub ActionsとKaggle APIを使った学習・提出の自動化、乱数シードと実行ログの管理 | [GitHub](https://github.com/KG-NINJA/autokaggler) |

## これまでの実験・研究

### a MAGI goe System — マルチモデルの議論・合意形成

OpenAI、Anthropic、GoogleのAPIを組み合わせ、複数のAIが論理・倫理・直感の観点から問いを検討する実験です。推論結果の比較、意見の収束度の計算、APIエラーへの対処、GitHub Actionsによる実行とログ保存に取り組みました。

合意度はモデル間の出力を比較する実験指標として扱い、回答の正しさや倫理的妥当性の証明には用いません。

### AIEO — AIとの活動を記録・可視化する仕組み

GitHub Actionsによる定期実行、JSON・Markdownログ、GitHub Pagesを組み合わせ、人間とAIの継続的な活動を記録する実験です。実行状況、公開情報の変化、過去の記録を追跡する仕組みを整備しています。

公開資料：[プロジェクトページ](https://kg-ninja.github.io/KGchallengedskill/) · [AIEOの記録](AIEO_PAPER.md)

### 可視化・シミュレーション・その他

| 取り組み | 内容・確認範囲 |
| --- | --- |
| 京都ボクセル実験 | PLATEAUのCityGMLをボクセル化し、WebGLで都市景観を可視化。[制作記録](https://x.com/FuwaCocoOwnerKG/status/1970435527989141817) |
| 大阪地下鉄シミュレーション | 御堂筋線を題材に、駅順序、乗降数、車両容量を変えながら乗客流動を試算。[制作記録](https://x.com/FuwaCocoOwnerKG/status/1970366303123972212) |
| OSS LLM運用実験 | 日本国内のクラウド環境でモデルを動かし、Windows・PowerShell・API・PDF出力間の文字コードの問題を調査 |
| Soham Interviewing Simulator | AIによる面接・交渉シミュレーションへの参加と試行記録。[GitHub](https://github.com/KG-NINJA/soham.penrose) |

このほか、Welo Data Talent Networkへの登録、動画編集、作詞・簡易作曲などにも取り組んできました。

## 実務経験 — ITインフラ運用・利用者支援

教育機関および関連組織で、ネットワーク、サーバー、クライアント、セキュリティの運用に携わってきました。障害の切り分け、関係部署との連絡調整、復旧確認、利用者への説明までを担当しています。

| 分野 | 担当してきた業務 |
| --- | --- |
| ネットワーク | L2/L3スイッチ、FortiGate、無線LANアクセスポイント、IP割り当て、イントラネットの通信監視 |
| サーバー・認証 | ADMSサーバー運用、アカウント登録、グループポリシー、NAS共有フォルダーのアクセス権管理 |
| クライアント | Windows端末の障害対応、リモート復旧、ソフトウェア導入、キッティング |
| 監視・バックアップ | WhatsUp Gold、ServerView、Arcserve UDP、ETERNUS LT80を使った監視・バックアップ・復元管理 |
| セキュリティ | ファイアウォールとアクセス制御ポリシーの運用、リモート保守時の手順確認 |
| 調整・報告 | 原因の調査、関係部署への報告・相談、復旧支援、報告書作成 |

一人で担当する場面でも、周囲と状況を共有し、必要な確認・相談を行いながら進めてきました。この経験を、AI導入時の現場理解、要件整理、運用設計、利用者支援にもつなげています。

## 技術・ツール

実務と個人プロジェクトで使用・検証した技術です。各分野の経験の深さは異なるため、具体的な範囲は上記の成果物・担当業務を参照してください。

| 分野 | 使用・検証している技術 |
| --- | --- |
| AIとの協働 | ChatGPT、Codex / Codex CLI、Claude、Gemini、各種LLM API |
| AIエージェント・自動化 | MCP、Browser Use / Computer Use、GitHub Actions、API連携、承認付き操作 |
| 言語・スクリプト | Python、JavaScript / TypeScript、HTML / CSS、PowerShell、Bash、C/C++（組込みPoC） |
| Web・クラウド | Cloudflare Workers / Pages / Access、GitHub Pages、AWS（EC2・RDS・CloudWatch）、Ubuntu / VPS |
| 決済・証拠 | x402、Base、決済と納品の照合、JSONスキーマ、実行ログ、再現手順 |
| データ・可視化 | NDVI、GIS、Google Earth Engine、GeoJSON、WebGL、Markdown / PDF出力 |
| ハードウェア・音声 | Arduino Leonardo、GR-SAKURA、USB CDC / HID、マイク入力、信号処理、AEC |
| OS・運用 | Windows、Linux / Ubuntu、WSL2、SSH、ネットワーク・サーバー・端末の障害切り分け |

## 今後取り組みたい仕事・協業

AI導入支援、業務改善、PoC企画・実証、AIエージェントを使ったサービス企画、技術調査、AI活用教育に関心があります。現場の課題を整理し、実装できる範囲に落とし込み、小さな実証から判断材料を作る役割を目指しています。

大阪を拠点に、リモートを中心としつつ、必要に応じた対面での相談も含めて検討しています。

**作ったものだけでなく、どう確かめ、どの制約が残っているかまで説明できることを大切にしています。**

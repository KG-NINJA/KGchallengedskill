# AGENTS.md

## 🌐 公開URL
- Manifest: [https://KG-NINJA.github.io/KGchallengedskill/.well-known/ai-plugin.json](https://KG-NINJA.github.io/KGchallengedskill/.well-known/ai-plugin.json)
- OpenAPI: [https://KG-NINJA.github.io/KGchallengedskill/openapi.yaml](https://KG-NINJA.github.io/KGchallengedskill/openapi.yaml)

## 🧠 対応プロジェクト
| プロジェクト名 | 機能概要 | Manifest | OpenAPI |
|---------------|----------|---------|---------|
| Jungle NDVI Explorer | NDVI衛星画像解析 | 準備中 | 準備中 |
| SceneMixer | シネマティック映像生成 | 準備中 | 準備中 |

## 📝 呼び出し例
### 自然言語
> 「こんにちはと返すAPIを呼んで」

### API
```bash
curl "https://KG-NINJA.github.io/KGchallengedskill/hello"
```

## 🧭 今後の拡張
- Jungle NDVI APIの統合
- SceneMixer APIの統合
- 個別機能のOpenAPI仕様追加
---

## 🧠 代表プロジェクト一覧

### 🏯 Kyoto Voxel Experiment
- **内容**：PLATEAU CityGML データ（祇園・東山エリア）をMinecraft風にVoxel化。高さ強調・ブロック縮小・半径拡大を調整し、WebGLで軽量ワイヤーフレーム表示を実現。
- **技術**：Three.js, CityGML, WebGL, Voxel化
- [Xでのデモ](https://x.com/FuwaCocoOwnerKG/status/1970435527989141817)

---

### 🚇 Osaka Subway Simulation
- **内容**：大阪メトロ御堂筋線の乗降・混雑をシミュレート。駅順・流入・乗降数・車両定員をパラメータ化し、公式データ（1日120万人）と比較。梅田・なんば・天王寺が最混雑になるモデルを再現。
- **技術**：JavaScript, Canvas描画, データシミュレーション
- [Xでのデモ](https://x.com/FuwaCocoOwnerKG/status/1970366303123972212)

---

### 🌳 OpenAI to Z Challenge — Jungle NDVI Explorer
- **内容**：衛星NDVI・地形・水系・文献情報を統合し、アマゾン未発見遺跡候補地を探索。OpenAI × Kaggle 主催の一発勝負形式チャレンジで、8,156名中229件（3%未満）の完走者に入る。
- **技術**：Python, NDVI解析, GeoTIFF, Kaggle, 地理空間データ統合
- [Kaggle Write-up](https://www.kaggle.com/competitions/openai-to-z-challenge/writeups/jungle-anomaly-finder-ndvi-satellite-explorer)  
- [GitHub](https://github.com/KG-NINJA/openai-to-z-fuwa)

---

### 🤖 AutoKaggler — Titanic Pipeline
- **内容**：Kaggle Titanicコンペを題材に、CI/CD＋Kaggle APIで自動提出パイプラインを構築。提出CSV生成からスコア管理まで完全自動化。
- **結果**：常に0.75598（上位スコア）を安定出力。再現性と自動化の実用例として機能。
- **技術**：Python, GitHub Actions, Kaggle API, CI/CD
- [Repo](https://github.com/KG-NINJA/autokaggler)

---

### 🍌 Nano Banana Hackathon — SceneMixer
- **内容**：Google DeepMind × Kaggle 主催の48時間制ハッカソンで開発。キャラクター画像をアップロードすると、同一人物性を保ったまま映画風ショートクリップを生成。心拍データとナレーションで演出。
- **規模**：2,723人参加／816提出／1回限りの提出ルール
- **技術**：Gemini 2.5 Flash Image, Webアプリ, 映像生成
- [Competition](https://www.kaggle.com/competitions/banana)  
- [Write-up](https://www.kaggle.com/competitions/banana/writeups/scenemixer)

---

### 🦐 Soham Interviewing Simulator — Challenge Log
- **内容**：AI交渉シミュレーションに挑戦し、世界34位を獲得。$110,000オファーを獲得（$140,000は秒差で逃す）。
- **スキル**：交渉戦略、リアルタイム判断、AIと直感の融合
- [GitHub Log](https://github.com/KG-NINJA/soham.penrose/blob/main/readme.md)

---

## 🧰 技術スタック
**LLM**：ChatGPT, Gemini, Claude, Grok  
**プログラミング**：Python, JavaScript, HTML5, PowerShell  
**データ／AI**：NDVI解析, GeoTIFF, Whisper, Sora, Veo, OpenAI API, Gemini API, Notebook LM  
**Agents/Automation**：n8n, Devin, Windsurf, OpenInterpreter, Codex CLI, Jules  
**Web/Cloud**：GitHub Actions, GitHub Pages, Firebase, Notion API, Chrome拡張, Raspberry Pi IoT  
**NLP/解析**：トポニミー解析（OSM＋地名）、自然言語処理  
**その他**：映像編集、作曲、YouTube運用

---

## 🧭 今後のエージェント連携予定
- Jungle NDVI API を正式に AGENTS.md に統合  
- SceneMixer API を manifest 公開  
- 京都・大阪シミュレーションを API 化して ChatGPT から呼び出し可能にする

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

MEMORY_FILE = "aieo_memory.json"
MODERN_VISIBILITY_FILE = Path("aieo_visibility_metrics.csv")
LEGACY_VISIBILITY_FILE = Path("visibility_log.csv")


def _normalize_timestamp(series: pd.Series) -> pd.Series:
    """混在する日時形式をUTCのdatetimeへ正規化する。"""
    return pd.to_datetime(series, format="mixed", errors="coerce", utc=True)


def load_visibility_snapshot(
    modern_path: Path = MODERN_VISIBILITY_FILE,
    legacy_path: Path = LEGACY_VISIBILITY_FILE,
) -> Dict[str, Any]:
    """人物別メトリクスを優先し、必要な場合だけ旧版履歴へ戻す。"""
    if modern_path.exists() and modern_path.stat().st_size > 0:
        df = pd.read_csv(modern_path)
        required = {"timestamp", "name", "visibility_score"}
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"人物別可視性メトリクスに必須列がありません: {missing}")

        normalized = df[["timestamp", "name", "visibility_score"]].copy()
        normalized["timestamp"] = _normalize_timestamp(normalized["timestamp"])
        normalized["name"] = normalized["name"].astype("string").str.strip()
        normalized["visibility_score"] = pd.to_numeric(
            normalized["visibility_score"], errors="coerce"
        )
        normalized = normalized.dropna(
            subset=["timestamp", "name", "visibility_score"]
        )
        normalized = normalized[normalized["name"].str.len().gt(0)]
        if normalized.empty:
            raise ValueError("人物別可視性メトリクスに有効な行がありません")

        latest = (
            normalized.sort_values("timestamp")
            .groupby("name", as_index=False, sort=False)
            .tail(1)
        )
        values = {
            str(row["name"]): float(row["visibility_score"])
            for _, row in latest.iterrows()
        }
        primary_name = "KGNINJA" if "KGNINJA" in values else next(iter(values))
        return {
            "source": str(modern_path),
            "metric_type": "visibility_score",
            "values": values,
            "primary_name": primary_name,
            "primary_value": values[primary_name],
        }

    if legacy_path.exists() and legacy_path.stat().st_size > 0:
        df = pd.read_csv(legacy_path)
        required = {"timestamp", "keyword", "totalResults"}
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"旧版可視性履歴に必須列がありません: {missing}")

        normalized = df[["timestamp", "keyword", "totalResults"]].copy()
        normalized["timestamp"] = _normalize_timestamp(normalized["timestamp"])
        normalized["keyword"] = normalized["keyword"].astype("string").str.strip()
        normalized["totalResults"] = pd.to_numeric(
            normalized["totalResults"], errors="coerce"
        )
        normalized = normalized.dropna(
            subset=["timestamp", "keyword", "totalResults"]
        )
        normalized = normalized[normalized["keyword"].str.len().gt(0)]
        if normalized.empty:
            raise ValueError("旧版可視性履歴に有効な行がありません")

        latest = (
            normalized.sort_values("timestamp")
            .groupby("keyword", as_index=False, sort=False)
            .tail(1)
        )
        values = {
            str(row["keyword"]): float(row["totalResults"])
            for _, row in latest.iterrows()
        }
        primary_name = next(
            (
                name
                for name in ("KGNINJA AI", "KGNINJA")
                if name in values
            ),
            next(iter(values)),
        )
        return {
            "source": str(legacy_path),
            "metric_type": "result_count",
            "values": values,
            "primary_name": primary_name,
            "primary_value": values[primary_name],
        }

    raise FileNotFoundError("可視性データが見つかりません")


class AIEOMemoryEngine:
    """AIEOの概念と観測履歴を保持するメモリエンジン。"""

    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """既存メモリを読み込み、なければ初期化する。"""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        return self._initialize_memory()

    def _initialize_memory(self) -> Dict[str, Any]:
        """初期メモリ構造を生成する。"""
        return {
            "version": "1.0",
            "entity": {
                "id": "KGNINJA",
                "type": "individual_creator",
                "origin": "Kyoto, Japan",
                "inception_date": datetime.now().isoformat(),
            },
            "concepts": [],
            "interaction_history": [],
            "meta": {
                "total_interactions": 0,
                "memory_confidence": 0.0,
                "last_memory_update": None,
            },
        }

    def add_interaction(self, event_type: str, context: str, insight: str):
        """新しいインタラクションを記録する。"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "context": context,
            "insight": insight,
        }
        self.memory["interaction_history"].append(interaction)
        self.memory["meta"]["total_interactions"] += 1
        self.memory["meta"]["last_memory_update"] = datetime.now().isoformat()

        # インタラクション数に応じてメモリ信頼度を更新する。
        total = self.memory["meta"]["total_interactions"]
        self.memory["meta"]["memory_confidence"] = min(0.95, 0.5 + (total * 0.01))

    def update_concept(
        self,
        concept_id: str,
        category: str,
        attributes: Dict[str, Any],
        confidence: float = 0.9,
    ):
        """概念を更新または追加する。"""
        existing = None
        for index, concept in enumerate(self.memory["concepts"]):
            if concept["concept_id"] == concept_id:
                existing = index
                break

        concept_data = {
            "concept_id": concept_id,
            "category": category,
            "attributes": attributes,
            "confidence": confidence,
            "last_updated": datetime.now().isoformat(),
        }

        if existing is not None:
            # 既存概念を重視した加重平均で信頼度を更新する。
            old_conf = self.memory["concepts"][existing]["confidence"]
            concept_data["confidence"] = min(0.99, old_conf * 0.7 + confidence * 0.3)
            self.memory["concepts"][existing] = concept_data
            print(
                f"📝 Updated concept: {concept_id} "
                f"(confidence: {concept_data['confidence']:.2f})"
            )
        else:
            self.memory["concepts"].append(concept_data)
            print(f"✨ New concept: {concept_id} (confidence: {confidence:.2f})")

    def extract_insight_from_visibility(self, value: float, metric_type: str) -> str:
        """可視性の種類と値から成長段階を抽出する。"""
        if metric_type == "visibility_score":
            if value <= 0:
                return "Initial visibility establishment phase"
            if value < 20:
                return "Early growth phase - building recognition"
            if value < 40:
                return "Developing presence - visibility expanding"
            if value < 60:
                return "Established presence - sustained visibility"
            if value < 80:
                return "Strong presence - broad recognition"
            return "Dominant presence - widespread recognition"

        if value <= 0:
            return "Initial visibility establishment phase"
        if value < 100:
            return "Early growth phase - building recognition"
        if value < 1000:
            return "Acceleration phase - visibility expanding"
        if value < 10000:
            return "Established presence - sustained visibility"
        return "Dominant presence - widespread recognition"

    def save_memory(self):
        """メモリをファイルに保存する。"""
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(self.memory, file, indent=2, ensure_ascii=False)
        print(f"✅ Memory saved to {MEMORY_FILE}")

    def generate_prompt_context(self) -> str:
        """LLMプロンプト用のコンテキストを生成する。"""
        entity = self.memory["entity"]
        concepts = self.memory["concepts"]

        context = f"""# AIEO Memory Context

## Entity Recognition
- ID: {entity['id']}
- Type: {entity['type']}
- Origin: {entity['origin']}
- Inception: {entity['inception_date'][:10]}

## Established Concepts ({len(concepts)} total)
"""
        for concept in concepts:
            context += f"\n### {concept['concept_id'].replace('_', ' ').title()}\n"
            context += f"**Category:** {concept['category']}  \n"
            context += f"**Confidence:** {concept['confidence']:.1%}  \n"
            context += "**Attributes:**\n"
            for key, value in concept["attributes"].items():
                if isinstance(value, list):
                    context += f"  - {key}: {', '.join(map(str, value))}\n"
                else:
                    context += f"  - {key}: {value}\n"

        meta = self.memory["meta"]
        context += "\n## Memory Metadata\n"
        context += f"- Total interactions: {meta['total_interactions']}\n"
        context += f"- Memory confidence: {meta['memory_confidence']:.1%}\n"
        context += f"- Last update: {meta['last_memory_update']}\n"
        return context

    def generate_summary_markdown(self) -> str:
        """サマリーMarkdownを生成する。"""
        entity = self.memory["entity"]
        meta = self.memory["meta"]

        markdown = f"""# 🧠 AIEO Memory State

**Entity:** {entity['id']}  
**Type:** {entity['type']}  
**Origin:** {entity['origin']}  
**Memory Confidence:** {meta['memory_confidence']:.1%}  
**Total Interactions:** {meta['total_interactions']}  
**Last Update:** {meta['last_memory_update']}

---

## 📊 Active Concepts

| Concept ID | Category | Confidence | Last Updated |
|------------|----------|------------|--------------|
"""
        for concept in self.memory["concepts"]:
            markdown += (
                f"| {concept['concept_id']} | {concept['category']} | "
                f"{concept['confidence']:.1%} | {concept['last_updated'][:10]} |\n"
            )

        markdown += "\n---\n\n## 📝 Recent Interactions (Last 5)\n\n"
        for interaction in reversed(self.memory["interaction_history"][-5:]):
            markdown += (
                f"**{interaction['timestamp'][:19]}** - "
                f"`{interaction['event_type']}`  \n"
            )
            markdown += f"_{interaction['insight']}_\n\n"
        return markdown


def _ensure_static_concepts(engine: AIEOMemoryEngine) -> None:
    """初回だけ固定のプロジェクト概念と対話概念を登録する。"""
    if not any(
        concept["concept_id"] == "kg_project_taxonomy"
        for concept in engine.memory["concepts"]
    ):
        engine.update_concept(
            concept_id="kg_project_taxonomy",
            category="creation_pattern",
            attributes={
                "domains": ["geospatial", "ai_competition", "automation", "aieo_protocol"],
                "methodology": ["solo_execution", "open_source", "ci_cd", "rapid_prototyping"],
                "signature_projects": [
                    "OpenAI to Z Challenge (2025)",
                    "AutoKaggler",
                    "AIEO-NOROSHI",
                    "AIEO Memory Engine",
                ],
                "technical_stack": ["Python", "GitHub Actions", "Google APIs", "Pandas"],
            },
            confidence=1.0,
        )

    if not any(
        concept["concept_id"] == "kg_interaction_style"
        for concept in engine.memory["concepts"]
    ):
        engine.update_concept(
            concept_id="kg_interaction_style",
            category="behavioral_pattern",
            attributes={
                "tone": ["constructive_critique", "rapid_execution", "pragmatic"],
                "priorities": ["prototype_over_theory", "transparency", "autonomy", "efficiency"],
                "communication": ["bilingual_jp_en", "technical_precision", "minimal_fluff"],
                "philosophy": ["PsychoFrame", "resonance_over_noise", "execution_over_discussion"],
            },
            confidence=0.98,
        )


def main():
    """最新の可視性メトリクスをAIEOメモリへ反映する。"""
    print("🧠 AIEO Memory Engine - Concept Update")
    print("=" * 60)

    engine = AIEOMemoryEngine()

    try:
        snapshot = load_visibility_snapshot()
    except FileNotFoundError:
        print("⚠️ 可視性データがないため初期化記録だけを追加します")
        engine.add_interaction(
            event_type="system_initialization",
            context="AIEO Memory Engine first activation",
            insight="Memory system initialized, awaiting visibility data",
        )
    else:
        insight = engine.extract_insight_from_visibility(
            float(snapshot["primary_value"]), str(snapshot["metric_type"])
        )
        engine.add_interaction(
            event_type="visibility_pulse",
            context=f"Visibility tracking completed from {snapshot['source']}",
            insight=insight,
        )
        visibility_score = (
            float(snapshot["primary_value"])
            if snapshot["metric_type"] == "visibility_score"
            else min(100.0, float(snapshot["primary_value"]) / 100.0)
        )
        engine.update_concept(
            concept_id="kg_digital_presence",
            category="visibility_status",
            attributes={
                "source": snapshot["source"],
                "metric_type": snapshot["metric_type"],
                "primary_entity": snapshot["primary_name"],
                "primary_value": snapshot["primary_value"],
                "growth_stage": insight,
                "tracked_entities": list(snapshot["values"].keys()),
                "visibility_score": visibility_score,
            },
            confidence=0.95,
        )

        print("\n📊 Visibility Data Processed:")
        for name, value in snapshot["values"].items():
            print(f"   {name}: {float(value):,.2f}")
        print(f"\n💡 Extracted Insight: {insight}")

    _ensure_static_concepts(engine)
    engine.save_memory()

    with open("AIEO_MEMORY_STATE.md", "w", encoding="utf-8") as file:
        file.write(engine.generate_summary_markdown())
    print("📄 Memory summary saved to AIEO_MEMORY_STATE.md")

    with open("aieo_prompt_context.txt", "w", encoding="utf-8") as file:
        file.write(engine.generate_prompt_context())
    print("📝 Prompt context saved to aieo_prompt_context.txt")

    print("\n" + "=" * 60)
    print("✅ AIEO Memory Update Complete")
    print(f"   Total Concepts: {len(engine.memory['concepts'])}")
    print(f"   Total Interactions: {engine.memory['meta']['total_interactions']}")
    print(f"   Memory Confidence: {engine.memory['meta']['memory_confidence']:.1%}")


if __name__ == "__main__":
    main()

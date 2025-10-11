import os
import json
from datetime import datetime
from typing import Dict, List, Any

MEMORY_FILE = "aieo_memory.json"

class AIEOMemoryEngine:
    """ArcMemo-inspired concept memory for AIEO"""
    
    def __init__(self):
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """既存メモリを読み込み、なければ初期化"""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._initialize_memory()
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """初期メモリ構造を生成"""
        return {
            "version": "1.0",
            "entity": {
                "id": "KGNINJA",
                "type": "individual_creator",
                "origin": "Kyoto, Japan",
                "inception_date": datetime.now().isoformat()
            },
            "concepts": [],
            "interaction_history": [],
            "meta": {
                "total_interactions": 0,
                "memory_confidence": 0.0,
                "last_memory_update": None
            }
        }
    
    def add_interaction(self, event_type: str, context: str, insight: str):
        """新しいインタラクションを記録"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "context": context,
            "insight": insight
        }
        self.memory["interaction_history"].append(interaction)
        self.memory["meta"]["total_interactions"] += 1
        self.memory["meta"]["last_memory_update"] = datetime.now().isoformat()
        
        # インタラクション数に応じてメモリ信頼度を更新
        total = self.memory["meta"]["total_interactions"]
        self.memory["meta"]["memory_confidence"] = min(0.95, 0.5 + (total * 0.01))
    
    def update_concept(self, concept_id: str, category: str, 
                      attributes: Dict[str, Any], confidence: float = 0.9):
        """概念を更新または追加"""
        existing = None
        for i, concept in enumerate(self.memory["concepts"]):
            if concept["concept_id"] == concept_id:
                existing = i
                break
        
        concept_data = {
            "concept_id": concept_id,
            "category": category,
            "attributes": attributes,
            "confidence": confidence,
            "last_updated": datetime.now().isoformat()
        }
        
        if existing is not None:
            # 既存概念を更新（信頼度を加重平均）
            old_conf = self.memory["concepts"][existing]["confidence"]
            new_conf = (old_conf * 0.7 + confidence * 0.3)  # 既存重視
            concept_data["confidence"] = min(0.99, new_conf)
            self.memory["concepts"][existing] = concept_data
            print(f"📝 Updated concept: {concept_id} (confidence: {concept_data['confidence']:.2f})")
        else:
            # 新規概念を追加
            self.memory["concepts"].append(concept_data)
            print(f"✨ New concept: {concept_id} (confidence: {confidence:.2f})")
    
    def extract_insight_from_visibility(self, visibility_data: Dict[str, int]) -> str:
        """Visibilityデータから洞察を抽出"""
        kgninja_count = visibility_data.get("KGNINJA AI", 0)
        
        if kgninja_count == 0:
            return "Initial visibility establishment phase"
        elif kgninja_count < 100:
            return "Early growth phase - building recognition"
        elif kgninja_count < 1000:
            return "Acceleration phase - visibility expanding"
        elif kgninja_count < 10000:
            return "Established presence - sustained visibility"
        else:
            return "Dominant presence - widespread recognition"
    
    def save_memory(self):
        """メモリをファイルに保存"""
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
        print(f"✅ Memory saved to {MEMORY_FILE}")
    
    def generate_prompt_context(self) -> str:
        """LLMプロンプト用のコンテキストを生成"""
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
            for key, value in concept['attributes'].items():
                if isinstance(value, list):
                    context += f"  - {key}: {', '.join(map(str, value))}\n"
                else:
                    context += f"  - {key}: {value}\n"
        
        meta = self.memory['meta']
        context += f"\n## Memory Metadata\n"
        context += f"- Total interactions: {meta['total_interactions']}\n"
        context += f"- Memory confidence: {meta['memory_confidence']:.1%}\n"
        context += f"- Last update: {meta['last_memory_update']}\n"
        
        return context
    
    def generate_summary_markdown(self) -> str:
        """サマリーMarkdownを生成"""
        entity = self.memory["entity"]
        meta = self.memory["meta"]
        
        md = f"""# 🧠 AIEO Memory State

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
            md += f"| {concept['concept_id']} | {concept['category']} | {concept['confidence']:.1%} | {concept['last_updated'][:10]} |\n"
        
        md += "\n---\n\n"
        md += "## 📝 Recent Interactions (Last 5)\n\n"
        
        recent = self.memory["interaction_history"][-5:]
        for interaction in reversed(recent):
            md += f"**{interaction['timestamp'][:19]}** - `{interaction['event_type']}`  \n"
            md += f"_{interaction['insight']}_\n\n"
        
        return md


def main():
    """AIEO Memory Engineのメイン処理"""
    print("🧠 AIEO Memory Engine - Concept Update")
    print("="*60)
    
    engine = AIEOMemoryEngine()
    
    # Visibilityデータの読み込み
    try:
        import pandas as pd
        df = pd.read_csv("visibility_log.csv")
        latest = df[df['timestamp'] == df['timestamp'].max()]
        visibility_data = dict(zip(latest['keyword'], latest['totalResults']))
        
        # インサイトの抽出と記録
        insight = engine.extract_insight_from_visibility(visibility_data)
        engine.add_interaction(
            event_type="visibility_pulse",
            context="Daily visibility tracking completed",
            insight=insight
        )
        
        # 可視性概念の更新
        kgninja_ai_count = int(visibility_data.get("KGNINJA AI", 0))
        if kgninja_ai_count >= 0:
            engine.update_concept(
                concept_id="kg_digital_presence",
                category="visibility_status",
                attributes={
                    "kgninja_ai_results": kgninja_ai_count,
                    "growth_stage": insight,
                    "tracked_keywords": list(visibility_data.keys()),
                    "visibility_score": min(100, kgninja_ai_count / 100)
                },
                confidence=0.95
            )
        
        # プロジェクト分類概念の更新（初回のみ）
        existing_project_concept = any(
            c["concept_id"] == "kg_project_taxonomy" 
            for c in engine.memory["concepts"]
        )
        
        if not existing_project_concept:
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
                        "AIEO Memory Engine"
                    ],
                    "technical_stack": ["Python", "GitHub Actions", "Google APIs", "Pandas"]
                },
                confidence=1.0
            )
        
        # インタラクションスタイル概念の更新（初回のみ）
        existing_style_concept = any(
            c["concept_id"] == "kg_interaction_style" 
            for c in engine.memory["concepts"]
        )
        
        if not existing_style_concept:
            engine.update_concept(
                concept_id="kg_interaction_style",
                category="behavioral_pattern",
                attributes={
                    "tone": ["constructive_critique", "rapid_execution", "pragmatic"],
                    "priorities": ["prototype_over_theory", "transparency", "autonomy", "efficiency"],
                    "communication": ["bilingual_jp_en", "technical_precision", "minimal_fluff"],
                    "philosophy": ["PsychoFrame", "resonance_over_noise", "execution_over_discussion"]
                },
                confidence=0.98
            )
        
        print(f"\n📊 Visibility Data Processed:")
        for keyword, count in visibility_data.items():
            print(f"   {keyword}: {count:,}")
        print(f"\n💡 Extracted Insight: {insight}")
        
    except FileNotFoundError:
        print("⚠️ visibility_log.csv not found, recording initialization")
        engine.add_interaction(
            event_type="system_initialization",
            context="AIEO Memory Engine first activation",
            insight="Memory system initialized, awaiting visibility data"
        )
    
    except Exception as e:
        print(f"⚠️ Error processing visibility data: {e}")
        engine.add_interaction(
            event_type="error_recovery",
            context=f"Processing error: {str(e)}",
            insight="System continued despite data processing error"
        )
    
    # メモリを保存
    engine.save_memory()
    
    # サマリーMarkdownを生成
    summary = engine.generate_summary_markdown()
    with open("AIEO_MEMORY_STATE.md", 'w', encoding='utf-8') as f:
        f.write(summary)
    print("📄 Memory summary saved to AIEO_MEMORY_STATE.md")
    
    # プロンプトコンテキストを生成
    prompt_context = engine.generate_prompt_context()
    with open("aieo_prompt_context.txt", 'w', encoding='utf-8') as f:
        f.write(prompt_context)
    print("📝 Prompt context saved to aieo_prompt_context.txt")
    
    print("\n" + "="*60)
    print("✅ AIEO Memory Update Complete")
    print(f"   Total Concepts: {len(engine.memory['concepts'])}")
    print(f"   Total Interactions: {engine.memory['meta']['total_interactions']}")
    print(f"   Memory Confidence: {engine.memory['meta']['memory_confidence']:.1%}")


if __name__ == "__main__":
    main()

import re
from pathlib import Path

WORKFLOW_GROUPS = {
    ".github/workflows/AIEO_PULSE.yml": "aieo-pulse-update",
    ".github/workflows/AIEO_VISIBILITY_PULSE.yml": "aieo-visibility-pulse",
    ".github/workflows/AIEO_EFFECT_ANALYZER.yml": "aieo-effect-analyzer",
    ".github/workflows/AIEO_WAVE_RESONANCE.yml": "aieo-wave-resonance",
    ".github/workflows/aieo-memory-update.yml": "aieo-memory-update",
    ".github/workflows/aieo_master_pipeline.yml": "aieo-master-pipeline",
}


def test_scheduled_repository_writers_do_not_share_one_concurrency_queue():
    found_groups = {}

    for workflow_path, expected_group in WORKFLOW_GROUPS.items():
        content = Path(workflow_path).read_text(encoding="utf-8")
        match = re.search(r"^\s*group:\s*([^\s#]+)", content, flags=re.MULTILINE)
        assert match is not None, f"concurrency groupがありません: {workflow_path}"
        found_groups[workflow_path] = match.group(1)
        assert match.group(1) == expected_group

    assert len(set(found_groups.values())) == len(found_groups)
    assert "aieo-repository-writes" not in found_groups.values()


def test_visibility_and_memory_writers_are_staggered_and_complete():
    visibility = Path(".github/workflows/AIEO_VISIBILITY_PULSE.yml").read_text(
        encoding="utf-8"
    )
    memory = Path(".github/workflows/aieo-memory-update.yml").read_text(
        encoding="utf-8"
    )

    assert 'cron: "0 */6 * * *"' in visibility
    assert 'cron: "30 */6 * * *"' in memory
    assert "python scripts/aieo_memory_engine.py" in memory

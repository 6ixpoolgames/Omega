from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALPHA_UMBRELLA = ROOT / "formal" / "lean" / "AlphaCore.lean"
INDEPENDENCE = ROOT / "formal" / "lean" / "AlphaCore" / "Independence.lean"
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "alpha_independence_and_presentation_native_repair_v0.md"
)


def test_alpha_core_imports_independence_module() -> None:
    text = ALPHA_UMBRELLA.read_text(encoding="utf-8")
    assert "import AlphaCore.Independence" in text


def test_independence_module_exports_noncollapse_theorems() -> None:
    text = INDEPENDENCE.read_text(encoding="utf-8")
    required = [
        "relation_without_distinction",
        "distinction_without_relation",
        "relation_and_distinction_without_asymmetry",
        "reach_irreversibility_without_asymmetry",
        "asymmetry_implies_relation_and_distinction",
    ]
    missing = [name for name in required if name not in text]
    assert missing == []


def test_independence_module_has_no_placeholders() -> None:
    text = INDEPENDENCE.read_text(encoding="utf-8")
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_retained_note_documents_independence_repair() -> None:
    text = NOTE.read_text(encoding="utf-8")
    required = [
        "primitive non-collapse",
        "presentation-native",
        "relation_without_distinction",
        "distinction_without_relation",
        "relation_and_distinction_without_asymmetry",
        "reach_irreversibility_without_asymmetry",
        "asymmetry_implies_relation_and_distinction",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

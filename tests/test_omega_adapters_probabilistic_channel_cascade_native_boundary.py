from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
CASCADE = LEAN / "OmegaAdapters" / "ProbabilisticChannelCascadeNative.lean"
ENTRY = LEAN / "OmegaAdapters" / "ProbabilisticChannel.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"


def test_probabilistic_channel_cascade_imports_native_core_not_legacy() -> None:
    text = CASCADE.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelNative\b",
        text,
        re.MULTILINE,
    )
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_probabilistic_channel_entry_imports_native_cascade() -> None:
    entry = ENTRY.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelCascadeNative\b",
        entry,
        re.MULTILINE,
    )
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelCascadeNative\b",
        umbrella,
        re.MULTILINE,
    )


def test_probabilistic_channel_cascade_theorem_surface() -> None:
    text = CASCADE.read_text(encoding="utf-8")
    expected = [
        "chanComp",
        "cascadeTotalMass",
        "cascadeCompositeErrorMass",
        "cascade_composite_error_le_stage_errors",
        "cascade_error_bound_same_denominator",
        "cascadeTotalMass_eq_totalMass_chanComp",
        "cascadeCompositeErrorMass_eq_errorMass_chanComp",
    ]
    missing = [name for name in expected if name not in text]
    assert missing == []


def test_probabilistic_channel_cascade_has_no_proof_placeholders() -> None:
    text = CASCADE.read_text(encoding="utf-8")
    assert not re.search(r"\b(sorry|admit|axiom)\b", text)


def test_probabilistic_channel_cascade_doc_exists_and_marks_scope() -> None:
    doc = (
        ROOT
        / "docs"
        / "research_notes"
        / "omega_theory"
        / "omega_adapters_probabilistic_channel_cascade_native_v0.md"
    )
    text = " ".join(doc.read_text(encoding="utf-8").split())
    required = [
        "Lean-checked Alpha-native adapter conversion",
        "cascade_composite_error_le_stage_errors",
        "cascade_error_bound_same_denominator",
        "cascadeTotalMass_eq_totalMass_chanComp",
        "Policy, empirical, and compatibility semantics remain outside this module",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

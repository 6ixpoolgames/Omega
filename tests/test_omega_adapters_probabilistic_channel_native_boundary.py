from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
NATIVE = LEAN / "OmegaAdapters" / "ProbabilisticChannelNative.lean"
ENTRY = LEAN / "OmegaAdapters" / "ProbabilisticChannel.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"


def test_probabilistic_channel_native_imports_native_channel_not_legacy() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+OmegaAdapters\.FiniteChannelNative\b", text, re.MULTILINE)
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_probabilistic_channel_entry_imports_native_not_legacy() -> None:
    entry = ENTRY.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelNative\b", entry, re.MULTILINE)
    assert not re.search(
        r"^\s*import\s+OmegaCore\.Presentations\.ProbabilisticChannel\b",
        entry,
        re.MULTILINE,
    )
    assert re.search(r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelNative\b", umbrella, re.MULTILINE)


def test_probabilistic_channel_native_first_slice_theorem_surface() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    expected = [
        "exactSupportRecoverable_iff_nativeExactRecovers",
        "successMass_add_errorMass_eq_totalMass",
        "perfectProb_fullPrior_implies_exactSupport",
        "exactSupport_implies_perfectProb",
        "perfectProb_not_exact_without_full_prior",
        "highProb_not_exactSupport",
    ]
    missing = [name for name in expected if name not in text]
    assert missing == []


def test_probabilistic_channel_native_first_slice_defers_cascade_and_policy() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    deferred = [
        "cascade_composite_error_le_stage_errors",
        "cascade_error_bound_same_denominator",
        "bayes_best_can_exceed_fixed_declared",
    ]
    present = [name for name in deferred if name in text]
    assert present == []


def test_probabilistic_channel_native_has_no_proof_placeholders() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert not re.search(r"\b(sorry|admit|axiom)\b", text)


def test_probabilistic_channel_native_doc_exists_and_marks_scope() -> None:
    doc = (
        ROOT
        / "docs"
        / "research_notes"
        / "omega_theory"
        / "omega_adapters_probabilistic_channel_native_v0.md"
    )
    text = doc.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Alpha-native adapter conversion, first slice",
        "exactSupportRecoverable_iff_nativeExactRecovers",
        "perfectProb_fullPrior_implies_exactSupport",
        "highProb_not_exactSupport",
        "compatibility semantics remain outside this first slice",
    ]
    missing = [phrase for phrase in required if phrase not in normalized]
    assert missing == []

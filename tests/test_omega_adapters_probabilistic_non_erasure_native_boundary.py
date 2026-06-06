from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
NON_ERASURE = LEAN / "OmegaAdapters" / "ProbabilisticNonErasureNative.lean"
ENTRY = LEAN / "OmegaAdapters" / "ProbabilisticChannel.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "omega_adapters_probabilistic_non_erasure_native_v0.md"
)


def test_probabilistic_non_erasure_import_boundary() -> None:
    text = NON_ERASURE.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelNative\b",
        text,
        re.MULTILINE,
    )
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_probabilistic_non_erasure_entrypoints_import_module() -> None:
    entry = ENTRY.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticNonErasureNative\b",
        entry,
        re.MULTILINE,
    )
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticNonErasureNative\b",
        umbrella,
        re.MULTILINE,
    )


def test_probabilistic_non_erasure_theorem_surface() -> None:
    text = NON_ERASURE.read_text(encoding="utf-8")
    required = [
        "def RequirementSubset",
        "def ProbNonErasing",
        "def ExactSupportNonErasing",
        "theorem probNonErasing_mono_requirement",
        "theorem exactSupport_nonErasing_transfers_to_prob",
        "def ThresholdedDecoderRecovers",
        "theorem exactSupport_implies_thresholdedDecoderRecovers_100",
        "theorem marginal_recovery_does_not_force_all_requirements",
        "theorem thresholded_nonErasing_not_exactSupport",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_probabilistic_non_erasure_externalizes_recovery_evidence() -> None:
    text = NON_ERASURE.read_text(encoding="utf-8")
    assert "RecoveredAtThreshold" in text
    assert "This definition does not manufacture recovery evidence" in text
    forbidden = [
        "exists dec :",
        "Bayes",
        "argmax",
        "oracle",
    ]
    offenders = [phrase for phrase in forbidden if phrase in text]
    assert offenders == []


def test_probabilistic_non_erasure_has_no_placeholders() -> None:
    text = NON_ERASURE.read_text(encoding="utf-8")
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_probabilistic_non_erasure_note_documents_boundary() -> None:
    text = NOTE.read_text(encoding="utf-8")
    required = [
        "ProbNonErasing",
        "probNonErasing_mono_requirement",
        "RecoveredAtThreshold is external evidence",
        "marginal_recovery_does_not_force_all_requirements",
        "thresholded_nonErasing_not_exactSupport",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

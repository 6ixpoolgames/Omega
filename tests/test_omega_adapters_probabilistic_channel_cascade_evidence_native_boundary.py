from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
EVIDENCE = LEAN / "OmegaAdapters" / "ProbabilisticChannelCascadeEvidenceNative.lean"
ENTRY = LEAN / "OmegaAdapters" / "ProbabilisticChannel.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "omega_adapters_probabilistic_channel_cascade_evidence_native_v0.md"
)


def test_cascade_evidence_import_boundary() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelCascadeNative\b",
        text,
        re.MULTILINE,
    )
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_cascade_evidence_entrypoints_import_module() -> None:
    entry = ENTRY.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelCascadeEvidenceNative\b",
        entry,
        re.MULTILINE,
    )
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.ProbabilisticChannelCascadeEvidenceNative\b",
        umbrella,
        re.MULTILINE,
    )


def test_cascade_evidence_theorem_surface() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    required = [
        "structure CascadeEvidence",
        "def totalMass",
        "def errorMass",
        "def CompositeFailureCovered",
        "theorem union_bound",
        "def channelCascadeEvidence",
        "theorem channelCascadeEvidence_covered",
        "theorem channel_cascade_bound_from_evidence",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_cascade_evidence_avoids_independent_summary_theorem_surface() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    forbidden_theorem_names = [
        "independent_summary_bound",
        "independently_normalized_bound",
        "stage_rate_bound_without_path",
    ]
    offenders = [name for name in forbidden_theorem_names if name in text]
    assert offenders == []


def test_cascade_evidence_has_no_placeholders() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_cascade_evidence_note_documents_boundary() -> None:
    text = NOTE.read_text(encoding="utf-8")
    required = [
        "CascadeEvidence",
        "CascadeEvidence.union_bound",
        "channelCascadeEvidence",
        "channel_cascade_bound_from_evidence",
        "independently normalized",
        "theorem transfer should cite the evidence object",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
MODULE = LEAN / "OmegaAdapters" / "FiniteChannelDecoderNative.lean"
FINITE_CHANNEL = LEAN / "OmegaAdapters" / "FiniteChannel.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "omega_adapters_finite_channel_decoder_provenance_v0.md"
)
FINITE_CHANNEL_NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "omega_adapters_finite_channel_native_v0.md"
)


def test_decoder_provenance_module_is_imported() -> None:
    entry = FINITE_CHANNEL.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.FiniteChannelDecoderNative\b",
        entry,
        re.MULTILINE,
    )
    assert re.search(
        r"^\s*import\s+OmegaAdapters\.FiniteChannelDecoderNative\b",
        umbrella,
        re.MULTILINE,
    )


def test_decoder_provenance_exports_theorem_surface() -> None:
    text = MODULE.read_text(encoding="utf-8")
    required = [
        "inductive DecoderPolicy",
        "structure DecoderSpec",
        "structure DecoderRegistry",
        "def SpecExactRecovers",
        "def RegisteredExactRecovers",
        "def DeclaredRegisteredExactRecovers",
        "abbrev ExistsExactRecovers",
        "registered_exact_implies_exists_exact",
        "declared_registered_exact_implies_exists_exact",
        "spec_declared_exact_implies_exists_exact",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_decoder_provenance_blocks_reverse_implication_names() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = [
        "exists_exact_implies_registered",
        "exists_exact_implies_declared",
        "exists_exact_implies_declared_registered",
    ]
    offenders = [phrase for phrase in forbidden if phrase in text]
    assert offenders == []


def test_decoder_provenance_counterexamples_present() -> None:
    text = MODULE.read_text(encoding="utf-8")
    required = [
        "exists_exact_not_empty_registered",
        "bad_declared_registry_but_exists_exact",
        "bad_declared_good_exists",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_decoder_provenance_has_no_placeholders() -> None:
    text = MODULE.read_text(encoding="utf-8")
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_docs_state_exact_recovers_is_existence_style() -> None:
    note = NOTE.read_text(encoding="utf-8")
    finite_channel_note = FINITE_CHANNEL_NOTE.read_text(encoding="utf-8")
    required_note = [
        "existence-style exact recovery",
        "RegisteredExactRecovers",
        "DeclaredRegisteredExactRecovers",
        "No theorem proves that existence-style recovery implies registered",
    ]
    missing_note = [phrase for phrase in required_note if phrase not in note]
    assert missing_note == []
    assert "existence-style exact decoder recovery" in finite_channel_note

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
NATIVE = LEAN / "OmegaAdapters" / "FiniteBooleanNative.lean"
ENTRY = LEAN / "OmegaAdapters" / "FiniteBoolean.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"


def test_finite_boolean_native_imports_native_transport_only() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+ProtoOmega\.Transport\.Native\b", text, re.MULTILINE)
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_finite_boolean_entry_imports_native_not_legacy() -> None:
    entry = ENTRY.read_text(encoding="utf-8")
    umbrella = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+OmegaAdapters\.FiniteBooleanNative\b", entry, re.MULTILINE)
    assert not re.search(r"^\s*import\s+OmegaCore\.Presentations\.FiniteBoolean\b", entry, re.MULTILINE)
    assert re.search(r"^\s*import\s+OmegaAdapters\.FiniteBooleanNative\b", umbrella, re.MULTILINE)


def test_finite_boolean_native_has_expected_theorem_surface() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    expected = [
        "supportTransport_id_iff",
        "supportTransport_comp_subset",
        "changed_carrier_first_step",
        "changed_carrier_second_step",
        "changed_carrier_composite_recovery",
    ]
    missing = [name for name in expected if name not in text]
    assert missing == []


def test_finite_boolean_native_has_no_proof_placeholders() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert not re.search(r"\b(sorry|admit|axiom)\b", text)


def test_finite_boolean_native_doc_exists_and_marks_scope() -> None:
    doc = ROOT / "docs" / "research_notes" / "omega_theory" / "omega_adapters_finite_boolean_native_v0.md"
    text = doc.read_text(encoding="utf-8")
    required = [
        "Alpha-native adapter conversion",
        "supportTransport_id_iff",
        "supportTransport_comp_subset",
        "changed_carrier_composite_recovery",
        "compatibility semantics remain outside this module",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

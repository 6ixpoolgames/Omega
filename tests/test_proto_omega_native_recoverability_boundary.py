from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
RECOVERABILITY = LEAN / "ProtoOmega" / "Recoverability"

NATIVE = RECOVERABILITY / "Native.lean"
EXAMPLES = RECOVERABILITY / "NativeExamples.lean"
LEGACY_BRIDGE = RECOVERABILITY / "LegacyBridge.lean"

BANNED_DOWNSTREAM_TERMS = [
    "value",
    "valuer",
    "agency",
    "life",
    "living",
    "ethics",
    "moral",
    "good",
    "bad",
    "preference",
    "utility",
    "reward",
    "alignment",
    "lush",
    "anti-value",
    "death",
    "self",
    "identity",
]


def _new_native_files() -> list[Path]:
    return [NATIVE, EXAMPLES, LEGACY_BRIDGE]


def test_native_recoverability_imports_no_omega_core() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)
    assert re.search(r"^\s*import\s+ProtoOmega\.Transport\.Native\b", text, re.MULTILINE)


def test_native_examples_import_no_omega_core() -> None:
    text = EXAMPLES.read_text(encoding="utf-8")
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_only_recoverability_legacy_bridge_imports_omega_core() -> None:
    offenders: list[str] = []
    for path in _new_native_files():
        text = path.read_text(encoding="utf-8")
        if re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE):
            if path != LEGACY_BRIDGE:
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_native_recoverability_lean_has_no_downstream_terms() -> None:
    offenders: list[str] = []
    for path in [NATIVE, EXAMPLES]:
        text = path.read_text(encoding="utf-8").lower()
        for term in BANNED_DOWNSTREAM_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", text):
                offenders.append(f"{path.relative_to(ROOT)}:{term}")
    assert offenders == []


def test_native_recoverability_files_have_no_proof_placeholders() -> None:
    pattern = re.compile(r"\b(sorry|admit|axiom)\b")
    offenders: list[str] = []
    for path in _new_native_files():
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_native_recoverability_doc_exists_and_marks_scope() -> None:
    doc = ROOT / "docs" / "research_notes" / "omega_theory" / "proto_omega_recoverability_native_v0.md"
    text = doc.read_text(encoding="utf-8")
    required = [
        "Lean-checked Alpha-native recoverability layer",
        "NonErasing is requirement-relative coverage",
        "ProcessBundle",
        "JointPresentation",
        "Compatible",
        "Compatibility and completion remain downstream.",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

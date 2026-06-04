from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
RECOVERABILITY = LEAN / "ProtoOmega" / "Recoverability"

RECURRENT_NATIVE = RECOVERABILITY / "RecurrentNative.lean"
RECURRENT_EXAMPLES = RECOVERABILITY / "RecurrentNativeExamples.lean"


def test_recurrent_native_imports_no_omega_core() -> None:
    for path in [RECURRENT_NATIVE, RECURRENT_EXAMPLES]:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_recurrent_native_imports_native_recoverability() -> None:
    text = RECURRENT_NATIVE.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*import\s+ProtoOmega\.Recoverability\.Native\b",
        text,
        re.MULTILINE,
    )


def test_recurrent_native_has_no_proof_placeholders() -> None:
    pattern = re.compile(r"\b(sorry|admit|axiom)\b")
    offenders: list[str] = []
    for path in [RECURRENT_NATIVE, RECURRENT_EXAMPLES]:
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_recurrent_native_doc_exists_and_marks_scope() -> None:
    doc = ROOT / "docs" / "research_notes" / "omega_theory" / "proto_omega_recurrent_native_v0.md"
    text = doc.read_text(encoding="utf-8")
    required = [
        "Lean-checked Alpha-native finite-chain recoverability layer",
        "Chain",
        "RecoverChain",
        "recoverChain_sound",
        "compatibility",
        "completion",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
NATIVE = LEAN / "ProtoOmega" / "Separations" / "MarginalJointNative.lean"


def test_marginal_joint_native_imports_native_transport_only() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+ProtoOmega\.Transport\.Native\b", text, re.MULTILINE)
    assert not re.search(r"^\s*import\s+OmegaCore(\.|\s|$)", text, re.MULTILINE)


def test_marginal_joint_native_has_no_proof_placeholders() -> None:
    text = NATIVE.read_text(encoding="utf-8")
    assert not re.search(r"\b(sorry|admit|axiom)\b", text)


def test_marginal_joint_native_doc_exists_and_marks_scope() -> None:
    doc = ROOT / "docs" / "research_notes" / "omega_theory" / "proto_omega_marginal_joint_native_v0.md"
    text = doc.read_text(encoding="utf-8")
    required = [
        "Lean-checked Alpha-native finite separation",
        "marginal_non_erasure_not_joint_non_erasure",
        "marginal coverage does not imply joint coverage",
        "not an Omega-level result",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

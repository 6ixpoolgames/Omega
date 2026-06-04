from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALPHA_LEAN_DIR = ROOT / "formal" / "lean" / "AlphaCore"
ALPHA_NOTE = ROOT / "docs" / "research_notes" / "omega_theory" / "alpha_primitive_core_v0.md"


DOWNSTREAM_TERMS = [
    "omega",
    "value",
    "valuer",
    "agent",
    "agency",
    "life",
    "living",
    "ethic",
    "moral",
    "preference",
    "utility",
    "reward",
    "alignment",
    "uncertainty",
    "viability",
    "completion",
    "lush",
    "self",
    "identity",
    "death",
]


def _alpha_lean_files() -> list[Path]:
    return sorted(ALPHA_LEAN_DIR.glob("*.lean")) + [ROOT / "formal" / "lean" / "AlphaCore.lean"]


def test_alpha_core_lean_has_no_proof_placeholders() -> None:
    pattern = re.compile(r"\b(sorry|admit|axiom)\b")
    offenders: list[str] = []
    for path in _alpha_lean_files():
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_alpha_core_lean_has_no_downstream_semantic_terms() -> None:
    offenders: list[str] = []
    for path in _alpha_lean_files():
        text = path.read_text(encoding="utf-8").lower()
        for term in DOWNSTREAM_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", text):
                offenders.append(f"{path.relative_to(ROOT)}:{term}")
    assert offenders == []


def test_alpha_note_documents_standalone_boundary() -> None:
    text = ALPHA_NOTE.read_text(encoding="utf-8")
    required = [
        "Alpha Primitive Core v0",
        "Alpha is the standalone primitive floor",
        "Omega is downstream of Alpha",
        "OmegaCore",
        "establish Alpha first",
        "lake build AlphaCore",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

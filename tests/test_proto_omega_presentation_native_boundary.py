from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTO_UMBRELLA = ROOT / "formal" / "lean" / "ProtoOmega.lean"
PRESENTATION_NATIVE = (
    ROOT / "formal" / "lean" / "ProtoOmega" / "Presentation" / "Native.lean"
)
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "alpha_independence_and_presentation_native_repair_v0.md"
)


def test_proto_omega_imports_presentation_native_module() -> None:
    text = PROTO_UMBRELLA.read_text(encoding="utf-8")
    assert "import ProtoOmega.Presentation.Native" in text


def test_presentation_native_import_boundary() -> None:
    text = PRESENTATION_NATIVE.read_text(encoding="utf-8")
    assert "import AlphaCore" in text
    assert "import OmegaCore" not in text


def test_presentation_native_exports_core_structures() -> None:
    text = PRESENTATION_NATIVE.read_text(encoding="utf-8")
    required = [
        "structure DistPresentation",
        "structure SepPresentation",
        "structure DistOrder",
        "structure Transport",
        "def toSepPresentation",
        "def toDistPresentation",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_presentation_native_has_no_placeholders() -> None:
    text = PRESENTATION_NATIVE.read_text(encoding="utf-8")
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_retained_note_documents_presentation_boundary() -> None:
    text = NOTE.read_text(encoding="utf-8")
    required = [
        "DistPresentation",
        "SepPresentation",
        "DistOrder",
        "Transport",
        "full Alpha substrate",
        "presentation-native",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

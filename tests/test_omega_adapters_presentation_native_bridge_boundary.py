from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
BOOLEAN = LEAN / "OmegaAdapters" / "FiniteBooleanNative.lean"
CHANNEL = LEAN / "OmegaAdapters" / "FiniteChannelNative.lean"
BRIDGE = LEAN / "OmegaAdapters" / "SubstrateBridge.lean"
UMBRELLA = LEAN / "OmegaAdapters.lean"
NOTE = (
    ROOT
    / "docs"
    / "research_notes"
    / "omega_theory"
    / "omega_adapters_presentation_native_bridge_repair_v0.md"
)


def test_omega_adapters_imports_substrate_bridge() -> None:
    text = UMBRELLA.read_text(encoding="utf-8")
    assert re.search(r"^\s*import\s+OmegaAdapters\.SubstrateBridge\b", text, re.MULTILINE)


def test_finite_boolean_exposes_presentation_native_surface() -> None:
    text = BOOLEAN.read_text(encoding="utf-8")
    required = [
        "eventSepPresentation",
        "eventDistPresentation",
        "eventPresentationOrder",
        "supportPresentationTransport",
        "supportPresentationTransport_id_iff",
        "supportPresentationTransport_comp_subset",
    ]
    missing = [name for name in required if name not in text]
    assert missing == []


def test_finite_channel_exposes_presentation_native_surface() -> None:
    text = CHANNEL.read_text(encoding="utf-8")
    required = [
        "obsSepPresentation",
        "obsDistPresentation",
        "obsPresentationOrder",
        "channelPresentationTransport",
        "channelPresentationTransport_comp_subset",
    ]
    missing = [name for name in required if name not in text]
    assert missing == []


def test_substrate_bridge_is_explicit_and_placeholder_free() -> None:
    text = BRIDGE.read_text(encoding="utf-8")
    required = [
        "structure SubstrateBridge",
        "structure RelationBridge",
        "alphaFrameSelfBridge",
        "alphaFrameRelBridge",
        "sep_sound",
        "support_sound",
    ]
    missing = [name for name in required if name not in text]
    assert missing == []
    assert re.search(r"\b(sorry|admit|axiom)\b", text) is None


def test_retained_note_documents_adapter_repair() -> None:
    text = NOTE.read_text(encoding="utf-8")
    required = [
        "presentation-native",
        "Alpha-frame compatible",
        "SubstrateBridge",
        "RelationBridge",
        "supportPresentationTransport",
        "channelPresentationTransport",
        "separate proof obligation",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

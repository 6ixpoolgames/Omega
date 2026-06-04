from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal" / "lean"
MAP = ROOT / "docs" / "research_notes" / "omega_theory" / "alpha_omega_unification_map_v0.md"

DOWNSTREAM_MODULES = [
    "OmegaCore",
    "ProtoOmega",
    "OmegaAdapters",
    "OmegaProper",
    "OmegaArchive",
    "AlphaOmega",
]

ACTIVE_UMBRELLAS = [
    LEAN / "ProtoOmega.lean",
    LEAN / "OmegaAdapters.lean",
    LEAN / "OmegaProper.lean",
    LEAN / "AlphaOmega.lean",
]

OLD_OMEGA_CORE_FILES = [
    "OmegaCore/AdapterFailures.lean",
    "OmegaCore/Basic.lean",
    "OmegaCore/Completion.lean",
    "OmegaCore/Counterexamples.lean",
    "OmegaCore/DistTrans.lean",
    "OmegaCore/MarginalJoint.lean",
    "OmegaCore/NormalLax.lean",
    "OmegaCore/PrimitiveWitness.lean",
    "OmegaCore/Recurrent.lean",
    "OmegaCore/Presentations/FiniteBoolean.lean",
    "OmegaCore/Presentations/FiniteChannel.lean",
    "OmegaCore/Presentations/ProbabilisticChannel.lean",
    "OmegaCore/Presentations/ProbabilisticChannelPolicy.lean",
]


def _lean_files_under(path: Path) -> list[Path]:
    return sorted(path.rglob("*.lean"))


def test_alpha_core_imports_no_downstream_layers() -> None:
    files = _lean_files_under(LEAN / "AlphaCore") + [LEAN / "AlphaCore.lean"]
    offenders: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for module in DOWNSTREAM_MODULES:
            if re.search(rf"^\s*import\s+{re.escape(module)}(\.|\s|$)", text, re.MULTILINE):
                offenders.append(f"{path.relative_to(ROOT)} imports {module}")
    assert offenders == []


def test_alpha_omega_does_not_import_archive() -> None:
    text = (LEAN / "AlphaOmega.lean").read_text(encoding="utf-8")
    assert not re.search(r"^\s*import\s+OmegaArchive(\.|\s|$)", text, re.MULTILINE)


def test_active_umbrellas_do_not_import_archive() -> None:
    offenders: list[str] = []
    for path in ACTIVE_UMBRELLAS:
        text = path.read_text(encoding="utf-8")
        if re.search(r"^\s*import\s+OmegaArchive(\.|\s|$)", text, re.MULTILINE):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_new_formal_layers_have_no_proof_placeholders() -> None:
    pattern = re.compile(r"\b(sorry|admit|axiom)\b")
    paths: list[Path] = [
        LEAN / "AlphaOmega.lean",
        LEAN / "ProtoOmega.lean",
        LEAN / "OmegaAdapters.lean",
        LEAN / "OmegaProper.lean",
        LEAN / "OmegaArchive.lean",
    ]
    for dirname in ["AlphaCore", "ProtoOmega", "OmegaAdapters", "OmegaProper", "OmegaArchive"]:
        paths.extend(_lean_files_under(LEAN / dirname))

    offenders: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_unification_map_lists_every_old_omega_core_file() -> None:
    text = MAP.read_text(encoding="utf-8").replace("\\", "/")
    missing = [old for old in OLD_OMEGA_CORE_FILES if old not in text]
    assert missing == []


def test_unification_map_states_architecture_rules() -> None:
    text = MAP.read_text(encoding="utf-8")
    required = [
        "AlphaCore imports no downstream layer.",
        "ProtoOmega is derived dynamics/recoverability",
        "OmegaAdapters are substrate/presentation specific.",
        "OmegaProper is downstream and not solved.",
        "OmegaArchive is recoverable history, not active trunk.",
        "`AlphaOmega.lean` intentionally does not import `OmegaArchive`.",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

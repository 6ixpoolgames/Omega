"""X2 registry-first stochastic distinction-channel probe configuration."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from .registry_first_engine import (
    CascadeDistinctionSpec,
    CascadeSpec,
    Channel,
    DistinctionSpec,
    RegistryFirstConfig,
    RegistrySpec,
    RequirementSpec,
    ThresholdSpec,
    run_registry_first_engine,
)


DEFAULT_OUT = Path("results/stochastic_distinction_channel/20260605_registry_first_probe_v0")
PROBE_ID = "registry_first_stochastic_channel_probe_v0"
PROBE_SCHEMA_VERSION = "0.3.0"
SCOPE = "finite registry-first stochastic channel probe; provenance gap measurement only"
STATES = ["00", "01", "10", "11"]
PANELS = {"tiny", "medium"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run X2 registry-first stochastic-channel probe.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--panel",
        choices=sorted(PANELS),
        default="tiny",
        help="Channel panel to score. 'tiny' preserves the original smoke; 'medium' adds gap-revealing controls.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_registry_first_probe(out_dir=args.out, panel=args.panel)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_registry_first_probe(*, out_dir: Path = DEFAULT_OUT, panel: str = "tiny") -> dict[str, object]:
    if panel not in PANELS:
        raise ValueError(f"unknown registry-first probe panel: {panel}")
    return run_registry_first_engine(config=build_config(panel=panel), out_dir=out_dir)


def build_config(*, panel: str = "tiny") -> RegistryFirstConfig:
    return RegistryFirstConfig(
        probe_id=PROBE_ID,
        probe_schema_version=PROBE_SCHEMA_VERSION,
        scope=SCOPE,
        carrier_id="X2",
        states=STATES,
        source_distinctions=source_distinctions(),
        target_distinctions=target_distinctions(),
        fixed_targets={
            "D_A": "E_A",
            "D_B": "E_B",
            "D_joint": "E_joint",
            "D_parity": "E_parity",
            "D_trivial": "E_trivial",
        },
        requirements=[
            RequirementSpec("req_A", "single A distinction", ["D_A"]),
            RequirementSpec("req_B", "single B distinction", ["D_B"]),
            RequirementSpec("req_marginals", "A and B marginal distinctions", ["D_A", "D_B"]),
            RequirementSpec("req_joint", "joint pair distinction", ["D_joint"]),
            RequirementSpec("req_parity", "parity distinction", ["D_parity"]),
            RequirementSpec("req_all_nontrivial", "A, B, joint, and parity distinctions", ["D_A", "D_B", "D_joint", "D_parity"]),
        ],
        thresholds=thresholds(),
        registries=declared_decoder_registries(),
        channels=channel_definitions(panel=panel),
        channel_families=channel_families(panel=panel),
        cascades=[
            CascadeSpec(
                cascade_id="cascade_identity_then_b_flip_noise_9_1",
                first_channel_id="identity_channel",
                second_channel_id="b_flip_noise_9_1_channel",
                distinction_pairs=[
                    CascadeDistinctionSpec("D_A", "E_A", {"0": "0", "1": "1"}, {"0": "0", "1": "1"}),
                    CascadeDistinctionSpec("D_B", "E_B", {"0": "0", "1": "1"}, {"0": "0", "1": "1"}),
                ],
            )
        ],
        panel=panel,
    )


def source_distinctions() -> dict[str, DistinctionSpec]:
    return {
        "D_A": DistinctionSpec(["0", "1"], lambda state: state[0], "first bit", "single"),
        "D_B": DistinctionSpec(["0", "1"], lambda state: state[1], "second bit", "single"),
        "D_joint": DistinctionSpec(STATES, lambda state: state, "ordered pair", "full_joint"),
        "D_parity": DistinctionSpec(
            ["0", "1"],
            lambda state: str((int(state[0]) + int(state[1])) % 2),
            "xor of bits",
            "parity",
        ),
        "D_trivial": DistinctionSpec(["*"], lambda _state: "*", "constant", "trivial"),
    }


def target_distinctions() -> dict[str, DistinctionSpec]:
    return {
        "E_A": DistinctionSpec(["0", "1"], lambda state: state[0], "first bit", "single"),
        "E_B": DistinctionSpec(["0", "1"], lambda state: state[1], "second bit", "single"),
        "E_joint": DistinctionSpec(STATES, lambda state: state, "ordered pair", "full_joint"),
        "E_parity": DistinctionSpec(
            ["0", "1"],
            lambda state: str((int(state[0]) + int(state[1])) % 2),
            "xor of bits",
            "parity",
        ),
        "E_trivial": DistinctionSpec(["*"], lambda _state: "*", "constant", "trivial"),
    }


def thresholds() -> list[ThresholdSpec]:
    return [
        ThresholdSpec("threshold_exact_support", "exact support recovery", Fraction(1)),
        ThresholdSpec("threshold_0_95", "success >= 0.95", Fraction(19, 20)),
        ThresholdSpec("threshold_0_75", "success >= 0.75", Fraction(3, 4)),
    ]


def declared_decoder_registries() -> list[RegistrySpec]:
    return [
        RegistrySpec("reg_declared_D_A_E_A", "D_A", "E_A", "declared", [("dec_D_A_E_A_identity", {"0": "0", "1": "1"})]),
        RegistrySpec("reg_declared_D_B_E_B", "D_B", "E_B", "declared", [("dec_D_B_E_B_identity", {"0": "0", "1": "1"})]),
        RegistrySpec(
            "reg_declared_D_joint_E_joint",
            "D_joint",
            "E_joint",
            "declared",
            [("dec_D_joint_E_joint_identity", {state: state for state in STATES})],
        ),
        RegistrySpec("reg_declared_D_parity_E_parity", "D_parity", "E_parity", "declared", [("dec_D_parity_E_parity_identity", {"0": "0", "1": "1"})]),
        RegistrySpec("reg_declared_D_trivial_E_trivial", "D_trivial", "E_trivial", "declared", [("dec_D_trivial", {"*": "*"})]),
        RegistrySpec("reg_bad_declared_D_A_E_A", "D_A", "E_A", "declared", [("dec_bad_D_A_constant_0", {"0": "0", "1": "0"})]),
        RegistrySpec("reg_empty_D_joint_E_joint", "D_joint", "E_joint", "declared", []),
    ]


def channel_definitions(panel: str = "tiny") -> dict[str, Channel]:
    channels: dict[str, Channel] = {
        "identity_channel": {source: {target: int(source == target) for target in STATES} for source in STATES},
        "collapse_to_00_channel": {source: {target: int(target == "00") for target in STATES} for source in STATES},
        "a_preserved_b_erased_channel": {
            source: {target: int(target[0] == source[0]) for target in STATES}
            for source in STATES
        },
        "b_flip_noise_9_1_channel": bit_flip_noise_channel(1, keep=9, flip=1),
        "parity_projector_channel": {
            source: {target: int((target in ("00", "01")) and target[1] == parity(source)) for target in STATES}
            for source in STATES
        },
    }
    if panel == "medium":
        channels.update(
            {
                "b_preserved_a_erased_channel": {
                    source: {target: int(target[1] == source[1]) for target in STATES}
                    for source in STATES
                },
                "a_flip_noise_9_1_channel": bit_flip_noise_channel(0, keep=9, flip=1),
                "b_flip_noise_3_1_channel": bit_flip_noise_channel(1, keep=3, flip=1),
                "independent_bit_noise_81_9_9_1_channel": {
                    source: {target: independent_bit_noise_weight(source, target) for target in STATES}
                    for source in STATES
                },
                "parity_preserved_scramble_channel": {
                    source: {target: int(parity(target) == parity(source)) for target in STATES}
                    for source in STATES
                },
                "joint_cycle_channel": {
                    source: {target: int(target == cycle_state(source)) for target in STATES}
                    for source in STATES
                },
                "swap_bits_channel": {
                    source: {target: int(target == swap_bits(source)) for target in STATES}
                    for source in STATES
                },
                "copy_a_to_b_channel": {
                    source: {target: int(target == source[0] + source[0]) for target in STATES}
                    for source in STATES
                },
            }
        )
    return channels


def channel_families(panel: str = "tiny") -> dict[str, str]:
    family = {
        "identity_channel": "identity",
        "collapse_to_00_channel": "constant_output",
        "a_preserved_b_erased_channel": "selective_distinction_preservation",
        "b_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "parity_projector_channel": "parity_projection",
    }
    if panel == "medium":
        family.update(
            {
                "b_preserved_a_erased_channel": "selective_distinction_preservation",
                "a_flip_noise_9_1_channel": "natural_weight_bit_noise",
                "b_flip_noise_3_1_channel": "natural_weight_bit_noise",
                "independent_bit_noise_81_9_9_1_channel": "natural_weight_independent_bit_noise",
                "parity_preserved_scramble_channel": "parity_preserving_scramble",
                "joint_cycle_channel": "deterministic_relabeling",
                "swap_bits_channel": "deterministic_relabeling",
                "copy_a_to_b_channel": "deterministic_projection",
            }
        )
    return family


def bit_flip_noise_channel(index: int, *, keep: int, flip: int) -> Channel:
    return {
        source: {
            target: keep if target == source else flip if target == flip_bit(source, index) else 0
            for target in STATES
        }
        for source in STATES
    }


def flip_bit(state: str, index: int) -> str:
    bits = list(state)
    bits[index] = "0" if bits[index] == "1" else "1"
    return "".join(bits)


def parity(state: str) -> str:
    return str((int(state[0]) + int(state[1])) % 2)


def hamming_distance(left: str, right: str) -> int:
    return sum(int(a != b) for a, b in zip(left, right))


def independent_bit_noise_weight(source: str, target: str) -> int:
    return {0: 81, 1: 9, 2: 1}[hamming_distance(source, target)]


def cycle_state(state: str) -> str:
    order = ["00", "01", "11", "10"]
    return order[(order.index(state) + 1) % len(order)]


def swap_bits(state: str) -> str:
    return state[1] + state[0]


if __name__ == "__main__":
    main()

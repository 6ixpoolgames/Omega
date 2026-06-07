"""X3 registry-first stochastic distinction-channel probe configuration."""

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


DEFAULT_OUT = Path("results/stochastic_distinction_channel/20260606_registry_first_probe_x3_v0")
PROBE_ID = "registry_first_stochastic_channel_probe_x3_v0"
PROBE_SCHEMA_VERSION = "0.2.0"
SCOPE = "finite registry-first X3 stochastic channel probe; provenance gap measurement only"
STATES = [f"{value:03b}" for value in range(8)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run X3 registry-first stochastic-channel probe.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_registry_first_x3_probe(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_registry_first_x3_probe(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    return run_registry_first_engine(config=build_config(), out_dir=out_dir)


def build_config() -> RegistryFirstConfig:
    return RegistryFirstConfig(
        probe_id=PROBE_ID,
        probe_schema_version=PROBE_SCHEMA_VERSION,
        scope=SCOPE,
        carrier_id="X3",
        states=STATES,
        source_distinctions=source_distinctions(),
        target_distinctions=target_distinctions(),
        fixed_targets={
            "D_A": "E_A",
            "D_B": "E_B",
            "D_C": "E_C",
            "D_joint": "E_joint",
            "D_parity": "E_parity",
            "D_trivial": "E_trivial",
        },
        requirements=[
            RequirementSpec("req_A", "single A distinction", ["D_A"]),
            RequirementSpec("req_B", "single B distinction", ["D_B"]),
            RequirementSpec("req_C", "single C distinction", ["D_C"]),
            RequirementSpec("req_marginals", "A, B, and C marginal distinctions", ["D_A", "D_B", "D_C"]),
            RequirementSpec("req_joint", "joint triple distinction", ["D_joint"]),
            RequirementSpec("req_parity", "parity distinction", ["D_parity"]),
            RequirementSpec("req_all_nontrivial", "A, B, C, joint, and parity distinctions", ["D_A", "D_B", "D_C", "D_joint", "D_parity"]),
        ],
        thresholds=thresholds(),
        registries=declared_decoder_registries(),
        channels=channel_definitions(),
        channel_families=channel_families(),
        cascades=[
            CascadeSpec(
                cascade_id="cascade_identity_then_b_flip_noise_9_1",
                first_channel_id="identity_channel",
                second_channel_id="b_flip_noise_9_1_channel",
                distinction_pairs=[
                    CascadeDistinctionSpec("D_A", "E_A", {"0": "0", "1": "1"}, {"0": "0", "1": "1"}),
                    CascadeDistinctionSpec("D_B", "E_B", {"0": "0", "1": "1"}, {"0": "0", "1": "1"}),
                    CascadeDistinctionSpec("D_C", "E_C", {"0": "0", "1": "1"}, {"0": "0", "1": "1"}),
                ],
            )
        ],
    )


def source_distinctions() -> dict[str, DistinctionSpec]:
    return {
        "D_A": DistinctionSpec(["0", "1"], lambda state: state[0], "first bit", "single"),
        "D_B": DistinctionSpec(["0", "1"], lambda state: state[1], "second bit", "single"),
        "D_C": DistinctionSpec(["0", "1"], lambda state: state[2], "third bit", "single"),
        "D_joint": DistinctionSpec(STATES, lambda state: state, "ordered triple", "full_joint"),
        "D_parity": DistinctionSpec(
            ["0", "1"],
            lambda state: str(sum(int(bit) for bit in state) % 2),
            "xor of three bits",
            "parity",
        ),
        "D_trivial": DistinctionSpec(["*"], lambda _state: "*", "constant", "trivial"),
    }


def target_distinctions() -> dict[str, DistinctionSpec]:
    return {
        "E_A": DistinctionSpec(["0", "1"], lambda state: state[0], "first bit", "single"),
        "E_B": DistinctionSpec(["0", "1"], lambda state: state[1], "second bit", "single"),
        "E_C": DistinctionSpec(["0", "1"], lambda state: state[2], "third bit", "single"),
        "E_joint": DistinctionSpec(STATES, lambda state: state, "ordered triple", "full_joint"),
        "E_parity": DistinctionSpec(
            ["0", "1"],
            lambda state: str(sum(int(bit) for bit in state) % 2),
            "xor of three bits",
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
        RegistrySpec("reg_declared_D_C_E_C", "D_C", "E_C", "declared", [("dec_D_C_E_C_identity", {"0": "0", "1": "1"})]),
        RegistrySpec("reg_declared_D_joint_E_joint", "D_joint", "E_joint", "declared", [("dec_D_joint_E_joint_identity", {state: state for state in STATES})]),
        RegistrySpec("reg_declared_D_parity_E_parity", "D_parity", "E_parity", "declared", [("dec_D_parity_E_parity_identity", {"0": "0", "1": "1"})]),
        RegistrySpec("reg_declared_D_trivial_E_trivial", "D_trivial", "E_trivial", "declared", [("dec_D_trivial", {"*": "*"})]),
        RegistrySpec("reg_bad_declared_D_A_E_A", "D_A", "E_A", "declared", [("dec_bad_D_A_constant_0", {"0": "0", "1": "0"})]),
        RegistrySpec("reg_empty_D_joint_E_joint", "D_joint", "E_joint", "declared", []),
    ]


def channel_definitions() -> dict[str, Channel]:
    return {
        "identity_channel": {source: {target: int(source == target) for target in STATES} for source in STATES},
        "collapse_to_000_channel": {source: {target: int(target == "000") for target in STATES} for source in STATES},
        "a_preserved_bc_erased_channel": same_bit_channel(0),
        "b_preserved_ac_erased_channel": same_bit_channel(1),
        "c_preserved_ab_erased_channel": same_bit_channel(2),
        "ab_preserved_c_erased_channel": same_prefix_channel(2),
        "a_flip_noise_9_1_channel": bit_flip_noise_channel(0, keep=9, flip=1),
        "b_flip_noise_9_1_channel": bit_flip_noise_channel(1, keep=9, flip=1),
        "c_flip_noise_9_1_channel": bit_flip_noise_channel(2, keep=9, flip=1),
        "b_flip_noise_3_1_channel": bit_flip_noise_channel(1, keep=3, flip=1),
        "independent_bit_noise_729_81_9_1_channel": {
            source: {target: independent_bit_noise_weight(source, target) for target in STATES}
            for source in STATES
        },
        "parity_preserved_scramble_channel": {
            source: {target: int(parity(target) == parity(source)) for target in STATES}
            for source in STATES
        },
        "joint_cycle_channel": {source: {target: int(target == cycle_state(source)) for target in STATES} for source in STATES},
        "rotate_bits_channel": {source: {target: int(target == rotate_bits(source)) for target in STATES} for source in STATES},
        "copy_a_to_all_channel": {source: {target: int(target == source[0] * 3) for target in STATES} for source in STATES},
    }


def channel_families() -> dict[str, str]:
    return {
        "identity_channel": "identity",
        "collapse_to_000_channel": "constant_output",
        "a_preserved_bc_erased_channel": "selective_distinction_preservation",
        "b_preserved_ac_erased_channel": "selective_distinction_preservation",
        "c_preserved_ab_erased_channel": "selective_distinction_preservation",
        "ab_preserved_c_erased_channel": "partial_joint_preservation",
        "a_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "b_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "c_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "b_flip_noise_3_1_channel": "natural_weight_bit_noise",
        "independent_bit_noise_729_81_9_1_channel": "natural_weight_independent_bit_noise",
        "parity_preserved_scramble_channel": "parity_preserving_scramble",
        "joint_cycle_channel": "deterministic_relabeling",
        "rotate_bits_channel": "deterministic_relabeling",
        "copy_a_to_all_channel": "deterministic_projection",
    }


def same_bit_channel(index: int) -> Channel:
    return {
        source: {target: int(target[index] == source[index]) for target in STATES}
        for source in STATES
    }


def same_prefix_channel(width: int) -> Channel:
    return {
        source: {target: int(target[:width] == source[:width]) for target in STATES}
        for source in STATES
    }


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
    return str(sum(int(bit) for bit in state) % 2)


def hamming_distance(left: str, right: str) -> int:
    return sum(int(a != b) for a, b in zip(left, right))


def independent_bit_noise_weight(source: str, target: str) -> int:
    return {0: 729, 1: 81, 2: 9, 3: 1}[hamming_distance(source, target)]


def cycle_state(state: str) -> str:
    order = ["000", "001", "011", "010", "110", "111", "101", "100"]
    return order[(order.index(state) + 1) % len(order)]


def rotate_bits(state: str) -> str:
    return state[1:] + state[0]


if __name__ == "__main__":
    main()

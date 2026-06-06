"""Registry-first stochastic distinction-channel probe.

This probe is deliberately small and staged. It freezes declared decoder registries,
requirement sets, and thresholds before scoring any channel rows, then compares
declared/registered recovery with existence-style capacity and optimized
diagnostics.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Callable

from omega.future_field_atlas.util import stable_hash, write_csv, write_json

from .schema import canonical_json, fraction_text


DEFAULT_OUT = Path("results/stochastic_distinction_channel/20260605_registry_first_probe_v0")
PROBE_ID = "registry_first_stochastic_channel_probe_v0"
PROBE_SCHEMA_VERSION = "0.2.0"
SCOPE = "finite registry-first stochastic channel probe; provenance gap measurement only"
STATES = ["00", "01", "10", "11"]
PANELS = {"tiny", "medium"}


LabelFn = Callable[[str], str]
DecoderMap = dict[str, str]


def row_digest(rows: list[dict[str, object]]) -> str:
    normalized = [
        {str(key): str(value) for key, value in sorted(row.items())}
        for row in rows
    ]
    return stable_hash(normalized, length=24)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run registry-first stochastic-channel probe.")
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
    out_dir.mkdir(parents=True, exist_ok=True)

    carrier_rows = carrier_manifest()
    distinction_rows = distinction_manifest()
    requirement_rows = requirement_manifest()
    threshold_rows = threshold_manifest()
    registry_manifest_rows, decoder_registry_rows = declared_decoder_registries()

    pre_score_payload = {
        "carrier_manifest": carrier_rows,
        "distinction_manifest": distinction_rows,
        "requirement_set_manifest": requirement_rows,
        "threshold_manifest": threshold_rows,
        "registry_manifest": registry_manifest_rows,
        "declared_decoder_registry": decoder_registry_rows,
    }
    digests = {
        "registry_digest": stable_hash(
            {
                "registry_manifest": registry_manifest_rows,
                "declared_decoder_registry": decoder_registry_rows,
            },
            length=24,
        ),
        "requirement_digest": stable_hash(requirement_rows, length=24),
        "threshold_digest": stable_hash(threshold_rows, length=24),
    }
    digests["manifest_bundle_digest"] = stable_hash({**pre_score_payload, **digests}, length=24)

    pre_score_outputs = {
        "carrier_manifest.csv": carrier_rows,
        "distinction_manifest.csv": distinction_rows,
        "requirement_set_manifest.csv": requirement_rows,
        "threshold_manifest.csv": threshold_rows,
        "registry_manifest.csv": registry_manifest_rows,
        "declared_decoder_registry.csv": decoder_registry_rows,
    }
    pre_score_artifact_digests = {
        name: row_digest(rows) for name, rows in pre_score_outputs.items()
    }
    for name, rows in pre_score_outputs.items():
        write_csv(out_dir / name, rows)
    write_json(
        out_dir / "registry_digest.json",
        {
            **digests,
            "probe_id": PROBE_ID,
            "panel": panel,
            "pre_score_artifacts": sorted(pre_score_outputs),
            "pre_score_artifact_digests": pre_score_artifact_digests,
            "digest_available_before_scoring": True,
            "scope": SCOPE,
        },
    )

    channels = channel_definitions(panel=panel)
    priors = uniform_prior()
    observations = observation_tables()
    channel_rows = channel_manifest(channels)
    natural_audit_rows = natural_weight_equivalence_audit(channels)

    existence_rows = existence_recovery_by_distinction(channels, digests)
    optimized_rows = optimized_recovery_diagnostic(channels, priors, digests)
    registered_rows = registered_recovery_by_distinction(
        channels=channels,
        registry_manifest_rows=registry_manifest_rows,
        decoder_registry_rows=decoder_registry_rows,
        digests=digests,
    )
    coverage_rows = decoder_registry_coverage_audit(registry_manifest_rows, decoder_registry_rows)
    gap_rows = provenance_gap_by_distinction(
        registered_rows=registered_rows,
        existence_rows=existence_rows,
        optimized_rows=optimized_rows,
        digests=digests,
    )
    path_rows, cascade_summary_rows = cascade_evidence(channels, priors, digests)
    readiness_rows = theorem_transfer_readiness(
        registered_rows=registered_rows,
        gap_rows=gap_rows,
        cascade_summary_rows=cascade_summary_rows,
        natural_audit_rows=natural_audit_rows,
        digests=digests,
    )
    scoring_order_rows = scoring_order_audit(pre_score_outputs, digests)

    scored_outputs: dict[str, list[dict[str, object]]] = {
        "source_prior_manifest.csv": priors,
        "source_observation_table.csv": observations["source"],
        "target_observation_table.csv": observations["target"],
        "channel_manifest.csv": channel_rows,
        "channel_matrix.csv": channel_matrix_rows(channels, digests),
        "path_ensemble_rows.csv": path_rows,
        "registered_recovery_by_distinction.csv": registered_rows,
        "existence_recovery_by_distinction.csv": existence_rows,
        "optimized_recovery_diagnostic.csv": optimized_rows,
        "cascade_evidence_summary.csv": cascade_summary_rows,
        "theorem_transfer_readiness.csv": readiness_rows,
        "scoring_order_audit.csv": scoring_order_rows,
        "decoder_registry_coverage_audit.csv": coverage_rows,
        "provenance_gap_by_distinction.csv": gap_rows,
        "natural_weight_equivalence_audit.csv": natural_audit_rows,
    }
    for name, rows in scored_outputs.items():
        write_csv(out_dir / name, rows)
    scored_artifact_digests = {
        name: row_digest(rows) for name, rows in scored_outputs.items()
    }
    digest_chain = {
        "probe_id": PROBE_ID,
        "probe_schema_version": PROBE_SCHEMA_VERSION,
        "panel": panel,
        "registry_digest": digests["registry_digest"],
        "requirement_digest": digests["requirement_digest"],
        "threshold_digest": digests["threshold_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "pre_score_artifact_digests": pre_score_artifact_digests,
        "scored_artifact_digests": scored_artifact_digests,
    }
    digest_chain["digest_chain_digest"] = stable_hash(digest_chain, length=24)
    write_json(out_dir / "manifest_digest_chain.json", digest_chain)

    manifest = probe_manifest(
        out_dir=out_dir,
        panel=panel,
        pre_score_outputs=pre_score_outputs,
        scored_outputs=scored_outputs,
        digests=digests,
        digest_chain=digest_chain,
    )
    write_json(out_dir / "registry_first_probe_manifest.json", manifest)
    bundle = formal_consumption_bundle(
        out_dir=out_dir,
        panel=panel,
        digests=digests,
        manifest=manifest,
        readiness_rows=readiness_rows,
    )
    write_json(out_dir / "registry_first_formal_consumption_bundle.json", bundle)
    report = render_report(
        panel=panel,
        digests=digests,
        gap_rows=gap_rows,
        readiness_rows=readiness_rows,
        cascade_summary_rows=cascade_summary_rows,
        coverage_rows=coverage_rows,
    )
    (out_dir / "registry_first_probe_report.md").write_text(report, encoding="utf-8")

    return {
        "probe_id": PROBE_ID,
        "panel": panel,
        "out_dir": str(out_dir),
        "registry_digest": digests["registry_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "channel_count": len(channels),
        "registered_rows": len(registered_rows),
        "gap_rows": len(gap_rows),
        "cascade_evidence_status": cascade_summary_rows[0]["cascade_evidence_status"],
        "overall_status": bundle["overall_status"],
    }


def carrier_manifest() -> list[dict[str, object]]:
    return [
        {
            "carrier_id": "X2",
            "carrier_role": "source_and_target",
            "state_count": len(STATES),
            "states": ";".join(STATES),
            "scope": SCOPE,
        }
    ]


def source_distinctions() -> dict[str, dict[str, object]]:
    return {
        "D_A": {"label_set": ["0", "1"], "label": lambda state: state[0], "rule": "first bit"},
        "D_B": {"label_set": ["0", "1"], "label": lambda state: state[1], "rule": "second bit"},
        "D_joint": {"label_set": STATES, "label": lambda state: state, "rule": "ordered pair"},
        "D_parity": {
            "label_set": ["0", "1"],
            "label": lambda state: str((int(state[0]) + int(state[1])) % 2),
            "rule": "xor of bits",
        },
        "D_trivial": {"label_set": ["*"], "label": lambda _state: "*", "rule": "constant"},
    }


def target_distinctions() -> dict[str, dict[str, object]]:
    return {
        "E_A": {"label_set": ["0", "1"], "label": lambda state: state[0], "rule": "first bit"},
        "E_B": {"label_set": ["0", "1"], "label": lambda state: state[1], "rule": "second bit"},
        "E_joint": {"label_set": STATES, "label": lambda state: state, "rule": "ordered pair"},
        "E_parity": {
            "label_set": ["0", "1"],
            "label": lambda state: str((int(state[0]) + int(state[1])) % 2),
            "rule": "xor of bits",
        },
        "E_trivial": {"label_set": ["*"], "label": lambda _state: "*", "rule": "constant"},
    }


def fixed_target_for(source_distinction_id: str) -> str:
    return {
        "D_A": "E_A",
        "D_B": "E_B",
        "D_joint": "E_joint",
        "D_parity": "E_parity",
        "D_trivial": "E_trivial",
    }[source_distinction_id]


def distinction_manifest() -> list[dict[str, object]]:
    rows = []
    for distinction_id, spec in source_distinctions().items():
        rows.append(
            {
                "distinction_id": distinction_id,
                "carrier_id": "X2",
                "distinction_role": "source",
                "label_set": ";".join(spec["label_set"]),
                "labeling_rule": spec["rule"],
                "fixed_target_distinction_id": fixed_target_for(distinction_id),
                "scope": SCOPE,
            }
        )
    for distinction_id, spec in target_distinctions().items():
        rows.append(
            {
                "distinction_id": distinction_id,
                "carrier_id": "X2",
                "distinction_role": "target",
                "label_set": ";".join(spec["label_set"]),
                "labeling_rule": spec["rule"],
                "fixed_target_distinction_id": "",
                "scope": SCOPE,
            }
        )
    return rows


def observation_tables() -> dict[str, list[dict[str, object]]]:
    source_rows = []
    target_rows = []
    for distinction_id, spec in source_distinctions().items():
        label = spec["label"]
        for state in STATES:
            source_rows.append(
                {
                    "carrier_id": "X2",
                    "state_id": state,
                    "distinction_id": distinction_id,
                    "label": label(state),
                    "registry_first": 1,
                }
            )
    for distinction_id, spec in target_distinctions().items():
        label = spec["label"]
        for state in STATES:
            target_rows.append(
                {
                    "carrier_id": "X2",
                    "state_id": state,
                    "target_distinction_id": distinction_id,
                    "label": label(state),
                    "registry_first": 1,
                }
            )
    return {"source": source_rows, "target": target_rows}


def requirement_manifest() -> list[dict[str, object]]:
    specs = [
        ("req_A", "single A distinction", ["D_A"]),
        ("req_B", "single B distinction", ["D_B"]),
        ("req_marginals", "A and B marginal distinctions", ["D_A", "D_B"]),
        ("req_joint", "joint pair distinction", ["D_joint"]),
        ("req_parity", "parity distinction", ["D_parity"]),
        ("req_all_nontrivial", "A, B, joint, and parity distinctions", ["D_A", "D_B", "D_joint", "D_parity"]),
    ]
    return [
        {
            "requirement_set_id": requirement_id,
            "requirement_set_name": name,
            "source_distinction_ids": ";".join(distinctions),
            "requirement_count": len(distinctions),
            "declaration_rule": "pre_score_declared_requirement_set",
            "semantic_status": "finite_distinction_requirement_only",
            "scope": SCOPE,
        }
        for requirement_id, name, distinctions in specs
    ]


def threshold_manifest() -> list[dict[str, object]]:
    thresholds = [
        ("threshold_exact_support", "exact support recovery", Fraction(1)),
        ("threshold_0_95", "success >= 0.95", Fraction(19, 20)),
        ("threshold_0_75", "success >= 0.75", Fraction(3, 4)),
    ]
    return [
        {
            "threshold_id": threshold_id,
            "threshold_semantics": semantics,
            "threshold_value": float(value),
            "threshold_fraction": fraction_text(value),
            "comparison_rule": "success_mass * denominator >= numerator * total_mass",
            "predeclared": 1,
            "scope": SCOPE,
        }
        for threshold_id, semantics, value in thresholds
    ]


def declared_decoder_registries() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    registry_specs = [
        ("reg_declared_D_A_E_A", "D_A", "E_A", "declared", [("dec_D_A_E_A_identity", {"0": "0", "1": "1"})]),
        ("reg_declared_D_B_E_B", "D_B", "E_B", "declared", [("dec_D_B_E_B_identity", {"0": "0", "1": "1"})]),
        (
            "reg_declared_D_joint_E_joint",
            "D_joint",
            "E_joint",
            "declared",
            [("dec_D_joint_E_joint_identity", {state: state for state in STATES})],
        ),
        (
            "reg_declared_D_parity_E_parity",
            "D_parity",
            "E_parity",
            "declared",
            [("dec_D_parity_E_parity_identity", {"0": "0", "1": "1"})],
        ),
        ("reg_declared_D_trivial_E_trivial", "D_trivial", "E_trivial", "declared", [("dec_D_trivial", {"*": "*"})]),
        ("reg_bad_declared_D_A_E_A", "D_A", "E_A", "declared", [("dec_bad_D_A_constant_0", {"0": "0", "1": "0"})]),
        ("reg_empty_D_joint_E_joint", "D_joint", "E_joint", "declared", []),
    ]
    registry_rows = []
    decoder_rows = []
    for registry_id, source_distinction_id, target_distinction_id, policy, decoders in registry_specs:
        registry_rows.append(
            {
                "registry_id": registry_id,
                "source_distinction_id": source_distinction_id,
                "target_distinction_id": target_distinction_id,
                "registry_policy": policy,
                "decoder_count": len(decoders),
                "generation_rule": "pre_score_declared_decoder_registry",
                "eligible_for_declared_recovery": int(policy == "declared"),
                "pre_score_declared": 1,
                "scope": SCOPE,
            }
        )
        for decoder_id, mapping in decoders:
            for target_label, source_label in sorted(mapping.items()):
                decoder_rows.append(
                    {
                        "registry_id": registry_id,
                        "decoder_id": decoder_id,
                        "decoder_policy": policy,
                        "source_distinction_id": source_distinction_id,
                        "target_distinction_id": target_distinction_id,
                        "target_label": target_label,
                        "decoded_source_label": source_label,
                        "uses_target_observation_only": 1,
                        "eligible_for_declared_recovery": int(policy == "declared"),
                        "scope": SCOPE,
                    }
                )
    return registry_rows, decoder_rows


def channel_definitions(panel: str = "tiny") -> dict[str, dict[str, dict[str, int]]]:
    if panel not in PANELS:
        raise ValueError(f"unknown registry-first probe panel: {panel}")
    channels: dict[str, dict[str, dict[str, int]]] = {}
    channels["identity_channel"] = {
        source: {target: int(source == target) for target in STATES}
        for source in STATES
    }
    channels["collapse_to_00_channel"] = {
        source: {target: int(target == "00") for target in STATES}
        for source in STATES
    }
    channels["a_preserved_b_erased_channel"] = {
        source: {target: int(target[0] == source[0]) for target in STATES}
        for source in STATES
    }
    channels["b_flip_noise_9_1_channel"] = {
        source: {
            target: (9 if target == source else (1 if target == flip_b(source) else 0))
            for target in STATES
        }
        for source in STATES
    }
    channels["parity_projector_channel"] = {
        source: {
            target: int((target in ("00", "01")) and target[1] == parity(source))
            for target in STATES
        }
        for source in STATES
    }
    if panel == "medium":
        channels.update(medium_channel_definitions())
    return channels


def medium_channel_definitions() -> dict[str, dict[str, dict[str, int]]]:
    return {
        "b_preserved_a_erased_channel": {
            source: {target: int(target[1] == source[1]) for target in STATES}
            for source in STATES
        },
        "a_flip_noise_9_1_channel": {
            source: {
                target: (9 if target == source else (1 if target == flip_a(source) else 0))
                for target in STATES
            }
            for source in STATES
        },
        "b_flip_noise_3_1_channel": {
            source: {
                target: (3 if target == source else (1 if target == flip_b(source) else 0))
                for target in STATES
            }
            for source in STATES
        },
        "independent_bit_noise_81_9_9_1_channel": {
            source: {
                target: independent_bit_noise_weight(source, target)
                for target in STATES
            }
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


def flip_a(state: str) -> str:
    return ("0" if state[0] == "1" else "1") + state[1]


def flip_b(state: str) -> str:
    return state[0] + ("0" if state[1] == "1" else "1")


def parity(state: str) -> str:
    return str((int(state[0]) + int(state[1])) % 2)


def hamming_distance(a: str, b: str) -> int:
    return sum(int(left != right) for left, right in zip(a, b))


def independent_bit_noise_weight(source: str, target: str) -> int:
    distance = hamming_distance(source, target)
    return {0: 81, 1: 9, 2: 1}[distance]


def cycle_state(state: str) -> str:
    order = ["00", "01", "11", "10"]
    return order[(order.index(state) + 1) % len(order)]


def swap_bits(state: str) -> str:
    return state[1] + state[0]


def channel_manifest(channels: dict[str, dict[str, dict[str, int]]]) -> list[dict[str, object]]:
    family = {
        "identity_channel": "identity",
        "collapse_to_00_channel": "constant_output",
        "a_preserved_b_erased_channel": "selective_distinction_preservation",
        "b_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "parity_projector_channel": "parity_projection",
        "b_preserved_a_erased_channel": "selective_distinction_preservation",
        "a_flip_noise_9_1_channel": "natural_weight_bit_noise",
        "b_flip_noise_3_1_channel": "natural_weight_bit_noise",
        "independent_bit_noise_81_9_9_1_channel": "natural_weight_independent_bit_noise",
        "parity_preserved_scramble_channel": "parity_preserving_scramble",
        "joint_cycle_channel": "deterministic_relabeling",
        "swap_bits_channel": "deterministic_relabeling",
        "copy_a_to_b_channel": "deterministic_projection",
    }
    rows = []
    for channel_id in sorted(channels):
        row_totals = sorted({sum(row.values()) for row in channels[channel_id].values()})
        rows.append(
            {
                "channel_id": channel_id,
                "source_carrier_id": "X2",
                "target_carrier_id": "X2",
                "channel_family": family[channel_id],
                "natural_weight_row_totals": ";".join(str(total) for total in row_totals),
                "row_weight_total_constancy": "constant" if len(row_totals) == 1 else "nonconstant",
                "seed_policy": "deterministic",
                "params_json": canonical_json({}),
                "scope": SCOPE,
            }
        )
    return rows


def uniform_prior() -> list[dict[str, object]]:
    return [
        {
            "prior_id": "uniform_X2_natural",
            "carrier_id": "X2",
            "state_id": state,
            "prior_weight": 1,
            "prior_weight_total": len(STATES),
            "probability_fraction": fraction_text(Fraction(1, len(STATES))),
            "pre_score_declared": 1,
            "scope": SCOPE,
        }
        for state in STATES
    ]


def channel_matrix_rows(
    channels: dict[str, dict[str, dict[str, int]]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    rows = []
    for channel_id, matrix in sorted(channels.items()):
        for source_state, target_weights in sorted(matrix.items()):
            row_total = sum(target_weights.values())
            for target_state, weight in sorted(target_weights.items()):
                rows.append(
                    {
                        "channel_id": channel_id,
                        "source_state": source_state,
                        "target_state": target_state,
                        "natural_weight": weight,
                        "row_weight_total": row_total,
                        "probability_fraction": fraction_text(Fraction(weight, row_total)) if row_total else "",
                        "registry_digest": digests["registry_digest"],
                        "manifest_bundle_digest": digests["manifest_bundle_digest"],
                    }
                )
    return rows


def natural_weight_equivalence_audit(channels: dict[str, dict[str, dict[str, int]]]) -> list[dict[str, object]]:
    rows = []
    for channel_id, matrix in sorted(channels.items()):
        row_totals = {source_state: sum(weights.values()) for source_state, weights in matrix.items()}
        totals = sorted(set(row_totals.values()))
        status = "natural_weight_exact_probability_equivalent" if all(total > 0 for total in row_totals.values()) else "blocked_zero_row"
        rows.append(
            {
                "channel_id": channel_id,
                "row_weight_total": ";".join(f"{state}:{total}" for state, total in sorted(row_totals.items())),
                "row_weight_total_constancy": "constant" if len(totals) == 1 else "nonconstant",
                "global_scale_equivalence": "uniform_row_total" if len(totals) == 1 else "row_scaled",
                "probability_semantics_status": status,
                "notes": "finite natural weights are exact rational channel rows",
            }
        )
    return rows


def label(distinction_id: str, state: str) -> str:
    if distinction_id.startswith("D_"):
        spec = source_distinctions()[distinction_id]
    else:
        spec = target_distinctions()[distinction_id]
    return spec["label"](state)


def support_exact_with_decoder(
    channel: dict[str, dict[str, int]],
    source_distinction_id: str,
    target_distinction_id: str,
    decoder: DecoderMap,
) -> bool:
    for source_state, target_weights in channel.items():
        source_label = label(source_distinction_id, source_state)
        for target_state, weight in target_weights.items():
            if weight <= 0:
                continue
            target_label = label(target_distinction_id, target_state)
            if decoder.get(target_label) != source_label:
                return False
    return True


def success_mass(
    channel: dict[str, dict[str, int]],
    source_distinction_id: str,
    target_distinction_id: str,
    decoder: DecoderMap,
) -> tuple[int, int]:
    success = 0
    total = 0
    for source_state, target_weights in channel.items():
        source_prior_weight = 1
        source_label = label(source_distinction_id, source_state)
        for target_state, weight in target_weights.items():
            path_weight = source_prior_weight * weight
            total += path_weight
            target_label = label(target_distinction_id, target_state)
            if decoder.get(target_label) == source_label:
                success += path_weight
    return success, total


def enumerate_decoders(source_distinction_id: str, target_distinction_id: str) -> list[DecoderMap]:
    source_labels = list(source_distinctions()[source_distinction_id]["label_set"])
    target_labels = list(target_distinctions()[target_distinction_id]["label_set"])
    decoders = []
    for outputs in itertools.product(source_labels, repeat=len(target_labels)):
        decoders.append(dict(zip(target_labels, outputs)))
    return decoders


def existence_recovery_by_distinction(
    channels: dict[str, dict[str, dict[str, int]]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    rows = []
    for channel_id, channel in sorted(channels.items()):
        for source_distinction_id in sorted(source_distinctions()):
            for target_distinction_id in sorted(target_distinctions()):
                witness = None
                for decoder in enumerate_decoders(source_distinction_id, target_distinction_id):
                    if support_exact_with_decoder(channel, source_distinction_id, target_distinction_id, decoder):
                        witness = decoder
                        break
                rows.append(
                    {
                        "channel_id": channel_id,
                        "source_distinction_id": source_distinction_id,
                        "target_distinction_id": target_distinction_id,
                        "existence_recovery": int(witness is not None),
                        "recovery_provenance_class": "existence_capacity",
                        "witness_decoder_json": canonical_json(witness or {}),
                        "registry_digest": digests["registry_digest"],
                        "manifest_bundle_digest": digests["manifest_bundle_digest"],
                        "theorem_transfer_class": "support_exact_capacity_ready" if witness else "not_recovered",
                    }
                )
    return rows


def optimized_recovery_diagnostic(
    channels: dict[str, dict[str, dict[str, int]]],
    priors: list[dict[str, object]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    _ = priors
    rows = []
    for channel_id, channel in sorted(channels.items()):
        for source_distinction_id in sorted(source_distinctions()):
            best: dict[str, object] | None = None
            for target_distinction_id in sorted(target_distinctions()):
                for decoder in enumerate_decoders(source_distinction_id, target_distinction_id):
                    success, total = success_mass(channel, source_distinction_id, target_distinction_id, decoder)
                    exact = support_exact_with_decoder(channel, source_distinction_id, target_distinction_id, decoder)
                    candidate = {
                        "target_distinction_id": target_distinction_id,
                        "decoder_json": canonical_json(decoder),
                        "success_mass": success,
                        "total_mass": total,
                        "success_probability": float(Fraction(success, total)) if total else 0.0,
                        "success_fraction": fraction_text(Fraction(success, total)) if total else "",
                        "optimized_recovery": int(success == total),
                        "optimized_support_exact": int(exact),
                    }
                    if best is None or (success, int(exact), target_distinction_id) > (
                        int(best["success_mass"]),
                        int(best["optimized_support_exact"]),
                        str(best["target_distinction_id"]),
                    ):
                        best = candidate
            assert best is not None
            rows.append(
                {
                    "channel_id": channel_id,
                    "source_distinction_id": source_distinction_id,
                    "target_distinction_id": best["target_distinction_id"],
                    "decoder_policy_id": "optimized_best_available_diagnostic",
                    "recovery_provenance_class": "optimized_diagnostic",
                    "success_mass": best["success_mass"],
                    "total_mass": best["total_mass"],
                    "success_probability": best["success_probability"],
                    "success_fraction": best["success_fraction"],
                    "optimized_recovery": best["optimized_recovery"],
                    "optimized_support_exact": best["optimized_support_exact"],
                    "decoder_json": best["decoder_json"],
                    "theorem_transfer_class": "optimized_diagnostic_only",
                    "registry_digest": digests["registry_digest"],
                    "manifest_bundle_digest": digests["manifest_bundle_digest"],
                }
            )
    return rows


def registered_recovery_by_distinction(
    *,
    channels: dict[str, dict[str, dict[str, int]]],
    registry_manifest_rows: list[dict[str, object]],
    decoder_registry_rows: list[dict[str, object]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    decoders_by_registry: dict[str, dict[str, DecoderMap]] = defaultdict(lambda: defaultdict(dict))
    for row in decoder_registry_rows:
        registry_id = str(row["registry_id"])
        decoder_id = str(row["decoder_id"])
        decoders_by_registry[registry_id][decoder_id][str(row["target_label"])] = str(row["decoded_source_label"])

    rows = []
    for channel_id, channel in sorted(channels.items()):
        for registry in registry_manifest_rows:
            registry_id = str(registry["registry_id"])
            source_distinction_id = str(registry["source_distinction_id"])
            target_distinction_id = str(registry["target_distinction_id"])
            working_decoder_id = ""
            working_decoder_json = ""
            for decoder_id, decoder in sorted(decoders_by_registry.get(registry_id, {}).items()):
                if support_exact_with_decoder(channel, source_distinction_id, target_distinction_id, decoder):
                    working_decoder_id = decoder_id
                    working_decoder_json = canonical_json(decoder)
                    break
            registered = bool(working_decoder_id)
            declared = str(registry["registry_policy"]) == "declared"
            rows.append(
                {
                    "channel_id": channel_id,
                    "registry_id": registry_id,
                    "source_distinction_id": source_distinction_id,
                    "target_distinction_id": target_distinction_id,
                    "registry_policy": registry["registry_policy"],
                    "registered_recovery": int(registered),
                    "declared_registered_recovery": int(registered and declared),
                    "recovery_provenance_class": "declared_registered" if registered and declared else "registered",
                    "working_decoder_id": working_decoder_id,
                    "working_decoder_json": working_decoder_json,
                    "decoder_count": registry["decoder_count"],
                    "registry_digest": digests["registry_digest"],
                    "manifest_bundle_digest": digests["manifest_bundle_digest"],
                    "theorem_transfer_class": "declared_registered_recovery_ready"
                    if registered and declared
                    else "registered_not_recovered",
                }
            )
    return rows


def decoder_registry_coverage_audit(
    registry_manifest_rows: list[dict[str, object]],
    decoder_registry_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    decoder_counts: dict[str, int] = defaultdict(int)
    for row in decoder_registry_rows:
        decoder_counts[str(row["registry_id"])] += 1
    rows = []
    for registry in registry_manifest_rows:
        expected = int(registry["decoder_count"])
        observed_labels = decoder_counts[str(registry["registry_id"])]
        rows.append(
            {
                "registry_id": registry["registry_id"],
                "source_distinction_id": registry["source_distinction_id"],
                "target_distinction_id": registry["target_distinction_id"],
                "declared_decoder_count": expected,
                "decoder_table_rows": observed_labels,
                "coverage_status": "empty_registry_control"
                if expected == 0
                else ("covered" if observed_labels > 0 else "blocked_missing_decoder_rows"),
                "notes": "empty registry is a negative control" if expected == 0 else "",
            }
        )
    return rows


def provenance_gap_by_distinction(
    *,
    registered_rows: list[dict[str, object]],
    existence_rows: list[dict[str, object]],
    optimized_rows: list[dict[str, object]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    existence = {
        (row["channel_id"], row["source_distinction_id"], row["target_distinction_id"]): row
        for row in existence_rows
    }
    optimized = {
        (row["channel_id"], row["source_distinction_id"]): row
        for row in optimized_rows
    }
    rows = []
    for reg in registered_rows:
        key = (reg["channel_id"], reg["source_distinction_id"], reg["target_distinction_id"])
        exact_capacity = existence.get(key, {})
        opt = optimized.get((reg["channel_id"], reg["source_distinction_id"]), {})
        registered = as_bool(reg["registered_recovery"])
        declared_registered = as_bool(reg["declared_registered_recovery"])
        existence_value = as_bool(exact_capacity.get("existence_recovery", 0))
        optimized_value = as_bool(opt.get("optimized_recovery", 0))
        if declared_registered:
            transfer_class = "declared_registered_recovery_ready"
            blocked_reason = ""
        elif existence_value:
            transfer_class = "existence_capacity_only"
            blocked_reason = "declared_registry_did_not_recover"
        elif optimized_value:
            transfer_class = "optimized_diagnostic_only"
            blocked_reason = "optimized_policy_not_declared_registry"
        else:
            transfer_class = "not_recovered"
            blocked_reason = "no_registered_or_exact_capacity_recovery"
        rows.append(
            {
                "distinction_id": reg["source_distinction_id"],
                "channel_id": reg["channel_id"],
                "registry_id": reg["registry_id"],
                "target_distinction_id": reg["target_distinction_id"],
                "registered_recovery": int(registered),
                "declared_registered_recovery": int(declared_registered),
                "existence_recovery": int(existence_value),
                "optimized_recovery": int(optimized_value),
                "optimized_target_distinction_id": opt.get("target_distinction_id", ""),
                "registered_vs_existence_gap": int(existence_value and not registered),
                "registered_vs_optimized_gap": int(optimized_value and not registered),
                "theorem_transfer_class": transfer_class,
                "blocked_reason": blocked_reason,
                "recovery_provenance_class": reg["recovery_provenance_class"]
                if declared_registered
                else ("existence_capacity" if existence_value else "optimized_diagnostic" if optimized_value else "not_recovered"),
                "registry_digest": digests["registry_digest"],
                "manifest_bundle_digest": digests["manifest_bundle_digest"],
            }
        )
    return rows


def cascade_evidence(
    channels: dict[str, dict[str, dict[str, int]]],
    priors: list[dict[str, object]],
    digests: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    _ = priors
    cascade_id = "cascade_identity_then_b_flip_noise_9_1"
    first_channel_id = "identity_channel"
    second_channel_id = "b_flip_noise_9_1_channel"
    rows = []
    summaries = []
    for source_distinction_id, target_distinction_id in [("D_A", "E_A"), ("D_B", "E_B")]:
        dec1 = {"0": "0", "1": "1"}
        dec2 = {"0": "0", "1": "1"}
        first_error_mass = 0
        second_error_mass = 0
        composite_error_mass = 0
        total_mass = 0
        positive_path_count = 0
        for source_state in STATES:
            source_prior_weight = 1
            for intermediate_state, first_weight in channels[first_channel_id][source_state].items():
                for target_state, second_weight in channels[second_channel_id][intermediate_state].items():
                    path_weight = source_prior_weight * first_weight * second_weight
                    if path_weight <= 0:
                        continue
                    positive_path_count += 1
                    total_mass += path_weight
                    source_label = label(source_distinction_id, source_state)
                    intermediate_label = label(target_distinction_id, intermediate_state)
                    target_label = label(target_distinction_id, target_state)
                    first_output = dec1[intermediate_label]
                    second_output = dec2[target_label]
                    composed_output = dec1[second_output]
                    first_error = int(first_output != source_label)
                    second_error = int(second_output != intermediate_label)
                    composite_error = int(composed_output != source_label)
                    first_error_mass += first_error * path_weight
                    second_error_mass += second_error * path_weight
                    composite_error_mass += composite_error * path_weight
                    rows.append(
                        {
                            "cascade_id": cascade_id,
                            "source_distinction_id": source_distinction_id,
                            "target_distinction_id": target_distinction_id,
                            "source_state": source_state,
                            "intermediate_state": intermediate_state,
                            "target_state": target_state,
                            "source_prior_weight": source_prior_weight,
                            "first_channel_weight": first_weight,
                            "second_channel_weight": second_weight,
                            "path_weight": path_weight,
                            "source_distinction_label": source_label,
                            "intermediate_distinction_label": intermediate_label,
                            "target_distinction_label": target_label,
                            "first_decoder_output": first_output,
                            "second_decoder_output": second_output,
                            "composed_decoder_output": composed_output,
                            "first_stage_error": first_error,
                            "second_stage_error": second_error,
                            "composite_error": composite_error,
                            "registry_digest": digests["registry_digest"],
                            "manifest_bundle_digest": digests["manifest_bundle_digest"],
                        }
                    )
        summaries.append(
            {
                "cascade_id": cascade_id,
                "source_distinction_id": source_distinction_id,
                "target_distinction_id": target_distinction_id,
                "path_count": len(STATES) * len(STATES) * len(STATES),
                "positive_path_count": positive_path_count,
                "total_path_mass": total_mass,
                "first_stage_error_mass": first_error_mass,
                "second_stage_error_mass": second_error_mass,
                "composite_error_mass": composite_error_mass,
                "bound_rhs_error_mass": first_error_mass + second_error_mass,
                "bound_pass": int(composite_error_mass <= first_error_mass + second_error_mass),
                "cascade_evidence_status": "path_rows_retained",
                "lossless_reconstruction_contract": "path rows retained in path_ensemble_rows.csv",
                "theorem_transfer_eligible": 1,
                "registry_digest": digests["registry_digest"],
                "manifest_bundle_digest": digests["manifest_bundle_digest"],
            }
        )
    return rows, summaries


def theorem_transfer_readiness(
    *,
    registered_rows: list[dict[str, object]],
    gap_rows: list[dict[str, object]],
    cascade_summary_rows: list[dict[str, object]],
    natural_audit_rows: list[dict[str, object]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    has_declared_registered = any(as_bool(row["declared_registered_recovery"]) for row in registered_rows)
    has_existence_only = any(row["theorem_transfer_class"] == "existence_capacity_only" for row in gap_rows)
    has_optimized_gap = any(as_bool(row["registered_vs_optimized_gap"]) for row in gap_rows)
    cascade_ready = all(
        row["cascade_evidence_status"] in {"path_rows_retained", "losslessly_reconstructible"}
        and as_bool(row["bound_pass"])
        for row in cascade_summary_rows
    )
    natural_ready = all(row["probability_semantics_status"] == "natural_weight_exact_probability_equivalent" for row in natural_audit_rows)
    rows = [
        readiness_row(
            "support_exact_capacity_ready",
            bool(has_existence_only or has_declared_registered),
            "existence_capacity",
            "existence_recovery_by_distinction.csv",
            "existence capacity rows are separated from declared registry rows",
            digests,
        ),
        readiness_row(
            "registered_recovery_ready",
            bool(any(as_bool(row["registered_recovery"]) for row in registered_rows)),
            "registered",
            "registered_recovery_by_distinction.csv",
            "registered recovery rows require a supplied registry",
            digests,
        ),
        readiness_row(
            "declared_registered_recovery_ready",
            bool(has_declared_registered),
            "declared_registered",
            "registry_manifest.csv;declared_decoder_registry.csv;registered_recovery_by_distinction.csv",
            "declared registry recovery is available for successful declared rows",
            digests,
        ),
        readiness_row(
            "probability_measurement_ready",
            natural_ready,
            "measurement",
            "natural_weight_equivalence_audit.csv;optimized_recovery_diagnostic.csv",
            "natural weights have exact finite probability semantics",
            digests,
        ),
        readiness_row(
            "cascade_union_bound_ready",
            cascade_ready,
            "declared_registered",
            "path_ensemble_rows.csv;cascade_evidence_summary.csv",
            "cascade evidence uses retained path rows on one path ensemble",
            digests,
        ),
        readiness_row(
            "policy_substitution_blocked",
            True,
            "audit_guard",
            "provenance_gap_by_distinction.csv;optimized_recovery_diagnostic.csv",
            "optimized rows are diagnostic and not substituted for declared registry rows",
            digests,
        ),
        readiness_row(
            "optimized_diagnostic_only",
            has_optimized_gap,
            "optimized_diagnostic",
            "optimized_recovery_diagnostic.csv",
            "optimized rows are available as diagnostics only",
            digests,
        ),
        readiness_row(
            "substrate_bridge_ready",
            False,
            "not_applicable",
            "",
            "this finite presentation probe does not assert substrate bridge contact",
            digests,
        ),
    ]
    return rows


def readiness_row(
    readiness_axis: str,
    ready: bool,
    recovery_provenance_class: str,
    required_artifacts: str,
    notes: str,
    digests: dict[str, str],
) -> dict[str, object]:
    return {
        "readiness_axis": readiness_axis,
        "ready": int(ready),
        "status": "ready" if ready else "not_ready",
        "recovery_provenance_class": recovery_provenance_class,
        "required_artifacts": required_artifacts,
        "claim_allowed": notes,
        "notes": notes,
        "registry_digest": digests["registry_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
    }


def scoring_order_audit(pre_score_outputs: dict[str, list[dict[str, object]]], digests: dict[str, str]) -> list[dict[str, object]]:
    stages = [
        ("carriers", "carrier_manifest.csv"),
        ("distinctions", "distinction_manifest.csv"),
        ("requirement_sets", "requirement_set_manifest.csv"),
        ("thresholds", "threshold_manifest.csv"),
        ("decoder_registries", "registry_manifest.csv;declared_decoder_registry.csv"),
        ("registry_digest", "registry_digest.json"),
        ("scoring", "registered/existence/optimized/cascade artifacts"),
    ]
    rows = []
    for index, (stage_name, artifact) in enumerate(stages, start=1):
        rows.append(
            {
                "sequence_index": index,
                "stage_name": stage_name,
                "artifact": artifact,
                "completed_before_scoring": int(index < len(stages)),
                "digest_available_before_scoring": int(stage_name in {"registry_digest", "scoring"} or index < len(stages)),
                "registry_digest": digests["registry_digest"],
                "manifest_bundle_digest": digests["manifest_bundle_digest"],
                "status": "PASS",
                "notes": "pre-score artifact emitted before scoring" if index < len(stages) else "scoring artifacts carry registry digest",
            }
        )
    assert pre_score_outputs
    return rows


def probe_manifest(
    *,
    out_dir: Path,
    panel: str,
    pre_score_outputs: dict[str, list[dict[str, object]]],
    scored_outputs: dict[str, list[dict[str, object]]],
    digests: dict[str, str],
    digest_chain: dict[str, object],
) -> dict[str, object]:
    output_rows = {**pre_score_outputs, **scored_outputs}
    payload = {
        "panel": panel,
        "digests": digests,
        "row_counts": {name: len(rows) for name, rows in output_rows.items()},
    }
    return {
        "probe_id": PROBE_ID,
        "probe_schema_version": PROBE_SCHEMA_VERSION,
        "panel": panel,
        "output_directory": str(out_dir),
        "registry_digest": digests["registry_digest"],
        "requirement_digest": digests["requirement_digest"],
        "threshold_digest": digests["threshold_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "pre_score_artifacts": sorted(pre_score_outputs),
        "scored_artifacts": sorted(scored_outputs),
        "digest_chain_artifact": "manifest_digest_chain.json",
        "digest_chain_digest": digest_chain["digest_chain_digest"],
        "row_counts": {name: len(rows) for name, rows in output_rows.items()},
        "deterministic_rebuild_inputs": sorted(pre_score_outputs) + sorted(scored_outputs) + ["manifest_digest_chain.json"],
        "scope": SCOPE,
        "probe_digest": stable_hash(payload, length=24),
    }


def formal_consumption_bundle(
    *,
    out_dir: Path,
    panel: str,
    digests: dict[str, str],
    manifest: dict[str, object],
    readiness_rows: list[dict[str, object]],
) -> dict[str, object]:
    ready_axes = {row["readiness_axis"]: bool(as_bool(row["ready"])) for row in readiness_rows}
    overall = (
        "registry_first_theorem_transfer_ready"
        if ready_axes.get("declared_registered_recovery_ready")
        and ready_axes.get("cascade_union_bound_ready")
        and ready_axes.get("policy_substitution_blocked")
        else "registry_first_measurement_ready"
    )
    payload = {
        "panel": panel,
        "registry_digest": digests["registry_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "ready_axes": ready_axes,
        "overall_status": overall,
    }
    return {
        "bundle_schema_version": "0.1.0",
        "probe_id": PROBE_ID,
        "panel": panel,
        "source_probe_digest": manifest["probe_digest"],
        "output_directory": str(out_dir),
        "registry_manifest": "registry_manifest.csv",
        "registry_digest_path": "registry_digest.json",
        "declared_decoder_registry": "declared_decoder_registry.csv",
        "requirement_set_manifest": "requirement_set_manifest.csv",
        "threshold_manifest": "threshold_manifest.csv",
        "registered_recovery_by_distinction": "registered_recovery_by_distinction.csv",
        "existence_recovery_by_distinction": "existence_recovery_by_distinction.csv",
        "optimized_recovery_diagnostic": "optimized_recovery_diagnostic.csv",
        "provenance_gap_by_distinction": "provenance_gap_by_distinction.csv",
        "path_ensemble_rows": "path_ensemble_rows.csv",
        "cascade_evidence_summary": "cascade_evidence_summary.csv",
        "manifest_digest_chain": "manifest_digest_chain.json",
        "theorem_transfer_readiness": "theorem_transfer_readiness.csv",
        "overall_status": overall,
        "scope": SCOPE,
        "bundle_digest": stable_hash(payload, length=24),
    }


def render_report(
    *,
    panel: str,
    digests: dict[str, str],
    gap_rows: list[dict[str, object]],
    readiness_rows: list[dict[str, object]],
    cascade_summary_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
) -> str:
    existence_gaps = [row for row in gap_rows if as_bool(row["registered_vs_existence_gap"])]
    optimized_gaps = [row for row in gap_rows if as_bool(row["registered_vs_optimized_gap"])]
    ready_lines = [
        f"- `{row['readiness_axis']}`: `{row['status']}` ({row['recovery_provenance_class']})"
        for row in readiness_rows
    ]
    gap_lines = [
        f"- `{row['channel_id']}` / `{row['registry_id']}`: "
        f"registered={row['registered_recovery']}, existence={row['existence_recovery']}, "
        f"optimized={row['optimized_recovery']} -> `{row['theorem_transfer_class']}`"
        for row in gap_rows
        if row["registry_id"] in {"reg_bad_declared_D_A_E_A", "reg_empty_D_joint_E_joint"}
    ][:12]
    cascade_lines = [
        f"- `{row['source_distinction_id']}`: composite {row['composite_error_mass']} <= "
        f"{row['first_stage_error_mass']} + {row['second_stage_error_mass']} "
        f"(`{row['cascade_evidence_status']}`)"
        for row in cascade_summary_rows
    ]
    coverage_lines = [
        f"- `{row['registry_id']}`: `{row['coverage_status']}`"
        for row in coverage_rows
        if row["coverage_status"] != "covered"
    ]
    return "\n".join(
        [
            "# Registry-First Stochastic Channel Probe v0",
            "",
            "## Executive Summary",
            "",
            "This run freezes declared decoder registries, requirement sets, and thresholds "
            "before scoring finite stochastic channels. It then separates declared registry "
            "recovery from existence-style channel capacity and optimized diagnostics. The "
            "useful object is the gap: a channel can contain recoverable information while a "
            "declared registry fails to recover it.",
            "",
            f"- registry digest: `{digests['registry_digest']}`",
            f"- manifest bundle digest: `{digests['manifest_bundle_digest']}`",
            f"- panel: `{panel}`",
            f"- registered vs existence gaps: {len(existence_gaps)}",
            f"- registered vs optimized gaps: {len(optimized_gaps)}",
            "",
            "## Scope",
            "",
            SCOPE,
            "",
            "## Generation Order",
            "",
            "Carriers, distinctions, requirement sets, thresholds, and declared decoder "
            "registries are emitted before scoring. `registry_digest.json` records the frozen "
            "registry bytes and every scored row carries the digest.",
            "",
            "## Registry Controls",
            "",
            *coverage_lines,
            "",
            "## Provenance Gap Examples",
            "",
            *gap_lines,
            "",
            "## Cascade Evidence",
            "",
            *cascade_lines,
            "",
            "## Theorem-Transfer Readiness",
            "",
            *ready_lines,
            "",
            "## Read",
            "",
            "Positive declared-registry rows can be used as declared recovery evidence. "
            "Existence-only rows are capacity evidence. Optimized rows are diagnostic. The "
            "empty-registry and bad-declared-decoder controls intentionally fail so those "
            "evidence classes cannot collapse into each other.",
        ]
    )


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass", "ready"}


if __name__ == "__main__":
    main()

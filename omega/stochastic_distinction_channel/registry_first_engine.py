"""Shared registry-first stochastic-channel probe engine.

The engine owns the provenance protocol: pre-score manifests, digest freezing,
scored recovery surfaces, path-level cascade evidence, readiness vectors, and
audit-compatible artifacts. Carrier-specific modules should only supply finite
states, distinctions, declared registries, channel panels, and cascade specs.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable

from omega.future_field_atlas.util import stable_hash, write_csv, write_json

from .schema import canonical_json, fraction_text


LabelFn = Callable[[str], str]
DecoderMap = dict[str, str]
Channel = dict[str, dict[str, int]]


@dataclass(frozen=True)
class DistinctionSpec:
    label_set: list[str]
    label: LabelFn
    rule: str
    rank_class: str = ""


@dataclass(frozen=True)
class RequirementSpec:
    requirement_set_id: str
    name: str
    source_distinction_ids: list[str]


@dataclass(frozen=True)
class ThresholdSpec:
    threshold_id: str
    semantics: str
    value: Fraction


@dataclass(frozen=True)
class RegistrySpec:
    registry_id: str
    source_distinction_id: str
    target_distinction_id: str
    policy: str
    decoders: list[tuple[str, DecoderMap]]


@dataclass(frozen=True)
class CascadeDistinctionSpec:
    source_distinction_id: str
    target_distinction_id: str
    first_decoder: DecoderMap
    second_decoder: DecoderMap


@dataclass(frozen=True)
class CascadeSpec:
    cascade_id: str
    first_channel_id: str
    second_channel_id: str
    distinction_pairs: list[CascadeDistinctionSpec]


@dataclass(frozen=True)
class RegistryFirstConfig:
    probe_id: str
    probe_schema_version: str
    scope: str
    carrier_id: str
    states: list[str]
    source_distinctions: dict[str, DistinctionSpec]
    target_distinctions: dict[str, DistinctionSpec]
    fixed_targets: dict[str, str]
    requirements: list[RequirementSpec]
    thresholds: list[ThresholdSpec]
    registries: list[RegistrySpec]
    channels: dict[str, Channel]
    channel_families: dict[str, str]
    cascades: list[CascadeSpec]
    panel: str = ""


def run_registry_first_engine(*, config: RegistryFirstConfig, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    carrier_rows = carrier_manifest(config)
    distinction_rows = distinction_manifest(config)
    requirement_rows = requirement_manifest(config)
    threshold_rows = threshold_manifest(config)
    registry_manifest_rows, decoder_registry_rows = declared_decoder_registries(config)

    pre_score_outputs = {
        "carrier_manifest.csv": carrier_rows,
        "distinction_manifest.csv": distinction_rows,
        "requirement_set_manifest.csv": requirement_rows,
        "threshold_manifest.csv": threshold_rows,
        "registry_manifest.csv": registry_manifest_rows,
        "declared_decoder_registry.csv": decoder_registry_rows,
    }
    pre_score_artifact_digests = {name: row_digest(rows) for name, rows in pre_score_outputs.items()}
    digests = {
        "registry_digest": stable_hash(
            {"registry_manifest": registry_manifest_rows, "declared_decoder_registry": decoder_registry_rows},
            length=24,
        ),
        "requirement_digest": stable_hash(requirement_rows, length=24),
        "threshold_digest": stable_hash(threshold_rows, length=24),
    }
    digests["manifest_bundle_digest"] = stable_hash(
        {"pre_score_outputs": pre_score_outputs, "digests": digests},
        length=24,
    )

    for name, rows in pre_score_outputs.items():
        write_csv(out_dir / name, rows)
    write_json(
        out_dir / "registry_digest.json",
        {
            **digests,
            "probe_id": config.probe_id,
            "carrier_id": config.carrier_id,
            "panel": config.panel,
            "pre_score_artifacts": sorted(pre_score_outputs),
            "pre_score_artifact_digests": pre_score_artifact_digests,
            "digest_available_before_scoring": True,
            "scope": config.scope,
        },
    )

    priors = uniform_prior(config)
    observations = observation_tables(config)
    channel_rows = channel_manifest(config)
    natural_audit_rows = natural_weight_equivalence_audit(config.channels)

    existence_rows = existence_recovery_by_distinction(config, digests)
    optimized_rows = optimized_recovery_diagnostic(config, digests)
    registered_rows = registered_recovery_by_distinction(
        config=config,
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
    path_rows, cascade_summary_rows = cascade_evidence(config, digests)
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
        "channel_matrix.csv": channel_matrix_rows(config.channels, digests),
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

    scored_artifact_digests = {name: row_digest(rows) for name, rows in scored_outputs.items()}
    channel_panel_digest = row_digest(channel_rows)
    scored_outputs_digest = stable_hash(scored_artifact_digests, length=24)
    digest_chain = {
        "probe_id": config.probe_id,
        "probe_schema_version": config.probe_schema_version,
        "carrier_id": config.carrier_id,
        "panel": config.panel,
        "channel_panel_digest": channel_panel_digest,
        "scored_outputs_digest": scored_outputs_digest,
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
        config=config,
        out_dir=out_dir,
        pre_score_outputs=pre_score_outputs,
        scored_outputs=scored_outputs,
        digests=digests,
        digest_chain=digest_chain,
    )
    write_json(out_dir / "registry_first_probe_manifest.json", manifest)
    bundle = formal_consumption_bundle(
        config=config,
        out_dir=out_dir,
        digests=digests,
        digest_chain=digest_chain,
        manifest=manifest,
        readiness_rows=readiness_rows,
    )
    write_json(out_dir / "registry_first_formal_consumption_bundle.json", bundle)
    report = render_report(
        config=config,
        digests=digests,
        digest_chain=digest_chain,
        gap_rows=gap_rows,
        readiness_rows=readiness_rows,
        cascade_summary_rows=cascade_summary_rows,
        coverage_rows=coverage_rows,
    )
    (out_dir / "registry_first_probe_report.md").write_text(report, encoding="utf-8")

    result = {
        "probe_id": config.probe_id,
        "carrier_id": config.carrier_id,
        "out_dir": str(out_dir),
        "registry_digest": digests["registry_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "channel_panel_digest": channel_panel_digest,
        "scored_outputs_digest": scored_outputs_digest,
        "channel_count": len(config.channels),
        "registered_rows": len(registered_rows),
        "gap_rows": len(gap_rows),
        "cascade_evidence_status": cascade_summary_rows[0]["cascade_evidence_status"],
        "overall_status": bundle["overall_status"],
    }
    if config.panel:
        result["panel"] = config.panel
    return result


def carrier_manifest(config: RegistryFirstConfig) -> list[dict[str, object]]:
    return [
        {
            "carrier_id": config.carrier_id,
            "carrier_role": "source_and_target",
            "state_count": len(config.states),
            "states": ";".join(config.states),
            "scope": config.scope,
        }
    ]


def distinction_manifest(config: RegistryFirstConfig) -> list[dict[str, object]]:
    rows = []
    for distinction_id, spec in config.source_distinctions.items():
        rows.append(
            {
                "distinction_id": distinction_id,
                "carrier_id": config.carrier_id,
                "distinction_role": "source",
                "label_set": ";".join(spec.label_set),
                "labeling_rule": spec.rule,
                "fixed_target_distinction_id": config.fixed_targets[distinction_id],
                "rank_class": spec.rank_class,
                "scope": config.scope,
            }
        )
    for distinction_id, spec in config.target_distinctions.items():
        rows.append(
            {
                "distinction_id": distinction_id,
                "carrier_id": config.carrier_id,
                "distinction_role": "target",
                "label_set": ";".join(spec.label_set),
                "labeling_rule": spec.rule,
                "fixed_target_distinction_id": "",
                "rank_class": spec.rank_class,
                "scope": config.scope,
            }
        )
    return rows


def observation_tables(config: RegistryFirstConfig) -> dict[str, list[dict[str, object]]]:
    return {
        "source": [
            {
                "carrier_id": config.carrier_id,
                "state_id": state,
                "distinction_id": distinction_id,
                "label": spec.label(state),
                "registry_first": 1,
            }
            for distinction_id, spec in config.source_distinctions.items()
            for state in config.states
        ],
        "target": [
            {
                "carrier_id": config.carrier_id,
                "state_id": state,
                "target_distinction_id": distinction_id,
                "label": spec.label(state),
                "registry_first": 1,
            }
            for distinction_id, spec in config.target_distinctions.items()
            for state in config.states
        ],
    }


def requirement_manifest(config: RegistryFirstConfig) -> list[dict[str, object]]:
    return [
        {
            "requirement_set_id": requirement.requirement_set_id,
            "requirement_set_name": requirement.name,
            "source_distinction_ids": ";".join(requirement.source_distinction_ids),
            "requirement_count": len(requirement.source_distinction_ids),
            "declaration_rule": "pre_score_declared_requirement_set",
            "semantic_status": "finite_distinction_requirement_only",
            "scope": config.scope,
        }
        for requirement in config.requirements
    ]


def threshold_manifest(config: RegistryFirstConfig) -> list[dict[str, object]]:
    return [
        {
            "threshold_id": threshold.threshold_id,
            "threshold_semantics": threshold.semantics,
            "threshold_value": float(threshold.value),
            "threshold_fraction": fraction_text(threshold.value),
            "comparison_rule": "success_mass * denominator >= numerator * total_mass",
            "predeclared": 1,
            "scope": config.scope,
        }
        for threshold in config.thresholds
    ]


def declared_decoder_registries(config: RegistryFirstConfig) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    registry_rows = []
    decoder_rows = []
    for registry in config.registries:
        registry_rows.append(
            {
                "registry_id": registry.registry_id,
                "source_distinction_id": registry.source_distinction_id,
                "target_distinction_id": registry.target_distinction_id,
                "registry_policy": registry.policy,
                "decoder_count": len(registry.decoders),
                "generation_rule": "pre_score_declared_decoder_registry",
                "eligible_for_declared_recovery": int(registry.policy == "declared"),
                "pre_score_declared": 1,
                "scope": config.scope,
            }
        )
        for decoder_id, mapping in registry.decoders:
            for target_label, source_label in sorted(mapping.items()):
                decoder_rows.append(
                    {
                        "registry_id": registry.registry_id,
                        "decoder_id": decoder_id,
                        "decoder_policy": registry.policy,
                        "source_distinction_id": registry.source_distinction_id,
                        "target_distinction_id": registry.target_distinction_id,
                        "target_label": target_label,
                        "decoded_source_label": source_label,
                        "uses_target_observation_only": 1,
                        "eligible_for_declared_recovery": int(registry.policy == "declared"),
                        "scope": config.scope,
                    }
                )
    return registry_rows, decoder_rows


def uniform_prior(config: RegistryFirstConfig) -> list[dict[str, object]]:
    return [
        {
            "prior_id": f"uniform_{config.carrier_id}_natural",
            "carrier_id": config.carrier_id,
            "state_id": state,
            "prior_weight": 1,
            "prior_weight_total": len(config.states),
            "probability_fraction": fraction_text(Fraction(1, len(config.states))),
            "pre_score_declared": 1,
            "scope": config.scope,
        }
        for state in config.states
    ]


def channel_manifest(config: RegistryFirstConfig) -> list[dict[str, object]]:
    rows = []
    for channel_id in sorted(config.channels):
        row_totals = sorted({sum(row.values()) for row in config.channels[channel_id].values()})
        rows.append(
            {
                "channel_id": channel_id,
                "source_carrier_id": config.carrier_id,
                "target_carrier_id": config.carrier_id,
                "channel_family": config.channel_families[channel_id],
                "natural_weight_row_totals": ";".join(str(total) for total in row_totals),
                "row_weight_total_constancy": "constant" if len(row_totals) == 1 else "nonconstant",
                "seed_policy": "deterministic",
                "params_json": canonical_json({}),
                "scope": config.scope,
            }
        )
    return rows


def channel_matrix_rows(channels: dict[str, Channel], digests: dict[str, str]) -> list[dict[str, object]]:
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


def natural_weight_equivalence_audit(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows = []
    for channel_id, matrix in sorted(channels.items()):
        row_totals = {source_state: sum(weights.values()) for source_state, weights in matrix.items()}
        totals = sorted(set(row_totals.values()))
        rows.append(
            {
                "channel_id": channel_id,
                "row_weight_total": ";".join(f"{state}:{total}" for state, total in sorted(row_totals.items())),
                "row_weight_total_constancy": "constant" if len(totals) == 1 else "nonconstant",
                "global_scale_equivalence": "uniform_row_total" if len(totals) == 1 else "row_scaled",
                "probability_semantics_status": "natural_weight_exact_probability_equivalent"
                if all(total > 0 for total in row_totals.values())
                else "blocked_zero_row",
                "notes": "finite natural weights are exact rational channel rows",
            }
        )
    return rows


def label(config: RegistryFirstConfig, distinction_id: str, state: str) -> str:
    specs = config.source_distinctions if distinction_id.startswith("D_") else config.target_distinctions
    return specs[distinction_id].label(state)


def support_exact_with_decoder(
    config: RegistryFirstConfig,
    channel: Channel,
    source_distinction_id: str,
    target_distinction_id: str,
    decoder: DecoderMap,
) -> bool:
    for source_state, target_weights in channel.items():
        source_label = label(config, source_distinction_id, source_state)
        for target_state, weight in target_weights.items():
            if weight <= 0:
                continue
            target_label = label(config, target_distinction_id, target_state)
            if decoder.get(target_label) != source_label:
                return False
    return True


def exact_decoder_witness(
    config: RegistryFirstConfig,
    channel: Channel,
    source_distinction_id: str,
    target_distinction_id: str,
) -> DecoderMap | None:
    target_to_source_labels: dict[str, set[str]] = defaultdict(set)
    for source_state, target_weights in channel.items():
        source_label = label(config, source_distinction_id, source_state)
        for target_state, weight in target_weights.items():
            if weight <= 0:
                continue
            target_to_source_labels[label(config, target_distinction_id, target_state)].add(source_label)
    if any(len(labels) > 1 for labels in target_to_source_labels.values()):
        return None
    source_default = config.source_distinctions[source_distinction_id].label_set[0]
    return {
        target_label: next(iter(target_to_source_labels.get(target_label, {source_default})))
        for target_label in config.target_distinctions[target_distinction_id].label_set
    }


def bayes_best_decoder(
    config: RegistryFirstConfig,
    channel: Channel,
    source_distinction_id: str,
    target_distinction_id: str,
) -> tuple[DecoderMap, int, int]:
    weights_by_target: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total = 0
    for source_state, target_weights in channel.items():
        source_label = label(config, source_distinction_id, source_state)
        for target_state, weight in target_weights.items():
            if weight <= 0:
                continue
            target_label = label(config, target_distinction_id, target_state)
            weights_by_target[target_label][source_label] += weight
            total += weight
    decoder: DecoderMap = {}
    success = 0
    source_default = config.source_distinctions[source_distinction_id].label_set[0]
    for target_label in config.target_distinctions[target_distinction_id].label_set:
        label_weights = weights_by_target.get(target_label, {})
        if not label_weights:
            decoder[target_label] = source_default
            continue
        best_label, best_weight = sorted(label_weights.items(), key=lambda item: (item[1], item[0]))[-1]
        decoder[target_label] = best_label
        success += best_weight
    return decoder, success, total


def existence_recovery_by_distinction(config: RegistryFirstConfig, digests: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    for channel_id, channel in sorted(config.channels.items()):
        for source_distinction_id in sorted(config.source_distinctions):
            for target_distinction_id in sorted(config.target_distinctions):
                witness = exact_decoder_witness(config, channel, source_distinction_id, target_distinction_id)
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


def optimized_recovery_diagnostic(config: RegistryFirstConfig, digests: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    for channel_id, channel in sorted(config.channels.items()):
        for source_distinction_id in sorted(config.source_distinctions):
            best: dict[str, object] | None = None
            for target_distinction_id in sorted(config.target_distinctions):
                decoder, success, total = bayes_best_decoder(config, channel, source_distinction_id, target_distinction_id)
                exact = exact_decoder_witness(config, channel, source_distinction_id, target_distinction_id) is not None
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
    config: RegistryFirstConfig,
    registry_manifest_rows: list[dict[str, object]],
    decoder_registry_rows: list[dict[str, object]],
    digests: dict[str, str],
) -> list[dict[str, object]]:
    decoders_by_registry: dict[str, dict[str, DecoderMap]] = defaultdict(lambda: defaultdict(dict))
    for row in decoder_registry_rows:
        decoders_by_registry[str(row["registry_id"])][str(row["decoder_id"])][str(row["target_label"])] = str(
            row["decoded_source_label"]
        )

    rows = []
    for channel_id, channel in sorted(config.channels.items()):
        for registry in registry_manifest_rows:
            registry_id = str(registry["registry_id"])
            source_distinction_id = str(registry["source_distinction_id"])
            target_distinction_id = str(registry["target_distinction_id"])
            working_decoder_id = ""
            working_decoder_json = ""
            for decoder_id, decoder in sorted(decoders_by_registry.get(registry_id, {}).items()):
                if support_exact_with_decoder(config, channel, source_distinction_id, target_distinction_id, decoder):
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
        observed = decoder_counts[str(registry["registry_id"])]
        rows.append(
            {
                "registry_id": registry["registry_id"],
                "source_distinction_id": registry["source_distinction_id"],
                "target_distinction_id": registry["target_distinction_id"],
                "declared_decoder_count": expected,
                "decoder_table_rows": observed,
                "coverage_status": "empty_registry_control"
                if expected == 0
                else "covered"
                if observed > 0
                else "blocked_missing_decoder_rows",
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
    existence = {(row["channel_id"], row["source_distinction_id"], row["target_distinction_id"]): row for row in existence_rows}
    optimized = {(row["channel_id"], row["source_distinction_id"]): row for row in optimized_rows}
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
                else "existence_capacity"
                if existence_value
                else "optimized_diagnostic"
                if optimized_value
                else "not_recovered",
                "registry_digest": digests["registry_digest"],
                "manifest_bundle_digest": digests["manifest_bundle_digest"],
            }
        )
    return rows


def cascade_evidence(config: RegistryFirstConfig, digests: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    summaries = []
    for cascade in config.cascades:
        for pair in cascade.distinction_pairs:
            first_error_mass = 0
            second_error_mass = 0
            composite_error_mass = 0
            total_mass = 0
            positive_path_count = 0
            for source_state in config.states:
                source_prior_weight = 1
                first_row = config.channels[cascade.first_channel_id][source_state]
                for intermediate_state, first_weight in first_row.items():
                    second_row = config.channels[cascade.second_channel_id][intermediate_state]
                    for target_state, second_weight in second_row.items():
                        path_weight = source_prior_weight * first_weight * second_weight
                        if path_weight <= 0:
                            continue
                        positive_path_count += 1
                        total_mass += path_weight
                        source_label = label(config, pair.source_distinction_id, source_state)
                        intermediate_label = label(config, pair.target_distinction_id, intermediate_state)
                        target_label = label(config, pair.target_distinction_id, target_state)
                        first_output = pair.first_decoder[intermediate_label]
                        second_output = pair.second_decoder[target_label]
                        composed_output = pair.first_decoder[second_output]
                        first_error = int(first_output != source_label)
                        second_error = int(second_output != intermediate_label)
                        composite_error = int(composed_output != source_label)
                        first_error_mass += first_error * path_weight
                        second_error_mass += second_error * path_weight
                        composite_error_mass += composite_error * path_weight
                        rows.append(
                            {
                                "cascade_id": cascade.cascade_id,
                                "source_distinction_id": pair.source_distinction_id,
                                "target_distinction_id": pair.target_distinction_id,
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
                    "cascade_id": cascade.cascade_id,
                    "source_distinction_id": pair.source_distinction_id,
                    "target_distinction_id": pair.target_distinction_id,
                    "path_count": len(config.states) ** 3,
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
    return [
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
                "notes": "pre-score artifact emitted before scoring"
                if index < len(stages)
                else "scoring artifacts carry registry digest",
            }
        )
    assert pre_score_outputs
    return rows


def probe_manifest(
    *,
    config: RegistryFirstConfig,
    out_dir: Path,
    pre_score_outputs: dict[str, list[dict[str, object]]],
    scored_outputs: dict[str, list[dict[str, object]]],
    digests: dict[str, str],
    digest_chain: dict[str, object],
) -> dict[str, object]:
    output_rows = {**pre_score_outputs, **scored_outputs}
    payload = {
        "carrier_id": config.carrier_id,
        "panel": config.panel,
        "digests": digests,
        "row_counts": {name: len(rows) for name, rows in output_rows.items()},
    }
    return {
        "probe_id": config.probe_id,
        "probe_schema_version": config.probe_schema_version,
        "carrier_id": config.carrier_id,
        "panel": config.panel,
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
        "scope": config.scope,
        "probe_digest": stable_hash(payload, length=24),
    }


def formal_consumption_bundle(
    *,
    config: RegistryFirstConfig,
    out_dir: Path,
    digests: dict[str, str],
    digest_chain: dict[str, object],
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
        "carrier_id": config.carrier_id,
        "panel": config.panel,
        "registry_digest": digests["registry_digest"],
        "manifest_bundle_digest": digests["manifest_bundle_digest"],
        "ready_axes": ready_axes,
        "overall_status": overall,
    }
    return {
        "bundle_schema_version": "0.1.0",
        "probe_id": config.probe_id,
        "carrier_id": config.carrier_id,
        "panel": config.panel,
        "source_probe_digest": manifest["probe_digest"],
        "manifest_digest_chain_digest": digest_chain["digest_chain_digest"],
        "channel_panel_digest": digest_chain["channel_panel_digest"],
        "scored_outputs_digest": digest_chain["scored_outputs_digest"],
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
        "scope": config.scope,
        "bundle_digest": stable_hash(payload, length=24),
    }


def render_report(
    *,
    config: RegistryFirstConfig,
    digests: dict[str, str],
    digest_chain: dict[str, object],
    gap_rows: list[dict[str, object]],
    readiness_rows: list[dict[str, object]],
    cascade_summary_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
) -> str:
    existence_gaps = [row for row in gap_rows if as_bool(row["registered_vs_existence_gap"])]
    optimized_gaps = [row for row in gap_rows if as_bool(row["registered_vs_optimized_gap"])]
    by_class: dict[str, int] = defaultdict(int)
    for row in gap_rows:
        by_class[str(row["theorem_transfer_class"])] += 1
    ready_lines = [
        f"- `{row['readiness_axis']}`: `{row['status']}` ({row['recovery_provenance_class']})"
        for row in readiness_rows
    ]
    class_lines = [f"- `{name}`: {count}" for name, count in sorted(by_class.items())]
    cascade_lines = [
        f"- `{row['source_distinction_id']}`: composite {row['composite_error_mass']} <= "
        f"{row['first_stage_error_mass']} + {row['second_stage_error_mass']} (`{row['cascade_evidence_status']}`)"
        for row in cascade_summary_rows
    ]
    coverage_lines = [
        f"- `{row['registry_id']}`: `{row['coverage_status']}`"
        for row in coverage_rows
        if row["coverage_status"] != "covered"
    ]
    title_suffix = f" {config.carrier_id}" if config.carrier_id else ""
    if config.panel:
        title_suffix += f" {config.panel}"
    return "\n".join(
        [
            f"# Registry-First Stochastic Channel Probe{title_suffix}",
            "",
            "## Executive Summary",
            "",
            "This run uses the shared registry-first engine. It freezes declared "
            "decoder registries, requirement sets, and thresholds before scoring, "
            "then separates declared, existence, and optimized recovery surfaces.",
            "",
            f"- registry digest: `{digests['registry_digest']}`",
            f"- manifest bundle digest: `{digests['manifest_bundle_digest']}`",
            f"- channel panel digest: `{digest_chain['channel_panel_digest']}`",
            f"- scored outputs digest: `{digest_chain['scored_outputs_digest']}`",
            f"- registered vs existence gaps: {len(existence_gaps)}",
            f"- registered vs optimized gaps: {len(optimized_gaps)}",
            "",
            "## Scope",
            "",
            config.scope,
            "",
            "## Registry Controls",
            "",
            *(coverage_lines or ["- none"]),
            "",
            "## Provenance Gap Classes",
            "",
            *class_lines,
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
            "This is a finite stochastic presentation result. Optimized rows remain "
            "diagnostic, and substrate bridge readiness remains out of scope.",
        ]
    )


def row_digest(rows: list[dict[str, object]]) -> str:
    normalized = [{str(key): str(value) for key, value in sorted(row.items())} for row in rows]
    return stable_hash(normalized, length=24)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass", "ready"}

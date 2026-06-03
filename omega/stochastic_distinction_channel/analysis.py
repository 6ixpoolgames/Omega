"""Decoder, recoverability, baseline, and composition analysis."""

from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction

from .construct import label_for
from .schema import CLAIM_BOUNDARY, canonical_json, decimal, fraction_text, ratio, safe_id


def matrix_rows(
    channel_rows: list[dict[str, object]],
    matrices: dict[str, dict[str, dict[str, Fraction]]],
) -> list[dict[str, object]]:
    meta = {str(row["channel_id"]): row for row in channel_rows}
    rows = []
    for channel_id, matrix in matrices.items():
        for source_state, targets in matrix.items():
            for target_state, probability in targets.items():
                rows.append(
                    {
                        "channel_id": channel_id,
                        "source_carrier_id": meta[channel_id]["source_carrier_id"],
                        "target_carrier_id": meta[channel_id]["target_carrier_id"],
                        "source_state": source_state,
                        "target_state": target_state,
                        "probability": decimal(probability),
                        "probability_fraction": fraction_text(probability),
                        "claim_boundary": CLAIM_BOUNDARY,
                    }
                )
    return rows


def support_rows(matrix_rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in matrix_rows_in:
        probability = Fraction(str(row["probability_fraction"]))
        if probability <= 0:
            continue
        out = dict(row)
        out["support"] = 1
        out["support_rule"] = "K(y|x) > 0"
        rows.append(out)
    return rows


def row_stochastic_audit(
    channel_rows: list[dict[str, object]],
    matrices: dict[str, dict[str, dict[str, Fraction]]],
) -> list[dict[str, object]]:
    rows = []
    for channel in channel_rows:
        channel_id = str(channel["channel_id"])
        for source_state, targets in matrices[channel_id].items():
            row_sum = sum(targets.values(), Fraction(0))
            rows.append(
                {
                    "channel_id": channel_id,
                    "source_state": source_state,
                    "row_sum": decimal(row_sum),
                    "row_sum_fraction": fraction_text(row_sum),
                    "status": "PASS" if row_sum == 1 else "FAIL",
                }
            )
    return rows


def distinction_partition_audit(
    carrier_map: dict[str, list[str]],
    distinctions: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows = []
    for spec in distinctions:
        carrier_id = str(spec["carrier_id"])
        states = carrier_map[carrier_id]
        labels = [label_for(str(spec["distinction_id"]), state) for state in states]
        declared = set(str(spec["label_set"]).split(";"))
        observed = set(labels)
        rows.append(
            {
                "distinction_id": spec["distinction_id"],
                "carrier_id": carrier_id,
                "state_count": len(states),
                "declared_label_count": len(declared),
                "observed_label_count": len(observed),
                "all_states_labeled": int(len(labels) == len(states)),
                "observed_subset_of_declared": int(observed.issubset(declared)),
                "status": "PASS" if observed.issubset(declared) and len(labels) == len(states) else "FAIL",
            }
        )
    return rows


def build_recoverability(
    *,
    channel_rows: list[dict[str, object]],
    matrices: dict[str, dict[str, dict[str, Fraction]]],
    carrier_map: dict[str, list[str]],
    distinctions: list[dict[str, object]],
    prior_rows: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    distinctions_by_carrier: dict[str, list[dict[str, object]]] = defaultdict(list)
    for spec in distinctions:
        distinctions_by_carrier[str(spec["carrier_id"])].append(spec)
    priors = priors_by_carrier(prior_rows)

    decoder_manifest: list[dict[str, object]] = []
    decoder_table: list[dict[str, object]] = []
    recoverability: list[dict[str, object]] = []
    confusion: list[dict[str, object]] = []
    support_recoverability_rows: list[dict[str, object]] = []

    for channel in channel_rows:
        channel_id = str(channel["channel_id"])
        source_carrier = str(channel["source_carrier_id"])
        target_carrier = str(channel["target_carrier_id"])
        prior_id = f"uniform_{source_carrier}"
        prior = priors[source_carrier]
        for source_dist in distinctions_by_carrier[source_carrier]:
            for target_dist in distinctions_by_carrier[target_carrier]:
                pair = analyze_pair(
                    channel_id=channel_id,
                    matrix=matrices[channel_id],
                    source_dist=source_dist,
                    target_dist=target_dist,
                    prior=prior,
                )
                support_recoverability_rows.append(support_recoverability_row(channel, source_dist, target_dist, pair))
                decoder_specs = decoder_specs_for_pair(channel, source_dist, target_dist, pair, prior_id)
                for decoder in decoder_specs:
                    decoder_manifest.append(decoder["manifest"])
                    decoder_table.extend(decoder["table"])
                    metric = score_decoder(pair, decoder["mapping"])
                    recoverability.append(
                        recoverability_row(
                            channel=channel,
                            source_dist=source_dist,
                            target_dist=target_dist,
                            prior_id=prior_id,
                            decoder=decoder,
                            pair=pair,
                            metric=metric,
                        )
                    )
                    confusion.extend(confusion_rows(channel, source_dist, target_dist, prior_id, decoder, pair))
    return {
        "decoder_manifest": decoder_manifest,
        "decoder_table": decoder_table,
        "recoverability": recoverability,
        "confusion": confusion,
        "support_recoverability": support_recoverability_rows,
    }


def analyze_pair(
    *,
    channel_id: str,
    matrix: dict[str, dict[str, Fraction]],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    prior: dict[str, Fraction],
) -> dict[str, object]:
    source_labels = str(source_dist["label_set"]).split(";")
    target_labels = str(target_dist["label_set"]).split(";")
    joint: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    support_sources_by_target: dict[str, set[str]] = defaultdict(set)
    source_label_prior: dict[str, Fraction] = defaultdict(Fraction)
    for source_state, target_probs in matrix.items():
        source_label = label_for(str(source_dist["distinction_id"]), source_state)
        source_label_prior[source_label] += prior[source_state]
        for target_state, probability in target_probs.items():
            target_label = label_for(str(target_dist["distinction_id"]), target_state)
            mass = prior[source_state] * probability
            joint[(source_label, target_label)] += mass
            if probability > 0:
                support_sources_by_target[target_label].add(source_label)
    exact_support = all(len(support_sources_by_target[label]) <= 1 for label in target_labels)
    bayes_mapping = {}
    for target_label in target_labels:
        best = max(
            source_labels,
            key=lambda source_label: (joint[(source_label, target_label)], source_label),
        )
        bayes_mapping[target_label] = best
    exact_mapping = {
        target_label: next(iter(sources)) if sources else source_labels[0]
        for target_label, sources in support_sources_by_target.items()
    }
    for target_label in target_labels:
        exact_mapping.setdefault(target_label, source_labels[0])
    chance = max(source_label_prior.values()) if source_label_prior else Fraction(0)
    return {
        "channel_id": channel_id,
        "source_labels": source_labels,
        "target_labels": target_labels,
        "joint": joint,
        "source_label_prior": source_label_prior,
        "bayes_mapping": bayes_mapping,
        "exact_mapping": exact_mapping,
        "exact_support": exact_support,
        "chance_success": chance,
    }


def decoder_specs_for_pair(
    channel: dict[str, object],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    pair: dict[str, object],
    prior_id: str,
) -> list[dict[str, object]]:
    specs = [
        make_decoder(
            channel,
            source_dist,
            target_dist,
            prior_id,
            "bayes_optimal_decoder",
            pair["bayes_mapping"],  # type: ignore[arg-type]
            "minimizes error under declared source prior",
        )
    ]
    if pair["exact_support"]:
        specs.append(
            make_decoder(
                channel,
                source_dist,
                target_dist,
                prior_id,
                "exact_decoder",
                pair["exact_mapping"],  # type: ignore[arg-type]
                "exact support decoder exists",
            )
        )
    if set(pair["source_labels"]) == set(pair["target_labels"]):
        mapping = {label: label for label in pair["target_labels"]}  # type: ignore[index]
        specs.append(
            make_decoder(
                channel,
                source_dist,
                target_dist,
                prior_id,
                "declared_decoder",
                mapping,
                "fixed same-label decoder rule",
            )
        )
    return specs


def make_decoder(
    channel: dict[str, object],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    prior_id: str,
    decoder_kind: str,
    mapping: dict[str, str],
    rule: str,
) -> dict[str, object]:
    decoder_id = (
        f"dec::{channel['channel_id']}::{source_dist['distinction_id']}::"
        f"{target_dist['distinction_id']}::{decoder_kind}"
    )
    manifest = {
        "decoder_id": decoder_id,
        "source_distinction_id": source_dist["distinction_id"],
        "target_distinction_id": target_dist["distinction_id"],
        "channel_id": channel["channel_id"],
        "prior_id": prior_id,
        "decoder_kind": decoder_kind,
        "decoder_rule": rule,
        "observation_scope": target_dist["observation_scope"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    table = [
        {
            "decoder_id": decoder_id,
            "target_label": target_label,
            "decoded_source_label": source_label,
            "decoder_kind": decoder_kind,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for target_label, source_label in sorted(mapping.items())
    ]
    return {"manifest": manifest, "table": table, "mapping": mapping}


def score_decoder(pair: dict[str, object], mapping: dict[str, str]) -> dict[str, Fraction]:
    joint: dict[tuple[str, str], Fraction] = pair["joint"]  # type: ignore[assignment]
    success = Fraction(0)
    for (source_label, target_label), mass in joint.items():
        if mapping.get(target_label) == source_label:
            success += mass
    chance = pair["chance_success"]  # type: ignore[assignment]
    advantage = Fraction(0) if chance == 1 else (success - chance) / (1 - chance)
    return {
        "success": success,
        "error": 1 - success,
        "chance": chance,
        "excess": success - chance,
        "advantage": advantage,
    }


def recoverability_row(
    *,
    channel: dict[str, object],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    prior_id: str,
    decoder: dict[str, object],
    pair: dict[str, object],
    metric: dict[str, Fraction],
) -> dict[str, object]:
    success = metric["success"]
    chance = metric["chance"]
    return {
        "channel_id": channel["channel_id"],
        "source_carrier_id": channel["source_carrier_id"],
        "target_carrier_id": channel["target_carrier_id"],
        "source_distinction_id": source_dist["distinction_id"],
        "target_distinction_id": target_dist["distinction_id"],
        "decoder_id": decoder["manifest"]["decoder_id"],  # type: ignore[index]
        "decoder_kind": decoder["manifest"]["decoder_kind"],  # type: ignore[index]
        "prior_id": prior_id,
        "observation_scope": target_dist["observation_scope"],
        "exact_recoverable_support": int(bool(pair["exact_support"])),
        "decoder_success_probability": float(success),
        "decoder_success_fraction": fraction_text(success),
        "decoder_error_probability": float(metric["error"]),
        "decoder_error_fraction": fraction_text(metric["error"]),
        "chance_success_probability": float(chance),
        "chance_success_fraction": fraction_text(chance),
        "excess_success_over_chance": float(metric["excess"]),
        "normalized_recovery_advantage": float(metric["advantage"]),
        "bayes_error": float(1 - score_decoder(pair, pair["bayes_mapping"])["success"]),  # type: ignore[arg-type]
        "threshold_id": "high_recovery",
        "threshold_value": 0.95,
        "passes_threshold": int(success >= Fraction(19, 20)),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def confusion_rows(
    channel: dict[str, object],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    prior_id: str,
    decoder: dict[str, object],
    pair: dict[str, object],
) -> list[dict[str, object]]:
    mapping: dict[str, str] = decoder["mapping"]  # type: ignore[assignment]
    rows = []
    joint: dict[tuple[str, str], Fraction] = pair["joint"]  # type: ignore[assignment]
    for (source_label, target_label), mass in sorted(joint.items()):
        rows.append(
            {
                "channel_id": channel["channel_id"],
                "source_distinction_id": source_dist["distinction_id"],
                "target_distinction_id": target_dist["distinction_id"],
                "decoder_id": decoder["manifest"]["decoder_id"],  # type: ignore[index]
                "prior_id": prior_id,
                "source_label": source_label,
                "target_observation_label": target_label,
                "decoded_source_label": mapping.get(target_label, ""),
                "probability": float(mass),
                "probability_fraction": fraction_text(mass),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def support_recoverability_row(
    channel: dict[str, object],
    source_dist: dict[str, object],
    target_dist: dict[str, object],
    pair: dict[str, object],
) -> dict[str, object]:
    return {
        "channel_id": channel["channel_id"],
        "source_distinction_id": source_dist["distinction_id"],
        "target_distinction_id": target_dist["distinction_id"],
        "support_relation_rule": "K(y|x) > 0",
        "exact_support_recoverability": int(bool(pair["exact_support"])),
        "disttrans_candidate": int(bool(pair["exact_support"])),
        "observation_scope": target_dist["observation_scope"],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def decoder_totality_audit(
    decoder_manifest: list[dict[str, object]],
    decoder_table: list[dict[str, object]],
    distinctions: list[dict[str, object]],
) -> list[dict[str, object]]:
    labels_by_dist = {
        str(row["distinction_id"]): set(str(row["label_set"]).split(";"))
        for row in distinctions
    }
    rows_by_decoder: dict[str, set[str]] = defaultdict(set)
    for row in decoder_table:
        rows_by_decoder[str(row["decoder_id"])].add(str(row["target_label"]))
    rows = []
    for decoder in decoder_manifest:
        decoder_id = str(decoder["decoder_id"])
        expected = labels_by_dist[str(decoder["target_distinction_id"])]
        observed = rows_by_decoder[decoder_id]
        rows.append(
            {
                "decoder_id": decoder_id,
                "target_distinction_id": decoder["target_distinction_id"],
                "expected_target_label_count": len(expected),
                "observed_decoder_label_count": len(observed),
                "missing_target_labels": ";".join(sorted(expected - observed)),
                "status": "PASS" if expected == observed else "FAIL",
            }
        )
    return rows


def threshold_application_audit(recoverability: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    thresholds = [
        ("exact_error_zero", "decoder_error_probability", 0.0, "=="),
        ("high_recovery", "decoder_success_probability", 0.95, ">="),
        ("moderate_recovery", "decoder_success_probability", 0.75, ">="),
    ]
    for row in recoverability:
        for threshold_id, metric, value, op in thresholds:
            measured = float(row[metric])
            if op == "==":
                passed = measured == value
            else:
                passed = measured >= value
            rows.append(
                {
                    "channel_id": row["channel_id"],
                    "source_distinction_id": row["source_distinction_id"],
                    "target_distinction_id": row["target_distinction_id"],
                    "decoder_id": row["decoder_id"],
                    "threshold_id": threshold_id,
                    "metric": metric,
                    "measured_value": measured,
                    "threshold_value": value,
                    "passes_threshold": int(passed),
                    "status": "PASS",
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def best_recoverability_index(recoverability: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    best: dict[tuple[str, str], dict[str, object]] = {}
    for row in recoverability:
        if row["decoder_kind"] != "bayes_optimal_decoder":
            continue
        key = (str(row["channel_id"]), str(row["source_distinction_id"]))
        current = best.get(key)
        if current is None or float(row["decoder_success_probability"]) > float(current["decoder_success_probability"]):
            best[key] = row
    return best


def non_erasure_tables(recoverability: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    requirement_rows = [
        ("req_marginals", ["D_A", "D_B"]),
        ("req_joint", ["D_joint"]),
        ("req_parity", ["D_parity"]),
        ("req_all_nontrivial", ["D_A", "D_B", "D_joint", "D_parity"]),
    ]
    manifest = [
        {
            "requirement_set_id": req_id,
            "distinction_ids": ";".join(dist_ids),
            "declaration_rule": "predeclared source distinction set",
            "semantic_status": "finite_stochastic_channel_only",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for req_id, dist_ids in requirement_rows
    ]
    best = best_recoverability_index(recoverability)
    channel_ids = sorted({str(row["channel_id"]) for row in recoverability if str(row["source_carrier_id"]) == "X2"})
    rows = []
    for channel_id in channel_ids:
        for req_id, dist_ids in requirement_rows:
            recovered = [dist for dist in dist_ids if best.get((channel_id, dist), {}).get("passes_threshold") in (1, "1")]
            rows.append(
                {
                    "requirement_set_id": req_id,
                    "channel_id": channel_id,
                    "decoder_policy": "bayes_best_target_distinction",
                    "threshold_id": "high_recovery",
                    "required_count": len(dist_ids),
                    "recovered_count": len(recovered),
                    "not_recovered_count": len(dist_ids) - len(recovered),
                    "non_erasing_status": "PASS" if len(recovered) == len(dist_ids) else "FAIL",
                    "recovered_distinction_ids": ";".join(recovered),
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return manifest, rows


def marginal_joint_diagnostic(recoverability: list[dict[str, object]]) -> list[dict[str, object]]:
    best = best_recoverability_index(recoverability)
    channel_ids = sorted({str(row["channel_id"]) for row in recoverability if str(row["source_carrier_id"]) == "X2"})
    rows = []
    for channel_id in channel_ids:
        values = {dist: best.get((channel_id, dist), {}) for dist in ["D_A", "D_B", "D_joint", "D_parity"]}
        passes = {dist: values[dist].get("passes_threshold") in (1, "1") for dist in values}
        if passes["D_A"] and passes["D_B"] and passes["D_joint"]:
            diagnostic_class = "marginal_and_joint_recovered"
        elif passes["D_A"] and passes["D_B"] and not passes["D_joint"]:
            diagnostic_class = "marginal_recovered_joint_not_recovered"
        elif passes["D_joint"] and not (passes["D_A"] and passes["D_B"]):
            diagnostic_class = "joint_recovered_marginal_not_recovered"
        elif not any(passes.values()):
            diagnostic_class = "all_nontrivial_lost"
        else:
            diagnostic_class = "mixed_or_partial"
        rows.append(
            {
                "channel_id": channel_id,
                "prior_id": "uniform_X2",
                "decoder_policy": "bayes_best_target_distinction",
                "A_success": values["D_A"].get("decoder_success_probability", ""),
                "B_success": values["D_B"].get("decoder_success_probability", ""),
                "joint_success": values["D_joint"].get("decoder_success_probability", ""),
                "parity_success": values["D_parity"].get("decoder_success_probability", ""),
                "A_observation_scope": values["D_A"].get("observation_scope", ""),
                "B_observation_scope": values["D_B"].get("observation_scope", ""),
                "joint_observation_scope": values["D_joint"].get("observation_scope", ""),
                "parity_observation_scope": values["D_parity"].get("observation_scope", ""),
                "A_passes_threshold": int(passes["D_A"]),
                "B_passes_threshold": int(passes["D_B"]),
                "joint_passes_threshold": int(passes["D_joint"]),
                "parity_passes_threshold": int(passes["D_parity"]),
                "diagnostic_class": diagnostic_class,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def baseline_tables(recoverability: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    baselines = [
        ("identity_channel", "identity_channel"),
        ("total_erasure_channel", "total_erasure_channel"),
        ("independent_noise_matched_channel", "bit_flip_p_0_05"),
        ("output_marginal_matched_channel", "output_marginal_matched_uniform"),
        ("random_channel_same_output_entropy", "random_channel_same_output_entropy_seed_17"),
    ]
    manifest = [
        {
            "baseline_id": baseline_id,
            "baseline_channel_id": channel_id,
            "baseline_role": baseline_id,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for baseline_id, channel_id in baselines
    ]
    best = best_recoverability_index(recoverability)
    target_channels = [
        "marginal_joint_degrade_q_0_10",
        "marginal_joint_degrade_q_0_20",
        "bit_flip_p_0_10",
        "asym_A_preserved_B_noisy_p_0_25",
        "asym_A_noisy_B_preserved_p_0_25",
    ]
    rows = []
    for channel_id in target_channels:
        for baseline_id, baseline_channel_id in baselines:
            for dist in ["D_A", "D_B", "D_joint", "D_parity"]:
                channel_success = float(best.get((channel_id, dist), {}).get("decoder_success_probability", 0))
                baseline_success = float(best.get((baseline_channel_id, dist), {}).get("decoder_success_probability", 0))
                rows.append(
                    {
                        "channel_id": channel_id,
                        "baseline_id": baseline_id,
                        "baseline_channel_id": baseline_channel_id,
                        "source_distinction_id": dist,
                        "channel_best_success": channel_success,
                        "baseline_best_success": baseline_success,
                        "success_delta_vs_baseline": channel_success - baseline_success,
                        "claim_boundary": CLAIM_BOUNDARY,
                    }
                )
    return manifest, rows


def asymmetry_summary_by_channel(
    *,
    channel_rows: list[dict[str, object]],
    matrices: dict[str, dict[str, dict[str, Fraction]]],
    recoverability: list[dict[str, object]],
) -> list[dict[str, object]]:
    best = best_recoverability_index(recoverability)
    rows = []
    for channel in channel_rows:
        channel_id = str(channel["channel_id"])
        matrix = matrices[channel_id]
        probabilities = [prob for target_probs in matrix.values() for prob in target_probs.values()]
        positive = [prob for prob in probabilities if prob > 0]
        row_entropies = [entropy(target_probs.values()) for target_probs in matrix.values()]
        a_success = float(best.get((channel_id, "D_A"), {}).get("decoder_success_probability", 0))
        b_success = float(best.get((channel_id, "D_B"), {}).get("decoder_success_probability", 0))
        joint_success = float(best.get((channel_id, "D_joint"), {}).get("decoder_success_probability", 0))
        parity_success = float(best.get((channel_id, "D_parity"), {}).get("decoder_success_probability", 0))
        rows.append(
            {
                "channel_id": channel_id,
                "channel_family": channel["channel_family"],
                "source_carrier_id": channel["source_carrier_id"],
                "target_carrier_id": channel["target_carrier_id"],
                "max_probability": float(max(probabilities) if probabilities else 0),
                "min_positive_probability": float(min(positive) if positive else 0),
                "mean_row_entropy_bits": sum(row_entropies) / len(row_entropies) if row_entropies else 0,
                "A_best_success": a_success,
                "B_best_success": b_success,
                "joint_best_success": joint_success,
                "parity_best_success": parity_success,
                "A_minus_B_success": a_success - b_success,
                "marginal_mean_minus_joint_success": ((a_success + b_success) / 2) - joint_success,
                "selective_preservation_read": selective_preservation_read(a_success, b_success, joint_success),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def entropy(values) -> float:
    total = sum(values, Fraction(0))
    if total <= 0:
        return 0.0
    out = 0.0
    for value in values:
        if value <= 0:
            continue
        probability = float(value / total)
        out -= probability * math.log2(probability)
    return out


def selective_preservation_read(a_success: float, b_success: float, joint_success: float) -> str:
    if abs(a_success - b_success) >= 0.25:
        return "coordinate_selective"
    if min(a_success, b_success) >= 0.95 and joint_success < 0.95:
        return "marginal_preserved_joint_degraded"
    if max(a_success, b_success, joint_success) <= 0.5:
        return "nontrivial_lost_or_chance"
    return "mixed_or_symmetric"


def channel_baseline_summary_for_report(rows: list[dict[str, object]]) -> list[str]:
    wanted = {
        ("marginal_joint_degrade_q_0_10", "independent_noise_matched_channel"),
        ("marginal_joint_degrade_q_0_10", "identity_channel"),
        ("bit_flip_p_0_10", "identity_channel"),
        ("bit_flip_p_0_10", "total_erasure_channel"),
    }
    out = []
    for row in rows:
        key = (str(row["channel_id"]), str(row["baseline_id"]))
        if key not in wanted or row["source_distinction_id"] not in ("D_A", "D_joint", "D_parity"):
            continue
        out.append(
            f"- `{row['channel_id']}` `{row['source_distinction_id']}` vs "
            f"`{row['baseline_id']}`: delta {float(row['success_delta_vs_baseline']):.6f}"
        )
    return out[:12]


def compose_matrix(
    first: dict[str, dict[str, Fraction]],
    second: dict[str, dict[str, Fraction]],
) -> dict[str, dict[str, Fraction]]:
    out: dict[str, dict[str, Fraction]] = {}
    target_states = sorted({target for row in second.values() for target in row})
    for source_state, middle_probs in first.items():
        row = {target: Fraction(0) for target in target_states}
        for middle_state, p1 in middle_probs.items():
            for target_state, p2 in second[middle_state].items():
                row[target_state] += p1 * p2
        out[source_state] = row
    return out


COMPOSITION_SPECS = [
    ("comp_bitflip_0_10_then_0_25", "bit_flip_p_0_10", "y2_bit_flip_p_0_25"),
    ("comp_identity_then_marginal_degrade_0_10", "identity_channel", "y2_marginal_joint_degrade_q_0_10"),
]


def build_composed_channels(
    matrices: dict[str, dict[str, dict[str, Fraction]]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, dict[str, dict[str, Fraction]]]]:
    specs = [
        ("comp_bitflip_0_10_then_0_25", "bit_flip_p_0_10", "y2_bit_flip_p_0_25"),
        ("comp_identity_then_marginal_degrade_0_10", "identity_channel", "y2_marginal_joint_degrade_q_0_10"),
    ]
    manifest = []
    channel_rows = []
    matrix_rows_out = []
    composed_matrices = {}
    for comp_id, first_id, second_id in specs:
        comp = compose_matrix(matrices[first_id], matrices[second_id])
        composed_matrices[comp_id] = comp
        channel_rows.append(
            {
                "channel_id": comp_id,
                "source_carrier_id": "X2",
                "target_carrier_id": "Y2",
                "channel_family": "composition",
                "params_json": canonical_json({"first_channel_id": first_id, "second_channel_id": second_id}),
                "seed_policy": "deterministic_composition",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
        manifest.append(
            {
                "composition_id": comp_id,
                "first_channel_id": first_id,
                "second_channel_id": second_id,
                "composed_channel_id": comp_id,
                "composition_rule": "K_comp(z|x)=sum_y K2(z|y)K1(y|x)",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
        for source_state, targets in comp.items():
            for target_state, probability in targets.items():
                matrix_rows_out.append(
                    {
                        "composition_id": comp_id,
                        "composed_channel_id": comp_id,
                        "source_state": source_state,
                        "target_state": target_state,
                        "probability": float(probability),
                        "probability_fraction": fraction_text(probability),
                        "claim_boundary": CLAIM_BOUNDARY,
                    }
                )
    return manifest, channel_rows, matrix_rows_out, composed_matrices


def composition_recoverability_checks(recoverability: list[dict[str, object]]) -> list[dict[str, object]]:
    best = best_recoverability_index(recoverability)
    check_rows = []
    for comp_id, first_id, second_id in COMPOSITION_SPECS:
        for source_dist, middle_dist, target_dist in [
            ("D_A", "E_A", "E_A"),
            ("D_B", "E_B", "E_B"),
            ("D_joint", "E_joint", "E_joint"),
            ("D_parity", "E_parity", "E_parity"),
            ("D_trivial", "E_trivial", "E_trivial"),
        ]:
            first_success = float(best.get((first_id, source_dist), {}).get("decoder_success_probability", 0))
            second_success = float(best.get((second_id, middle_dist), {}).get("decoder_success_probability", 0))
            comp_success = float(best.get((comp_id, source_dist), {}).get("decoder_success_probability", 0))
            check_rows.append(
                {
                    "composition_id": comp_id,
                    "source_distinction_id": source_dist,
                    "middle_distinction_id": middle_dist,
                    "target_distinction_id": target_dist,
                    "first_best_success": first_success,
                    "second_best_success": second_success,
                    "composed_best_success": comp_success,
                    "product_success_reference": first_success * second_success,
                    "composition_read": "measured_probability_not_theorem",
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return check_rows


def priors_by_carrier(prior_rows: list[dict[str, object]]) -> dict[str, dict[str, Fraction]]:
    priors: dict[str, dict[str, Fraction]] = defaultdict(dict)
    for row in prior_rows:
        priors[str(row["carrier_id"])][str(row["state_id"])] = Fraction(str(row["probability_fraction"]))
    return priors

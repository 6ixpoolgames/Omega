"""Construct carriers, distinctions, priors, thresholds, and channel matrices."""

from __future__ import annotations

from fractions import Fraction

from .schema import CLAIM_BOUNDARY, bit, canonical_json, flip_bit, fraction_text, parity


def carriers() -> dict[str, list[str]]:
    return {
        "X2": ["00", "01", "10", "11"],
        "Y2": ["00", "01", "10", "11"],
        "Y_A": ["0", "1"],
        "Y_B": ["0", "1"],
        "Y_star": ["*"],
    }


def carrier_manifest_rows(carrier_map: dict[str, list[str]]) -> list[dict[str, object]]:
    return [
        {
            "carrier_id": carrier_id,
            "state_count": len(states),
            "states": ";".join(states),
            "carrier_role": carrier_role(carrier_id),
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for carrier_id, states in carrier_map.items()
    ]


def carrier_role(carrier_id: str) -> str:
    if carrier_id == "X2":
        return "primary_source"
    if carrier_id == "Y2":
        return "primary_target_and_cascade_source"
    return "degraded_target"


def distinction_specs() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    specs = [
        ("X2", "D_A", "first bit A", ["0", "1"], "source_declared"),
        ("X2", "D_B", "second bit B", ["0", "1"], "source_declared"),
        ("X2", "D_joint", "ordered pair (A,B)", ["00", "01", "10", "11"], "source_declared"),
        ("X2", "D_parity", "A xor B", ["0", "1"], "source_declared"),
        ("X2", "D_trivial", "constant distinction", ["*"], "source_declared"),
        ("Y2", "E_A", "first bit A", ["0", "1"], "E_A_only"),
        ("Y2", "E_B", "second bit B", ["0", "1"], "E_B_only"),
        ("Y2", "E_joint", "ordered pair (A,B)", ["00", "01", "10", "11"], "E_A_and_E_B_jointly_available"),
        ("Y2", "E_parity", "A xor B", ["0", "1"], "E_parity"),
        ("Y2", "E_trivial", "constant distinction", ["*"], "trivial_target_observation"),
        ("Y_A", "E_A_marg", "single A bit", ["0", "1"], "E_A_only"),
        ("Y_A", "E_trivial_A", "constant distinction", ["*"], "trivial_target_observation"),
        ("Y_B", "E_B_marg", "single B bit", ["0", "1"], "E_B_only"),
        ("Y_B", "E_trivial_B", "constant distinction", ["*"], "trivial_target_observation"),
        ("Y_star", "E_trivial_star", "constant erased target", ["*"], "degraded_target_observation"),
    ]
    for carrier_id, distinction_id, rule, labels, scope in specs:
        rows.append(
            {
                "distinction_id": distinction_id,
                "carrier_id": carrier_id,
                "label_set": ";".join(labels),
                "labeling_rule": rule,
                "observation_scope": scope,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def label_for(distinction_id: str, state: str) -> str:
    if distinction_id in ("D_A", "E_A"):
        return state[0]
    if distinction_id in ("D_B", "E_B"):
        return state[1]
    if distinction_id in ("D_joint", "E_joint"):
        return state
    if distinction_id in ("D_parity", "E_parity"):
        return parity(state)
    if distinction_id == "E_A_marg":
        return state
    if distinction_id == "E_B_marg":
        return state
    return "*"


def observation_rows(
    carrier_map: dict[str, list[str]],
    distinctions: list[dict[str, object]],
    *,
    table_kind: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in distinctions:
        carrier_id = str(spec["carrier_id"])
        is_source = carrier_id in ("X2", "Y2")
        is_target = carrier_id in ("Y2", "Y_A", "Y_B", "Y_star")
        if table_kind == "source" and not is_source:
            continue
        if table_kind == "target" and not is_target:
            continue
        for state in carrier_map[carrier_id]:
            rows.append(
                {
                    "carrier_id": carrier_id,
                    "state_id": state,
                    "distinction_id": spec["distinction_id"],
                    "label": label_for(str(spec["distinction_id"]), state),
                    "observation_scope": spec["observation_scope"],
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def source_priors(carrier_map: dict[str, list[str]]) -> list[dict[str, object]]:
    rows = []
    for carrier_id in ("X2", "Y2"):
        states = carrier_map[carrier_id]
        probability = Fraction(1, len(states))
        for state in states:
            rows.append(
                {
                    "prior_id": f"uniform_{carrier_id}",
                    "carrier_id": carrier_id,
                    "state_id": state,
                    "probability": float(probability),
                    "probability_fraction": fraction_text(probability),
                    "prior_rule": "uniform_source_prior",
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def thresholds() -> list[dict[str, object]]:
    return [
        {
            "threshold_id": "exact_error_zero",
            "metric": "decoder_error_probability",
            "operator": "==",
            "threshold_value": 0,
            "predeclared": 1,
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "threshold_id": "high_recovery",
            "metric": "decoder_success_probability",
            "operator": ">=",
            "threshold_value": 0.95,
            "predeclared": 1,
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "threshold_id": "moderate_recovery",
            "metric": "decoder_success_probability",
            "operator": ">=",
            "threshold_value": 0.75,
            "predeclared": 1,
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "threshold_id": "chance_baseline",
            "metric": "decoder_success_probability",
            "operator": "compare_to",
            "threshold_value": "best_constant_decoder_under_same_prior",
            "predeclared": 1,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    ]


def channel_definitions() -> tuple[list[dict[str, object]], dict[str, dict[str, dict[str, Fraction]]]]:
    matrices: dict[str, dict[str, dict[str, Fraction]]] = {}
    rows: list[dict[str, object]] = []

    def add(
        channel_id: str,
        source_carrier_id: str,
        target_carrier_id: str,
        family: str,
        matrix: dict[str, dict[str, Fraction]],
        params: dict[str, object] | None = None,
        seed_policy: str = "deterministic",
    ) -> None:
        matrices[channel_id] = matrix
        rows.append(
            {
                "channel_id": channel_id,
                "source_carrier_id": source_carrier_id,
                "target_carrier_id": target_carrier_id,
                "channel_family": family,
                "params_json": canonical_json(params or {}),
                "seed_policy": seed_policy,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    x2 = ["00", "01", "10", "11"]
    add("identity_channel", "X2", "Y2", "identity", identity_matrix(x2))
    add("total_erasure_channel", "X2", "Y_star", "total_erasure", erasure_matrix(x2))
    add("projection_A_channel", "X2", "Y_A", "projection", projection_matrix(x2, 0), {"coordinate": "A"})
    add("projection_B_channel", "X2", "Y_B", "projection", projection_matrix(x2, 1), {"coordinate": "B"})
    for p in [Fraction(0), Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2)]:
        add(
            f"bit_flip_p_{prob_token(p)}",
            "X2",
            "Y2",
            "independent_bit_flip",
            bit_flip_matrix(x2, p, p),
            {"p_A": fraction_text(p), "p_B": fraction_text(p)},
        )
    add(
        "asym_A_preserved_B_noisy_p_0_25",
        "X2",
        "Y2",
        "asymmetric_bit_noise",
        bit_flip_matrix(x2, Fraction(0), Fraction(1, 4)),
        {"p_A": "0", "p_B": "1/4"},
    )
    add(
        "asym_A_noisy_B_preserved_p_0_25",
        "X2",
        "Y2",
        "asymmetric_bit_noise",
        bit_flip_matrix(x2, Fraction(1, 4), Fraction(0)),
        {"p_A": "1/4", "p_B": "0"},
    )
    add(
        "asym_A_erased_B_preserved",
        "X2",
        "Y2",
        "asymmetric_bit_erasure",
        erased_coordinate_matrix(x2, erased_index=0),
        {"erased_coordinate": "A", "preserved_coordinate": "B"},
    )
    add(
        "asym_B_erased_A_preserved",
        "X2",
        "Y2",
        "asymmetric_bit_erasure",
        erased_coordinate_matrix(x2, erased_index=1),
        {"erased_coordinate": "B", "preserved_coordinate": "A"},
    )
    add(
        "marginal_joint_degrade_q_0_10",
        "X2",
        "Y2",
        "marginal_preserving_joint_degrading",
        one_bit_shuffle_matrix(x2, Fraction(1, 10)),
        {"q_flip_exactly_one_bit": "1/10"},
    )
    add(
        "marginal_joint_degrade_q_0_20",
        "X2",
        "Y2",
        "marginal_preserving_joint_degrading",
        one_bit_shuffle_matrix(x2, Fraction(1, 5)),
        {"q_flip_exactly_one_bit": "1/5"},
    )
    add(
        "output_marginal_matched_uniform",
        "X2",
        "Y2",
        "output_marginal_matched_channel",
        uniform_output_matrix(x2),
    )
    add(
        "random_channel_same_output_entropy_seed_17",
        "X2",
        "Y2",
        "random_channel_same_output_entropy",
        deterministic_entropy_matched_matrix(x2, seed=17),
        {"seed": 17, "row_weights": ["1/2", "1/4", "1/8", "1/8"]},
        seed_policy="fixed_seed_17",
    )
    add("y2_identity_channel", "Y2", "Y2", "identity", identity_matrix(x2))
    add(
        "y2_bit_flip_p_0_25",
        "Y2",
        "Y2",
        "independent_bit_flip",
        bit_flip_matrix(x2, Fraction(1, 4), Fraction(1, 4)),
        {"p_A": "1/4", "p_B": "1/4"},
    )
    add(
        "y2_marginal_joint_degrade_q_0_10",
        "Y2",
        "Y2",
        "marginal_preserving_joint_degrading",
        one_bit_shuffle_matrix(x2, Fraction(1, 10)),
        {"q_flip_exactly_one_bit": "1/10"},
    )
    return rows, matrices


def identity_matrix(states: list[str]) -> dict[str, dict[str, Fraction]]:
    return {source: {target: Fraction(int(source == target), 1) for target in states} for source in states}


def erasure_matrix(states: list[str]) -> dict[str, dict[str, Fraction]]:
    return {source: {"*": Fraction(1)} for source in states}


def projection_matrix(states: list[str], index: int) -> dict[str, dict[str, Fraction]]:
    return {
        source: {target: Fraction(int(bit(source, index) == target), 1) for target in ["0", "1"]}
        for source in states
    }


def bit_flip_matrix(states: list[str], p_a: Fraction, p_b: Fraction) -> dict[str, dict[str, Fraction]]:
    matrix: dict[str, dict[str, Fraction]] = {}
    for source in states:
        row = {}
        for target in states:
            a_prob = (1 - p_a) if source[0] == target[0] else p_a
            b_prob = (1 - p_b) if source[1] == target[1] else p_b
            row[target] = a_prob * b_prob
        matrix[source] = row
    return matrix


def erased_coordinate_matrix(states: list[str], *, erased_index: int) -> dict[str, dict[str, Fraction]]:
    matrix = {}
    kept_index = 1 - erased_index
    for source in states:
        row = {}
        for target in states:
            row[target] = Fraction(1, 2) if target[kept_index] == source[kept_index] else Fraction(0)
        matrix[source] = row
    return matrix


def one_bit_shuffle_matrix(states: list[str], q: Fraction) -> dict[str, dict[str, Fraction]]:
    matrix = {}
    for source in states:
        row = {target: Fraction(0) for target in states}
        row[source] += 1 - q
        row[flip_bit(source, 0)] += q / 2
        row[flip_bit(source, 1)] += q / 2
        matrix[source] = row
    return matrix


def uniform_output_matrix(states: list[str]) -> dict[str, dict[str, Fraction]]:
    return {source: {target: Fraction(1, len(states)) for target in states} for source in states}


def deterministic_entropy_matched_matrix(states: list[str], *, seed: int) -> dict[str, dict[str, Fraction]]:
    weights = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 8)]
    matrix = {}
    for index, source in enumerate(states):
        shift = (index + seed) % len(states)
        targets = states[shift:] + states[:shift]
        matrix[source] = {target: weight for target, weight in zip(targets, weights)}
    return matrix


def prob_token(value: Fraction) -> str:
    if value == 0:
        return "0_00"
    return f"{float(value):.2f}".replace(".", "_")

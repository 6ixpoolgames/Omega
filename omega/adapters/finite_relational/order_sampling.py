"""Finite order-sampling harness.

This module samples small declared fact preorders and classifies whether simple
loss/expansion-style verdicts are invariant or order-dependent. It is a
pre-NOLP calibration harness, not a theory of value, standing, aggregation, or
Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any


PROTOCOL_DOC = "docs/research_notes/omega_theory/order_sampling_harness_protocol_v0.md"


@dataclass(frozen=True)
class FactOrder:
    order_id: str
    facts: tuple[str, ...]
    leq_pairs: frozenset[tuple[str, str]]

    def __post_init__(self) -> None:
        fact_set = set(self.facts)
        for fact in self.facts:
            if (fact, fact) not in self.leq_pairs:
                raise ValueError(f"order {self.order_id!r} is missing reflexive pair for {fact!r}")
        for left, right in self.leq_pairs:
            if left not in fact_set or right not in fact_set:
                raise ValueError(f"order {self.order_id!r} has unknown pair ({left!r}, {right!r})")
        for a in self.facts:
            for b in self.facts:
                for c in self.facts:
                    if (a, b) in self.leq_pairs and (b, c) in self.leq_pairs and (a, c) not in self.leq_pairs:
                        raise ValueError(f"order {self.order_id!r} is not transitive")

    def leq(self, left: str, right: str) -> bool:
        return (left, right) in self.leq_pairs


@dataclass(frozen=True)
class Profile:
    profile_id: str
    facts: frozenset[str]


def discrete_order(facts: tuple[str, ...]) -> FactOrder:
    return FactOrder(
        order_id="discrete",
        facts=facts,
        leq_pairs=frozenset((fact, fact) for fact in facts),
    )


def chain_order(facts: tuple[str, ...], order_id: str) -> FactOrder:
    pairs = {(fact, fact) for fact in facts}
    for idx, left in enumerate(facts):
        for right in facts[idx + 1 :]:
            pairs.add((left, right))
    return FactOrder(order_id=order_id, facts=facts, leq_pairs=frozenset(pairs))


def two_fact_orders() -> tuple[FactOrder, ...]:
    facts = ("local", "joint")
    return (
        discrete_order(facts),
        chain_order(("local", "joint"), "local_below_joint"),
        chain_order(("joint", "local"), "joint_below_local"),
    )


def three_fact_orders() -> tuple[FactOrder, ...]:
    facts = ("task", "revision", "joint")
    return (
        discrete_order(facts),
        chain_order(("task", "revision", "joint"), "task_below_revision_below_joint"),
        chain_order(("task", "joint", "revision"), "task_below_joint_below_revision"),
    )


def down_closed(profile: Profile, order: FactOrder) -> frozenset[str]:
    return frozenset(
        fact
        for fact in order.facts
        if any(profile_fact in profile.facts and order.leq(fact, profile_fact) for profile_fact in order.facts)
    )


def covered_expansion(profile: Profile, order: FactOrder) -> frozenset[str]:
    return frozenset(
        fact
        for fact in order.facts
        if any(profile_fact in profile.facts and order.leq(fact, profile_fact) for profile_fact in order.facts)
    )


def profile_dominates(left: Profile, right: Profile, order: FactOrder) -> bool:
    return down_closed(right, order).issubset(down_closed(left, order))


def expansion_dominates(left: Profile, right: Profile, order: FactOrder) -> bool:
    return covered_expansion(right, order).issubset(covered_expansion(left, order))


def classify_verdict(verdicts: tuple[bool, ...]) -> str:
    values = set(verdicts)
    if len(values) == 1:
        return "invariant_true" if True in values else "invariant_false"
    return "dependent"


def sample_profile_verdict(
    left: Profile,
    right: Profile,
    orders: tuple[FactOrder, ...],
    *,
    mode: str,
) -> dict[str, Any]:
    if mode not in {"loss", "expansion"}:
        raise ValueError(f"unknown mode {mode!r}")
    rows = []
    for order in orders:
        verdict = (
            profile_dominates(left, right, order)
            if mode == "loss"
            else expansion_dominates(left, right, order)
        )
        rows.append(
            {
                "order_id": order.order_id,
                "verdict": verdict,
                "left_closure": sorted(down_closed(left, order)),
                "right_closure": sorted(down_closed(right, order)),
            }
        )
    verdicts = tuple(row["verdict"] for row in rows)
    return {
        "left": left.profile_id,
        "right": right.profile_id,
        "mode": mode,
        "classification": classify_verdict(verdicts),
        "rows": rows,
    }


def loss_order_dependency_witness() -> dict[str, Any]:
    left = Profile("lose_local", frozenset({"local"}))
    right = Profile("lose_joint", frozenset({"joint"}))
    return sample_profile_verdict(left, right, two_fact_orders(), mode="loss")


def expansion_order_invariant_witness() -> dict[str, Any]:
    left = Profile("expand_task_and_revision", frozenset({"task", "revision"}))
    right = Profile("expand_task", frozenset({"task"}))
    return sample_profile_verdict(left, right, three_fact_orders(), mode="expansion")


def adjacent_order_pairs(orders: tuple[FactOrder, ...]) -> tuple[tuple[str, str], ...]:
    return tuple((left.order_id, right.order_id) for left, right in combinations(orders, 2))


def order_sampling_summary() -> dict[str, Any]:
    loss = loss_order_dependency_witness()
    expansion = expansion_order_invariant_witness()
    calibrated = (
        loss["classification"] == "dependent"
        and expansion["classification"] == "invariant_true"
    )
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "calibrated" if calibrated else "review",
        "loss_dependency_witness": loss,
        "expansion_invariant_witness": expansion,
        "sampled_order_classes": {
            "two_fact_orders": [order.order_id for order in two_fact_orders()],
            "three_fact_orders": [order.order_id for order in three_fact_orders()],
            "two_fact_adjacent_pairs": [list(pair) for pair in adjacent_order_pairs(two_fact_orders())],
        },
        "not_claimed": [
            "correct fact order",
            "value",
            "standing",
            "aggregation",
            "arbitration",
            "patienthood",
            "Omega validation",
        ],
    }


def order_sampling_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for witness_key in ("loss_dependency_witness", "expansion_invariant_witness"):
        witness = summary[witness_key]
        for row in witness["rows"]:
            rows.append(
                {
                    "witness": witness_key,
                    "left": witness["left"],
                    "right": witness["right"],
                    "mode": witness["mode"],
                    "classification": witness["classification"],
                    "order_id": row["order_id"],
                    "verdict": row["verdict"],
                }
            )
    return rows

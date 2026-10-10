"""Exact conditioning on finite information maps, including forgetting.

Information is a partition of one fixed probability space. Later information
need not refine earlier information; conditional means alone do not decide it.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from fractions import Fraction

from omega_v2.finite.model import FiniteDistribution

F = Fraction


def _conditional(law: FiniteDistribution, records: Mapping, values: Mapping) -> dict:
    cells = {}
    for outcome, probability in law.rows:
        if not isinstance(probability, F) or not isinstance(values[outcome], F):
            raise TypeError("probabilities and readouts must be exact Fractions")
        cell = cells.setdefault(records[outcome], {"mass": F(0), "weighted_sum": F(0)})
        cell["mass"] += probability
        cell["weighted_sum"] += probability * values[outcome]
    return {record: {"mass": cell["mass"], "mean": cell["weighted_sum"] / cell["mass"]}
            for record, cell in cells.items()}


def conditional_expectations(
    law: FiniteDistribution,
    information: Callable[[Hashable], Hashable],
    readout: Callable[[Hashable], Fraction],
) -> dict:
    """Return mass and conditional mean in every positive-mass information cell."""
    records = {outcome: information(outcome) for outcome in law.support}
    values = {outcome: readout(outcome) for outcome in law.support}
    return _conditional(law, records, values)


def audit_information_step(
    law: FiniteDistribution,
    before: Callable[[Hashable], Hashable],
    after: Callable[[Hashable], Hashable],
    readout: Callable[[Hashable], Fraction],
) -> dict:
    """Check refinement separately from E[E[X|after]|before] = E[X|before].

    All checks are on this law's positive-mass support. A failed refinement
    includes two outcomes merged by 'after' but distinguished by 'before'.
    This is an analyst's diagnostic, never an input to a controller policy.
    """
    previous = {outcome: before(outcome) for outcome in law.support}
    following = {outcome: after(outcome) for outcome in law.support}
    values = {outcome: readout(outcome) for outcome in law.support}
    first, witness = {}, None
    for outcome in law.support:
        record = following[outcome]
        if record in first:
            other = first[record]
            if previous[other] != previous[outcome] and witness is None:
                witness = {"same_after": record, "left": other, "right": outcome,
                           "before_left": previous[other], "before_right": previous[outcome]}
        else:
            first[record] = outcome
    prior = _conditional(law, previous, values)
    later = _conditional(law, following, values)
    projected = _conditional(law, previous, {o: later[following[o]]["mean"] for o in law.support})
    rows = [{"before": record, "mass": cell["mass"], "before_mean": cell["mean"],
             "expected_after_mean": projected[record]["mean"],
             "difference": projected[record]["mean"] - cell["mean"]}
            for record, cell in prior.items()]
    return {"after_refines_before": witness is None, "refinement_counterexample": witness,
            "tower_holds_for_readout": all(row["difference"] == 0 for row in rows),
            "before_cells": prior, "after_cells": later, "tower_rows": rows}

"""Bounded behavioral logic over dynamic continuation signatures.

The module removes the representative-state comparison basis from the finite
instrument by deriving a semantic universe from realized behavior signatures.
It also supplies finite positive forcing certificates for the retained bounded
alternating-refinement relation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Any, Iterable

from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    BehaviorSignature,
    FiniteControlSystem,
    alternating_refines,
    behavior_basis,
    behavior_signature,
    behavior_signatures,
    capability_profile,
    duplicate_outcome_systems,
    novel_branch_systems,
    quantifier_control_systems,
)
from omega.adapters.finite_relational.lushness_diversity import Profile


PROTOCOL_DOC = "docs/research_notes/omega_v2/bounded_behavioral_logic_protocol_v0.md"

Point = tuple[int, str]


class FormulaKind(str, Enum):
    TOP = "top"
    ATOM = "atom"
    AND = "and"
    OR = "or"
    FORCE = "force"


@dataclass(frozen=True)
class ForcingFormula:
    """One formula in the finite positive forcing grammar."""

    kind: FormulaKind
    atom: str | None = None
    terms: tuple["ForcingFormula", ...] = ()

    def __post_init__(self) -> None:
        if self.kind is FormulaKind.ATOM:
            if not self.atom or self.terms:
                raise ValueError("atom formulas require one atom and no terms")
            return
        if self.atom is not None:
            raise ValueError("only atom formulas may carry an atom")
        if self.kind is FormulaKind.FORCE and len(self.terms) != 1:
            raise ValueError("force formulas require exactly one body")
        if self.kind in {FormulaKind.TOP, FormulaKind.FORCE}:
            if self.kind is FormulaKind.TOP and self.terms:
                raise ValueError("top has no terms")
            return
        if not self.terms:
            raise ValueError("and/or formulas require at least one term")

    def payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"kind": self.kind.value}
        if self.atom is not None:
            payload["atom"] = self.atom
        if self.terms:
            payload["terms"] = [term.payload() for term in self.terms]
        return payload

    def canonical_json(self) -> str:
        return json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))


def top_formula() -> ForcingFormula:
    return ForcingFormula(FormulaKind.TOP)


def atom_formula(atom: str) -> ForcingFormula:
    return ForcingFormula(FormulaKind.ATOM, atom=atom)


def and_formula(*terms: ForcingFormula) -> ForcingFormula:
    flattened: set[ForcingFormula] = set()
    for term in terms:
        if term.kind is FormulaKind.TOP:
            continue
        if term.kind is FormulaKind.AND:
            flattened.update(term.terms)
        else:
            flattened.add(term)
    if not flattened:
        return top_formula()
    if len(flattened) == 1:
        return next(iter(flattened))
    return ForcingFormula(
        FormulaKind.AND,
        terms=tuple(sorted(flattened, key=_formula_sort_key)),
    )


def or_formula(*terms: ForcingFormula) -> ForcingFormula:
    flattened: set[ForcingFormula] = set()
    for term in terms:
        if term.kind is FormulaKind.TOP:
            return top_formula()
        if term.kind is FormulaKind.OR:
            flattened.update(term.terms)
        else:
            flattened.add(term)
    if not flattened:
        raise ValueError("the positive grammar has no empty disjunction")
    if len(flattened) == 1:
        return next(iter(flattened))
    return ForcingFormula(
        FormulaKind.OR,
        terms=tuple(sorted(flattened, key=_formula_sort_key)),
    )


def force_formula(body: ForcingFormula) -> ForcingFormula:
    return ForcingFormula(FormulaKind.FORCE, terms=(body,))


def formula_depth(formula: ForcingFormula) -> int:
    if formula.kind in {FormulaKind.TOP, FormulaKind.ATOM}:
        return 0
    child_depth = max(formula_depth(term) for term in formula.terms)
    return child_depth + (1 if formula.kind is FormulaKind.FORCE else 0)


def formula_uses_disjunction(formula: ForcingFormula) -> bool:
    return formula.kind is FormulaKind.OR or any(
        formula_uses_disjunction(term) for term in formula.terms
    )


def signature_refines(
    left: BehaviorSignature,
    right: BehaviorSignature,
) -> bool:
    """Return whether ``right`` weakly refines ``left`` structurally."""

    memo: dict[tuple[BehaviorSignature, BehaviorSignature], bool] = {}

    def visit(
        left_signature: BehaviorSignature,
        right_signature: BehaviorSignature,
    ) -> bool:
        key = (left_signature, right_signature)
        if key in memo:
            return memo[key]
        if not set(left_signature.atoms) <= set(right_signature.atoms):
            memo[key] = False
            return False
        for left_effect in left_signature.action_effects:
            if not any(
                all(
                    any(visit(left_next, right_next) for left_next in left_effect)
                    for right_next in right_effect
                )
                for right_effect in right_signature.action_effects
            ):
                memo[key] = False
                return False
        memo[key] = True
        return True

    return visit(left, right)


def characteristic_formula(signature: BehaviorSignature) -> ForcingFormula:
    """Build the finite positive characteristic formula for one signature."""

    memo: dict[BehaviorSignature, ForcingFormula] = {}

    def visit(current: BehaviorSignature) -> ForcingFormula:
        if current in memo:
            return memo[current]
        clauses = [atom_formula(atom) for atom in current.atoms]
        for effect in current.action_effects:
            outcome_formula = or_formula(*(visit(successor) for successor in effect))
            clauses.append(force_formula(outcome_formula))
        result = and_formula(*clauses)
        memo[current] = result
        return result

    return visit(signature)


def signature_satisfies(
    signature: BehaviorSignature,
    formula: ForcingFormula,
) -> bool:
    if formula.kind is FormulaKind.TOP:
        return True
    if formula.kind is FormulaKind.ATOM:
        assert formula.atom is not None
        return formula.atom in signature.atoms
    if formula.kind is FormulaKind.AND:
        return all(signature_satisfies(signature, term) for term in formula.terms)
    if formula.kind is FormulaKind.OR:
        return any(signature_satisfies(signature, term) for term in formula.terms)
    body = formula.terms[0]
    return any(
        all(signature_satisfies(successor, body) for successor in effect)
        for effect in signature.action_effects
    )


def state_satisfies(
    system: FiniteControlSystem,
    state: str,
    formula: ForcingFormula,
) -> bool:
    return signature_satisfies(
        behavior_signature(system, state, formula_depth(formula)),
        formula,
    )


def derived_behavior_universe(
    *systems: FiniteControlSystem,
    horizon: int,
) -> tuple[BehaviorSignature, ...]:
    signatures = {
        signature
        for system in systems
        for signature in behavior_signatures(system, horizon).values()
    }
    return tuple(sorted(signatures, key=_signature_sort_key))


def derived_capability_profile(
    system: FiniteControlSystem,
    state: str,
    *,
    universe: Iterable[BehaviorSignature],
    horizon: int,
) -> Profile:
    target = behavior_signature(system, state, horizon)
    return frozenset(
        candidate.fingerprint(horizon=horizon)
        for candidate in universe
        if signature_refines(candidate, target)
    )


def semantic_formula_extensions(
    systems: tuple[FiniteControlSystem, ...],
    *,
    horizon: int,
    allow_disjunction: bool,
) -> frozenset[frozenset[Point]]:
    """Compute formula extensions over a finite disjoint union of systems."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    points = frozenset(
        (index, state) for index, system in enumerate(systems) for state in system.states
    )
    atom_names = sorted(
        {atom for system in systems for state in system.states for atom in system.atoms_at(state)}
    )
    extensions = {points}
    extensions.update(
        frozenset(
            (index, state)
            for index, system in enumerate(systems)
            for state in system.states
            if atom in system.atoms_at(state)
        )
        for atom in atom_names
    )
    extensions = _boolean_closure(extensions, allow_disjunction=allow_disjunction)

    for _depth in range(horizon):
        previous = frozenset(extensions)
        forced = {_force_extension(systems, extension) for extension in previous}
        extensions = _boolean_closure(
            set(previous) | forced,
            allow_disjunction=allow_disjunction,
        )
    return frozenset(extensions)


def logical_refines(
    left: Point,
    right: Point,
    extensions: Iterable[frozenset[Point]],
) -> bool:
    return all(left not in extension or right in extension for extension in extensions)


def forcing_grammar_system() -> FiniteControlSystem:
    """Fixture where disjunction is needed to express an outcome cover."""

    return FiniteControlSystem(
        system_id="forcing_grammar",
        states=(
            "source_ab",
            "refine_a",
            "refine_b",
            "outsider_c",
            "outcome_a",
            "outcome_b",
            "outcome_c",
        ),
        actions=("offer_ab", "offer_a", "offer_b", "offer_c"),
        transitions=(
            ("source_ab", "offer_ab", "outcome_a"),
            ("source_ab", "offer_ab", "outcome_b"),
            ("refine_a", "offer_a", "outcome_a"),
            ("refine_b", "offer_b", "outcome_b"),
            ("outsider_c", "offer_c", "outcome_c"),
        ),
        atoms=(
            ("source_ab", frozenset({"root"})),
            ("refine_a", frozenset({"root"})),
            ("refine_b", frozenset({"root"})),
            ("outsider_c", frozenset({"root"})),
            ("outcome_a", frozenset({"a"})),
            ("outcome_b", frozenset({"b"})),
            ("outcome_c", frozenset({"c"})),
        ),
    )


def audited_systems() -> tuple[FiniteControlSystem, ...]:
    duplicate_base, duplicate_extension = duplicate_outcome_systems()
    choice, risk = quantifier_control_systems()
    novel_base, novel_extension = novel_branch_systems()
    return (
        duplicate_base,
        duplicate_extension,
        choice,
        risk,
        novel_base,
        novel_extension,
        forcing_grammar_system(),
    )


def structural_state_parity_witness(*, horizon: int = 2) -> dict[str, Any]:
    systems = audited_systems()
    mismatches: list[dict[str, Any]] = []
    for left_system in systems:
        left_signatures = behavior_signatures(left_system, horizon)
        for right_system in systems:
            right_signatures = behavior_signatures(right_system, horizon)
            for left_state in left_system.states:
                for right_state in right_system.states:
                    structural = signature_refines(
                        left_signatures[left_state],
                        right_signatures[right_state],
                    )
                    state_level = alternating_refines(
                        left_system,
                        left_state,
                        right_system,
                        right_state,
                        horizon=horizon,
                    )
                    if structural != state_level:
                        mismatches.append(
                            {
                                "left_system": left_system.system_id,
                                "left_state": left_state,
                                "right_system": right_system.system_id,
                                "right_state": right_state,
                                "structural": structural,
                                "state_level": state_level,
                            }
                        )
    return {
        "horizon": horizon,
        "ordered_state_pairs": sum(len(system.states) for system in systems) ** 2,
        "mismatches": mismatches,
        "parity": not mismatches,
    }


def derived_basis_parity_witness(*, horizon: int = 2) -> dict[str, Any]:
    systems = audited_systems()
    representative_basis = behavior_basis(*systems)
    semantic_universe = derived_behavior_universe(*systems, horizon=horizon)
    mismatches: list[dict[str, Any]] = []
    for system in systems:
        for state in system.states:
            old_profile = capability_profile(
                system,
                state,
                basis=representative_basis,
                horizon=horizon,
            )
            new_profile = derived_capability_profile(
                system,
                state,
                universe=semantic_universe,
                horizon=horizon,
            )
            if old_profile != new_profile:
                mismatches.append(
                    {
                        "system": system.system_id,
                        "state": state,
                        "old_profile": sorted(old_profile),
                        "new_profile": sorted(new_profile),
                    }
                )
    return {
        "horizon": horizon,
        "representative_count": len(representative_basis),
        "semantic_type_count": len(semantic_universe),
        "duplicate_representatives_removed": len(representative_basis) - len(semantic_universe),
        "mismatches": mismatches,
        "parity": not mismatches,
    }


def characteristic_correspondence_witness(*, horizon: int = 2) -> dict[str, Any]:
    systems = audited_systems()
    universe = derived_behavior_universe(*systems, horizon=horizon)
    mismatches: list[dict[str, Any]] = []
    disjunctive_certificates = 0
    for left in universe:
        certificate = characteristic_formula(left)
        disjunctive_certificates += int(formula_uses_disjunction(certificate))
        for right in universe:
            refines = signature_refines(left, right)
            satisfies = signature_satisfies(right, certificate)
            if refines != satisfies:
                mismatches.append(
                    {
                        "left": left.fingerprint(horizon=horizon),
                        "right": right.fingerprint(horizon=horizon),
                        "refines": refines,
                        "satisfies": satisfies,
                    }
                )
    return {
        "horizon": horizon,
        "semantic_type_count": len(universe),
        "ordered_type_pairs": len(universe) ** 2,
        "disjunctive_certificate_count": disjunctive_certificates,
        "mismatches": mismatches,
        "correspondence": not mismatches,
    }


def grammar_adequacy_witness(*, horizon: int = 1) -> dict[str, Any]:
    system = forcing_grammar_system()
    systems = (system,)
    conjunction_extensions = semantic_formula_extensions(
        systems,
        horizon=horizon,
        allow_disjunction=False,
    )
    full_extensions = semantic_formula_extensions(
        systems,
        horizon=horizon,
        allow_disjunction=True,
    )
    points = tuple((0, state) for state in system.states)

    def relation_mismatches(
        extensions: frozenset[frozenset[Point]],
    ) -> list[dict[str, Any]]:
        mismatches = []
        for left_index, left_state in points:
            for right_index, right_state in points:
                signature_order = alternating_refines(
                    system,
                    left_state,
                    system,
                    right_state,
                    horizon=horizon,
                )
                logic_order = logical_refines(
                    (left_index, left_state),
                    (right_index, right_state),
                    extensions,
                )
                if signature_order != logic_order:
                    mismatches.append(
                        {
                            "left_state": left_state,
                            "right_state": right_state,
                            "signature_order": signature_order,
                            "logic_order": logic_order,
                        }
                    )
        return mismatches

    conjunction_mismatches = relation_mismatches(conjunction_extensions)
    full_mismatches = relation_mismatches(full_extensions)
    target_mismatch = any(
        row["left_state"] == "source_ab" and row["right_state"] == "outsider_c"
        for row in conjunction_mismatches
    )
    return {
        "horizon": horizon,
        "conjunction_extension_count": len(conjunction_extensions),
        "full_extension_count": len(full_extensions),
        "conjunction_only_mismatches": conjunction_mismatches,
        "full_grammar_mismatches": full_mismatches,
        "target_multi_outcome_mismatch_present": target_mismatch,
        "conjunction_only_sufficient": not conjunction_mismatches,
        "disjunction_required_on_fixture": bool(conjunction_mismatches) and not full_mismatches,
        "full_grammar_recovers_preorder": not full_mismatches,
    }


def presentation_witness(*, horizon: int = 2) -> dict[str, Any]:
    base, _duplicate = duplicate_outcome_systems()
    relabeled = base.relabel(
        state_mapping={"root": "renamed_root", "persistent": "renamed_persistent"},
        action_mapping={"advance": "renamed_advance", "remain": "renamed_remain"},
        system_id="behavioral_logic_relabel",
    )
    universe = derived_behavior_universe(base, relabeled, horizon=horizon)
    base_signature = behavior_signature(base, "root", horizon)
    relabeled_signature = behavior_signature(relabeled, "renamed_root", horizon)
    certificate = characteristic_formula(base_signature)
    return {
        "horizon": horizon,
        "signatures_equal": base_signature == relabeled_signature,
        "profiles_equal": (
            derived_capability_profile(
                base,
                "root",
                universe=universe,
                horizon=horizon,
            )
            == derived_capability_profile(
                relabeled,
                "renamed_root",
                universe=universe,
                horizon=horizon,
            )
        ),
        "certificate_truth_preserved": (
            state_satisfies(base, "root", certificate)
            == state_satisfies(relabeled, "renamed_root", certificate)
        ),
    }


def bounded_behavioral_logic_summary() -> dict[str, Any]:
    structural = structural_state_parity_witness()
    basis = derived_basis_parity_witness()
    characteristic = characteristic_correspondence_witness()
    grammar = grammar_adequacy_witness()
    presentation = presentation_witness()
    cases = {
        "BL1_structural_state_parity": structural["parity"],
        "BL2_derived_basis_parity": basis["parity"],
        "BL3_characteristic_correspondence": characteristic["correspondence"],
        "BL4_grammar_adequacy": grammar["full_grammar_recovers_preorder"],
        "BL5_presentation_control": all(
            presentation[key]
            for key in (
                "signatures_equal",
                "profiles_equal",
                "certificate_truth_preserved",
            )
        ),
    }
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if all(cases.values()) else "review",
        "case_results": cases,
        "cases": {
            "structural_state_parity": structural,
            "derived_basis_parity": basis,
            "characteristic_correspondence": characteristic,
            "grammar_adequacy": grammar,
            "presentation": presentation,
        },
        "evidence_classification": {
            "theorem_regression": ["BL1_structural_state_parity"],
            "instrument_correctness": sorted(
                case for case in cases if case != "BL1_structural_state_parity"
            ),
            "risky_prediction": [],
        },
        "predecessor_evidence_reclassification": {
            "instrument_correctness": [
                "duplicate resistance",
                "effect-equivalent action resistance",
                "novel-branch strictness",
                "delayed-divergence depth",
                "action/outcome quantifier control",
                "deformation classification",
                "presentation controls",
                "lushness bridge plumbing",
            ],
            "risky_retained_result": [
                "adaptive fixed-world behavior strictly refines switching behavior"
            ],
        },
        "not_claimed": [
            "general ATL completeness",
            "general modal completeness",
            "value",
            "valuerhood",
            "agency",
            "standing",
            "identity",
            "moral license",
            "Omega validation",
        ],
    }


def case_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    theorem_regressions = set(summary["evidence_classification"]["theorem_regression"])
    return [
        {
            "case": case,
            "passes": passes,
            "evidence_class": (
                "theorem_regression" if case in theorem_regressions else "instrument_correctness"
            ),
        }
        for case, passes in summary["case_results"].items()
    ]


def certificate_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    case = summary["cases"]["characteristic_correspondence"]
    return [
        {
            "horizon": case["horizon"],
            "semantic_type_count": case["semantic_type_count"],
            "ordered_type_pairs": case["ordered_type_pairs"],
            "disjunctive_certificate_count": case["disjunctive_certificate_count"],
            "mismatch_count": len(case["mismatches"]),
            "correspondence": case["correspondence"],
        }
    ]


def grammar_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    case = summary["cases"]["grammar_adequacy"]
    return [
        {
            "grammar": "conjunction_only",
            "extension_count": case["conjunction_extension_count"],
            "mismatch_count": len(case["conjunction_only_mismatches"]),
            "recovers_preorder": case["conjunction_only_sufficient"],
        },
        {
            "grammar": "with_disjunction",
            "extension_count": case["full_extension_count"],
            "mismatch_count": len(case["full_grammar_mismatches"]),
            "recovers_preorder": case["full_grammar_recovers_preorder"],
        },
    ]


def _force_extension(
    systems: tuple[FiniteControlSystem, ...],
    extension: frozenset[Point],
) -> frozenset[Point]:
    return frozenset(
        (index, state)
        for index, system in enumerate(systems)
        for state in system.states
        if any(
            all((index, successor) in extension for successor in system.successors(state, action))
            for action in system.enabled_actions(state)
        )
    )


def _boolean_closure(
    seeds: set[frozenset[Point]],
    *,
    allow_disjunction: bool,
) -> set[frozenset[Point]]:
    closure = set(seeds)
    changed = True
    while changed:
        changed = False
        snapshot = tuple(closure)
        for left, right in combinations(snapshot, 2):
            candidates = [left & right]
            if allow_disjunction:
                candidates.append(left | right)
            for candidate in candidates:
                frozen = frozenset(candidate)
                if frozen not in closure:
                    closure.add(frozen)
                    changed = True
    return closure


def _formula_sort_key(formula: ForcingFormula) -> str:
    return formula.canonical_json()


def _signature_sort_key(signature: BehaviorSignature) -> str:
    return signature.canonical_json()

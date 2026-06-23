"""Generic audits over finite relational adapter profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from omega.adapters.finite_relational.facts import (
    binary_relation,
    bounded_recovery_facts,
    carrier_certificate_facts,
    carrier_transfer_facts,
    nonfactorization_witnesses_for_predicate,
    presentation_violations,
    presentation_fact_closure_facts,
    reachable_pairs,
    target_scramble_sensitivity_facts,
    ternary_relation,
)
from omega.adapters.finite_relational.model import FiniteRelationalModel, SchemaError


@dataclass(frozen=True)
class AuditResult:
    audit_id: str
    kind: str
    passed: bool
    finding: str
    observed: dict[str, Any]
    expectation: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "kind": self.kind,
            "passed": self.passed,
            "finding": self.finding,
            "expectation": self.expectation,
            "observed": self.observed,
        }


def run_declared_audits(model: FiniteRelationalModel) -> list[AuditResult]:
    return [run_audit(model, audit) for audit in model.audits]


def run_audit(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    kind = str(audit.get("kind", ""))
    if kind == "alpha_laws":
        return _alpha_laws(model, audit)
    if kind == "sound_presentation":
        return _sound_presentation(model, audit)
    if kind == "phantom_reachability":
        return _phantom_reachability(model, audit)
    if kind == "hidden_reachability_loss":
        return _hidden_reachability_loss(model, audit)
    if kind == "nonfactorization":
        return _nonfactorization(model, audit)
    if kind == "carrier_certificate":
        return _carrier_certificate(model, audit)
    if kind == "carrier_transfer":
        return _carrier_transfer(model, audit)
    if kind == "bounded_recovery":
        return _bounded_recovery(model, audit)
    if kind == "presentation_fact_closure":
        return _presentation_fact_closure(model, audit)
    if kind == "target_scramble_sensitivity":
        return _target_scramble_sensitivity(model, audit)
    raise SchemaError(f"unknown audit kind: {kind}")


def _alpha_laws(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    rel = binary_relation(model, _role(model, audit, "rel"))
    sep = ternary_relation(model, _role(model, audit, "sep"))
    asym = ternary_relation(model, _role(model, audit, "asym"))

    sep_irreflexive_violations = sorted((d, x, y) for d, x, y in sep if x == y)
    sep_symmetric_violations = sorted((d, x, y) for d, x, y in sep if (d, y, x) not in sep)
    asym_rel_violations = sorted((d, x, y) for d, x, y in asym if (x, y) not in rel)
    asym_sep_violations = sorted((d, x, y) for d, x, y in asym if (d, x, y) not in sep)

    laws_hold = not (
        sep_irreflexive_violations
        or sep_symmetric_violations
        or asym_rel_violations
        or asym_sep_violations
    )
    observed = {
        "laws_hold": laws_hold,
        "primitive_witness_exists": bool(asym),
        "sep_irreflexive_violations": sep_irreflexive_violations,
        "sep_symmetric_violations": sep_symmetric_violations,
        "asym_rel_violations": asym_rel_violations,
        "asym_sep_violations": asym_sep_violations,
    }
    return _result(audit, "alpha_laws", observed, "laws_hold", "alpha_laws_hold")


def _sound_presentation(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    violations = presentation_violations(
        model,
        presentation=_role(model, audit, "presentation"),
        forbidden=_role(model, audit, "forbidden"),
    )
    observed = {
        "sound": not violations,
        "violation_count": len(violations),
        "violations": violations,
    }
    return _result(audit, "sound_presentation", observed, "sound", "sound")


def _phantom_reachability(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    exact_edges = binary_relation(model, _role(model, audit, "exact_transition"))
    abstract_edges = binary_relation(model, _role(model, audit, "abstract_transition"))
    source = str(audit["source"])
    target = str(audit["target"])
    states = set(model.domain(str(audit.get("domain", "state"))))
    exact_reach = reachable_pairs(states, exact_edges)
    abstract_reach = reachable_pairs(states, abstract_edges)
    exact_path = (source, target) in exact_reach
    abstract_path = (source, target) in abstract_reach
    observed = {
        "phantom": abstract_path and not exact_path,
        "exact_path": exact_path,
        "abstract_path": abstract_path,
        "source": source,
        "target": target,
    }
    return _result(audit, "phantom_reachability", observed, "phantom", "phantom")


def _hidden_reachability_loss(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    before_edges = binary_relation(model, _role(model, audit, "before_transition"))
    after_edges = binary_relation(model, _role(model, audit, "after_transition"))
    abstract_edges = binary_relation(model, _role(model, audit, "abstract_transition"))
    source = str(audit["source"])
    target = str(audit["target"])
    states = set(model.domain(str(audit.get("domain", "state"))))
    before_path = (source, target) in reachable_pairs(states, before_edges)
    after_path = (source, target) in reachable_pairs(states, after_edges)
    abstract_path = (source, target) in reachable_pairs(states, abstract_edges)
    observed = {
        "hidden_loss": before_path and not after_path and abstract_path,
        "before_path": before_path,
        "after_path": after_path,
        "abstract_path": abstract_path,
        "source": source,
        "target": target,
    }
    return _result(
        audit,
        "hidden_reachability_loss",
        observed,
        "hidden_loss",
        "hidden_loss",
    )


def _nonfactorization(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    witnesses = nonfactorization_witnesses_for_predicate(
        model,
        summary=_role(model, audit, "summary"),
        target_predicate=_role(model, audit, "target_predicate"),
    )
    observed = {
        "witness": bool(witnesses),
        "witness_count": len(witnesses),
        "witnesses": witnesses,
    }
    return _result(audit, "nonfactorization", observed, "witness", "witness")


def _carrier_certificate(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    observed = carrier_certificate_facts(
        model,
        transition=_role(model, audit, "transition"),
        safety=_role(model, audit, "safety"),
        carrier=_role(model, audit, "carrier"),
        left=str(audit["left"]),
        right=str(audit["right"]),
        separation=_role(model, audit, "separation"),
    )
    return _result(audit, "carrier_certificate", observed, "certified", "certified")


def _carrier_transfer(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    observed = carrier_transfer_facts(
        model,
        source_transition=_role(model, audit, "source_transition"),
        source_safety=_role(model, audit, "source_safety"),
        source_carrier=_role(model, audit, "source_carrier"),
        source_left=str(audit["source_left"]),
        source_right=str(audit["source_right"]),
        source_separation=_role(model, audit, "source_separation"),
        target_transition=_role(model, audit, "target_transition"),
        target_safety=_role(model, audit, "target_safety"),
        target_carrier=_role(model, audit, "target_carrier"),
        target_left=str(audit["target_left"]),
        target_right=str(audit["target_right"]),
        target_separation=_role(model, audit, "target_separation"),
        correspondence=_role(model, audit, "correspondence"),
    )
    return _result(audit, "carrier_transfer", observed, "transferred", "transferred")


def _bounded_recovery(model: FiniteRelationalModel, audit: dict[str, Any]) -> AuditResult:
    decoders_raw = audit.get("decoders", ())
    if not isinstance(decoders_raw, list):
        raise SchemaError(f"audit {audit.get('id', '<unnamed>')} decoders must be a list")
    observed = bounded_recovery_facts(
        model,
        observation=_role(model, audit, "observation"),
        target_predicate=_role(model, audit, "target_predicate"),
        decoders=tuple(str(decoder) for decoder in decoders_raw),
        true_label=str(audit.get("true_label", "true")),
        false_label=str(audit.get("false_label", "false")),
    )
    return _result(audit, "bounded_recovery", observed, "recoverable", "recoverable")


def _presentation_fact_closure(
    model: FiniteRelationalModel,
    audit: dict[str, Any],
) -> AuditResult:
    observed = presentation_fact_closure_facts(
        model,
        presentations=_audit_strings(audit, "presentations"),
        target_predicates=_audit_strings(audit, "target_predicates"),
        seed_visible_pairs=_audit_pairs(audit, "seed_visible_pairs"),
        seed_target_predicates=_audit_strings(audit, "seed_target_predicates"),
        expected_common_visible_pairs=_audit_pairs(audit, "expected_common_visible_pairs"),
        expected_absent_visible_pairs=_audit_pairs(audit, "expected_absent_visible_pairs"),
        expected_common_target_predicates=_audit_strings(
            audit,
            "expected_common_target_predicates",
        ),
        expected_absent_target_predicates=_audit_strings(
            audit,
            "expected_absent_target_predicates",
        ),
        expected_surplus_visible_pairs=_audit_pairs(audit, "expected_surplus_visible_pairs"),
        expected_absent_surplus_visible_pairs=_audit_pairs(
            audit,
            "expected_absent_surplus_visible_pairs",
        ),
        expected_surplus_target_predicates=_audit_strings(
            audit,
            "expected_surplus_target_predicates",
        ),
        expected_absent_surplus_target_predicates=_audit_strings(
            audit,
            "expected_absent_surplus_target_predicates",
        ),
        expected_nonconstant_surplus_target_predicates=_audit_strings(
            audit,
            "expected_nonconstant_surplus_target_predicates",
        ),
        expected_absent_nonconstant_surplus_target_predicates=_audit_strings(
            audit,
            "expected_absent_nonconstant_surplus_target_predicates",
        ),
        domain=str(audit.get("domain", "state")),
    )
    return _result(
        audit,
        "presentation_fact_closure",
        observed,
        "closure_ok",
        "closure_ok",
    )


def _target_scramble_sensitivity(
    model: FiniteRelationalModel,
    audit: dict[str, Any],
) -> AuditResult:
    decoders_raw = audit.get("decoders", ())
    if not isinstance(decoders_raw, list):
        raise SchemaError(f"audit {audit.get('id', '<unnamed>')} decoders must be a list")
    observed = target_scramble_sensitivity_facts(
        model,
        observation=_role(model, audit, "observation"),
        target_predicate=_role(model, audit, "target_predicate"),
        scrambled_predicate=_role(model, audit, "scrambled_predicate"),
        decoders=tuple(str(decoder) for decoder in decoders_raw),
        true_label=str(audit.get("true_label", "true")),
        false_label=str(audit.get("false_label", "false")),
    )
    return _result(
        audit,
        "target_scramble_sensitivity",
        observed,
        "sensitive",
        "sensitive",
    )


def _role(model: FiniteRelationalModel, audit: dict[str, Any], name: str) -> str:
    if name in audit:
        return str(audit[name])
    profile_name = audit.get("profile")
    if profile_name is not None:
        profile = model.profiles[str(profile_name)]
        if name in profile:
            return str(profile[name])
    raise SchemaError(f"audit {audit.get('id', '<unnamed>')} is missing role: {name}")


def _audit_strings(audit: dict[str, Any], key: str) -> tuple[str, ...]:
    raw_items = audit.get(key, [])
    if not isinstance(raw_items, list):
        raise SchemaError(f"audit {audit.get('id', '<unnamed>')} {key} must be a list")
    return tuple(str(item) for item in raw_items)


def _audit_pairs(audit: dict[str, Any], key: str) -> tuple[tuple[str, str], ...]:
    raw_pairs = audit.get(key, [])
    if not isinstance(raw_pairs, list):
        raise SchemaError(f"audit {audit.get('id', '<unnamed>')} {key} must be a list")
    pairs = []
    for raw_pair in raw_pairs:
        if not isinstance(raw_pair, list) or len(raw_pair) != 2:
            raise SchemaError(
                f"audit {audit.get('id', '<unnamed>')} {key} entries must be two-item lists"
            )
        pairs.append((str(raw_pair[0]), str(raw_pair[1])))
    return tuple(pairs)


def _result(
    audit: dict[str, Any],
    kind: str,
    observed: dict[str, Any],
    primary_key: str,
    true_finding: str,
) -> AuditResult:
    observed_value = bool(observed[primary_key])
    expectation = audit.get("expect")
    if expectation is None:
        passed = True
    else:
        expected_value = _expected_bool(str(expectation), true_finding)
        passed = observed_value == expected_value
    finding = true_finding if observed_value else f"not_{true_finding}"
    return AuditResult(
        audit_id=str(audit.get("id", kind)),
        kind=kind,
        passed=passed,
        finding=finding,
        expectation=str(expectation) if expectation is not None else None,
        observed=observed,
    )


def _expected_bool(expectation: str, true_finding: str) -> bool:
    positive = {
        true_finding,
        "true",
        "yes",
        "pass",
        "sound",
        "certified",
        "phantom",
        "hidden_loss",
        "witness",
        "alpha_laws_hold",
        "transferred",
        "recoverable",
    }
    negative = {
        f"not_{true_finding}",
        "false",
        "no",
        "fail",
        "unsound",
        "uncertified",
        "no_phantom",
        "no_hidden_loss",
        "no_witness",
        "alpha_laws_fail",
        "not_transferred",
        "no_transfer",
        "not_recoverable",
        "no_recovery",
        "closure_mismatch",
        "not_closure_ok",
    }
    if expectation in positive:
        return True
    if expectation in negative:
        return False
    raise SchemaError(f"unknown expectation {expectation!r} for finding {true_finding!r}")

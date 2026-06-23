"""Source compiler contracts for finite relational adapter inputs."""

from __future__ import annotations

from typing import Any

from omega.adapters.finite_relational.model import SchemaError


RESERVED_IR_FIELDS = frozenset(
    {"predicates", "relations", "functions", "profiles", "audits"}
)


def reserved_ir_fields(raw: dict[str, Any]) -> tuple[str, ...]:
    """Reserved low-level IR fields present in a source-level declaration."""

    return tuple(sorted(RESERVED_IR_FIELDS & set(raw)))


def assert_no_reserved_ir_fields(raw: dict[str, Any], *, source_kind: str) -> None:
    """Reject source declarations that try to provide derived IR surfaces.

    Source compilers may accept substrate-level declarations such as nodes,
    edges, observations, presentations, obstacle sets, or correspondences.
    They must not let the source declare the low-level finite relational facts,
    profiles, or audits that the compiler and generic audit engine are supposed
    to derive.
    """

    leaked = reserved_ir_fields(raw)
    if leaked:
        raise SchemaError(
            f"{source_kind} sources must not declare finite relational IR fields: "
            + ", ".join(leaked)
        )


def compiled_derivation_contract(
    compiled: dict[str, Any],
    *,
    compiled_from: str,
    required_derivation_rules: tuple[str, ...] = (),
) -> dict[str, object]:
    """Summarize whether a compiled model records expected derivation provenance."""

    provenance = compiled.get("provenance", {})
    if not isinstance(provenance, dict):
        return {
            "complete": False,
            "compiled_from": None,
            "missing_derivation_rules": list(required_derivation_rules),
        }
    rules = provenance.get("derivation_rules", ())
    if not isinstance(rules, list):
        rules = ()
    missing_rules = [rule for rule in required_derivation_rules if rule not in rules]
    return {
        "complete": provenance.get("compiled_from") == compiled_from
        and not missing_rules,
        "compiled_from": provenance.get("compiled_from"),
        "missing_derivation_rules": missing_rules,
    }

"""Finite relational model schema for adapter pilots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


DEFAULT_DOMAIN = "state"
REQUIRED_PROVENANCE_FIELDS = ("declared_before_run", "source", "claim_boundary")


class SchemaError(ValueError):
    """Raised when a finite relational model is malformed."""


@dataclass(frozen=True)
class Predicate:
    """A named subset of one finite domain."""

    domain: str
    members: frozenset[str]


@dataclass(frozen=True)
class Relation:
    """A named finite relation over declared domains."""

    domains: tuple[str, ...]
    tuples: frozenset[tuple[str, ...]]

    @property
    def arity(self) -> int:
        return len(self.domains)


@dataclass(frozen=True)
class FiniteFunction:
    """A named finite map from a declared domain to labels or another domain."""

    domain: str
    mapping: dict[str, str]
    codomain: str | None = None


@dataclass(frozen=True)
class FiniteRelationalModel:
    """A finite multi-sorted relational structure plus profiles and audits."""

    model_id: str
    schema_version: str
    domains: dict[str, tuple[str, ...]]
    predicates: dict[str, Predicate]
    relations: dict[str, Relation]
    functions: dict[str, FiniteFunction]
    profiles: dict[str, dict[str, Any]]
    audits: tuple[dict[str, Any], ...]
    provenance: dict[str, Any]
    raw: dict[str, Any]

    def domain(self, name: str = DEFAULT_DOMAIN) -> tuple[str, ...]:
        try:
            return self.domains[name]
        except KeyError as exc:
            raise SchemaError(f"unknown domain: {name}") from exc

    def predicate_members(self, name: str) -> frozenset[str]:
        try:
            return self.predicates[name].members
        except KeyError as exc:
            raise SchemaError(f"unknown predicate: {name}") from exc

    def relation_tuples(self, name: str) -> frozenset[tuple[str, ...]]:
        try:
            return self.relations[name].tuples
        except KeyError as exc:
            raise SchemaError(f"unknown relation: {name}") from exc

    def function_mapping(self, name: str) -> dict[str, str]:
        try:
            return self.functions[name].mapping
        except KeyError as exc:
            raise SchemaError(f"unknown function: {name}") from exc


def load_model_path(path: Path) -> FiniteRelationalModel:
    return load_model(json.loads(path.read_text(encoding="utf-8")))


def load_model(raw: dict[str, Any]) -> FiniteRelationalModel:
    domains = _normalize_domains(raw)
    default_domain = str(raw.get("default_domain", DEFAULT_DOMAIN))
    if default_domain not in domains:
        raise SchemaError(f"default_domain is not declared: {default_domain}")

    predicates = {
        name: _normalize_predicate(name, value, domains, default_domain)
        for name, value in raw.get("predicates", {}).items()
    }
    relations = {
        name: _normalize_relation(name, value, domains, default_domain)
        for name, value in raw.get("relations", {}).items()
    }
    functions = {
        name: _normalize_function(name, value, domains, default_domain)
        for name, value in raw.get("functions", {}).items()
    }

    audits = tuple(_require_dict(audit, "audit") for audit in raw.get("audits", ()))
    profiles = {
        name: _require_dict(value, f"profile {name}")
        for name, value in raw.get("profiles", {}).items()
    }
    provenance = _require_dict(raw.get("provenance", {}), "provenance")

    return FiniteRelationalModel(
        model_id=str(raw.get("model_id", "unnamed_model")),
        schema_version=str(raw.get("schema_version", "0.1.0")),
        domains=domains,
        predicates=predicates,
        relations=relations,
        functions=functions,
        profiles=profiles,
        audits=audits,
        provenance=provenance,
        raw=raw,
    )


def validate_provenance(model: FiniteRelationalModel) -> dict[str, Any]:
    missing = [field for field in REQUIRED_PROVENANCE_FIELDS if field not in model.provenance]
    declared_before_run = model.provenance.get("declared_before_run")
    return {
        "model_id": model.model_id,
        "complete": not missing and declared_before_run is True,
        "missing": missing,
        "declared_before_run": declared_before_run,
        "source": model.provenance.get("source"),
        "claim_boundary": model.provenance.get("claim_boundary"),
    }


def model_digest(model: FiniteRelationalModel) -> str:
    canonical = json.dumps(model.raw, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _normalize_domains(raw: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    if "domains" in raw:
        domains_raw = _require_dict(raw["domains"], "domains")
        domains = {name: _unique_string_tuple(values, f"domain {name}") for name, values in domains_raw.items()}
        if "carrier" in raw and DEFAULT_DOMAIN not in domains:
            domains[DEFAULT_DOMAIN] = _unique_string_tuple(raw["carrier"], "carrier")
        return domains
    if "carrier" not in raw:
        raise SchemaError("model must declare either domains or carrier")
    return {DEFAULT_DOMAIN: _unique_string_tuple(raw["carrier"], "carrier")}


def _normalize_predicate(
    name: str,
    value: Any,
    domains: dict[str, tuple[str, ...]],
    default_domain: str,
) -> Predicate:
    if isinstance(value, dict):
        domain = str(value.get("domain", default_domain))
        members_raw = value.get("members", value.get("values"))
    else:
        domain = default_domain
        members_raw = value
    if members_raw is None:
        raise SchemaError(f"predicate {name} must declare members")
    members = frozenset(_string_list(members_raw, f"predicate {name} members"))
    _validate_domain_members(members, domain, domains, f"predicate {name}")
    return Predicate(domain=domain, members=members)


def _normalize_relation(
    name: str,
    value: Any,
    domains: dict[str, tuple[str, ...]],
    default_domain: str,
) -> Relation:
    if isinstance(value, dict):
        tuples_raw = value.get("tuples")
        declared_domains = value.get("domains")
    else:
        tuples_raw = value
        declared_domains = None
    if tuples_raw is None:
        raise SchemaError(f"relation {name} must declare tuples")
    tuples = frozenset(_tuple_list(tuples_raw, f"relation {name} tuples"))
    if declared_domains is None:
        arity = len(next(iter(tuples))) if tuples else 2
        relation_domains = tuple(default_domain for _ in range(arity))
    else:
        relation_domains = tuple(_string_list(declared_domains, f"relation {name} domains"))
    for domain in relation_domains:
        if domain not in domains:
            raise SchemaError(f"relation {name} references unknown domain: {domain}")
    for relation_tuple in tuples:
        if len(relation_tuple) != len(relation_domains):
            raise SchemaError(f"relation {name} tuple has wrong arity: {relation_tuple}")
        for item, domain in zip(relation_tuple, relation_domains, strict=True):
            if item not in domains[domain]:
                raise SchemaError(f"relation {name} item {item!r} is not in domain {domain}")
    return Relation(domains=relation_domains, tuples=tuples)


def _normalize_function(
    name: str,
    value: Any,
    domains: dict[str, tuple[str, ...]],
    default_domain: str,
) -> FiniteFunction:
    if isinstance(value, dict) and "mapping" in value:
        domain = str(value.get("domain", default_domain))
        codomain = value.get("codomain")
        mapping_raw = value["mapping"]
    else:
        domain = default_domain
        codomain = None
        mapping_raw = value
    if domain not in domains:
        raise SchemaError(f"function {name} references unknown domain: {domain}")
    mapping_dict = _require_dict(mapping_raw, f"function {name} mapping")
    mapping = {str(key): str(target) for key, target in mapping_dict.items()}
    domain_values = set(domains[domain])
    bad_keys = sorted(set(mapping) - domain_values)
    if bad_keys:
        raise SchemaError(f"function {name} has keys outside domain {domain}: {bad_keys}")
    if codomain is not None:
        codomain = str(codomain)
        if codomain not in domains:
            raise SchemaError(f"function {name} references unknown codomain: {codomain}")
        bad_values = sorted(set(mapping.values()) - set(domains[codomain]))
        if bad_values:
            raise SchemaError(f"function {name} has values outside codomain {codomain}: {bad_values}")
    return FiniteFunction(domain=domain, mapping=mapping, codomain=codomain)


def _validate_domain_members(
    members: frozenset[str],
    domain: str,
    domains: dict[str, tuple[str, ...]],
    label: str,
) -> None:
    if domain not in domains:
        raise SchemaError(f"{label} references unknown domain: {domain}")
    bad = sorted(members - set(domains[domain]))
    if bad:
        raise SchemaError(f"{label} has members outside domain {domain}: {bad}")


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def _unique_string_tuple(values: Any, label: str) -> tuple[str, ...]:
    items = _string_list(values, label)
    if len(set(items)) != len(items):
        raise SchemaError(f"{label} must not contain duplicates")
    return tuple(items)


def _string_list(values: Any, label: str) -> list[str]:
    if not isinstance(values, list):
        raise SchemaError(f"{label} must be a list")
    return [str(value) for value in values]


def _tuple_list(values: Any, label: str) -> list[tuple[str, ...]]:
    if not isinstance(values, list):
        raise SchemaError(f"{label} must be a list")
    tuples: list[tuple[str, ...]] = []
    for value in values:
        if not isinstance(value, list):
            raise SchemaError(f"{label} entries must be lists")
        tuples.append(tuple(str(item) for item in value))
    return tuples

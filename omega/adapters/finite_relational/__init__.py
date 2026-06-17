"""Schema-driven finite relational adapter.

The package exposes a small universal finite relational model plus generic
audits over role-selected profiles.
"""

from omega.adapters.finite_relational.audits import AuditResult, run_audit, run_declared_audits
from omega.adapters.finite_relational.model import (
    FiniteFunction,
    FiniteRelationalModel,
    Predicate,
    Relation,
    SchemaError,
    load_model,
    load_model_path,
    model_digest,
    validate_provenance,
)

__all__ = [
    "AuditResult",
    "FiniteFunction",
    "FiniteRelationalModel",
    "Predicate",
    "Relation",
    "SchemaError",
    "load_model",
    "load_model_path",
    "model_digest",
    "run_audit",
    "run_declared_audits",
    "validate_provenance",
]

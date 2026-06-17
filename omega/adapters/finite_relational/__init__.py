"""Schema-driven finite relational adapter.

The package exposes a small universal finite relational model plus generic
audits over role-selected profiles.
"""

from omega.adapters.finite_relational.audits import AuditResult, run_audit, run_declared_audits
from omega.adapters.finite_relational.adversarial_search import (
    GeneratedAdapterCase,
    generate_adversarial_cases,
)
from omega.adapters.finite_relational.controlled_experiment import (
    ControlledExperimentCase,
    ControlledExperimentFamily,
    controlled_experiment_summary,
    generate_controlled_experiment,
)
from omega.adapters.finite_relational.derived_graph import (
    compile_derived_graph,
    compile_derived_graph_path,
    load_derived_graph_path,
)
from omega.adapters.finite_relational.finite_grid import (
    compile_finite_grid,
    compile_finite_grid_path,
    load_finite_grid_path,
)
from omega.adapters.finite_relational.grid_obstacle_experiment import (
    GridObstacleCase,
    GridObstacleStudy,
    compile_grid_obstacle_source,
    generate_grid_obstacle_study,
)
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
    "GeneratedAdapterCase",
    "ControlledExperimentCase",
    "ControlledExperimentFamily",
    "GridObstacleCase",
    "GridObstacleStudy",
    "Predicate",
    "Relation",
    "SchemaError",
    "compile_derived_graph",
    "compile_derived_graph_path",
    "compile_finite_grid",
    "compile_finite_grid_path",
    "compile_grid_obstacle_source",
    "generate_adversarial_cases",
    "generate_controlled_experiment",
    "generate_grid_obstacle_study",
    "controlled_experiment_summary",
    "load_model",
    "load_model_path",
    "load_derived_graph_path",
    "load_finite_grid_path",
    "model_digest",
    "run_audit",
    "run_declared_audits",
    "validate_provenance",
]

# Retained Results Manifest v0

Status: retained-result quarry list / Omega close checkpoint
Scope: headline retained results for successor migration
Claim boundary: navigation and migration only; not a new theorem, not full
validation, not value, not standing, not agency, not identity, not Omega
validation

## Purpose

This note is the human-readable quarry list for Alpha migration. The machine
manifest lives at:

```text
manifest.json
```

## Core Retained Results

| Result | Status | Omega path | Migration target |
| --- | --- | --- | --- |
| ODT0 / decision floor | retained Lean scaffold | `formal/lean/OmegaProper/Decision/License.lean` | Gate instance after Core. |
| Robust corridor | retained Lean theorem family | `formal/lean/OmegaProper/Decision/RobustCorridor.lean` | REACH + GATE instance. |
| Ambiguity family reduction | retained Lean theorem family | `formal/lean/OmegaProper/Decision/AmbiguityFamily.lean` | LIFT/merge instance. |
| Containment / memorylessness / trajectory bridge | retained Lean theorem family | `formal/lean/OmegaProper/Decision/Containment*.lean`; `HistoryContainment*.lean`; `Trajectory*.lean` | REACH/GATE instances. |
| Adaptive fixed-world corridor B2.1 | retained Lean theorem family | `formal/lean/OmegaProper/Decision/AdaptiveFixedWorld*.lean`; `AdaptiveObservation.lean` | REACH + LIFT(info) instance. |
| Recovery frame and recovery-aware corridor | retained Lean theorem family | `formal/lean/OmegaProper/Decision/Recovery*.lean` | Recovery/Gate instance. |
| Loss dominance | retained Lean theorem family | `formal/lean/OmegaProper/Decision/NonrecoverableLossDominance*.lean` | Profile dominance instance. |
| Expansion dominance | retained Lean theorem family | `formal/lean/OmegaProper/Decision/ExpansionDominance*.lean` | Profile dominance instance. |
| Termination supremum | retained Lean theorem | `formal/lean/OmegaProper/Decision/TerminationSupremum.lean` | Profile top-loss instance. |
| Certificate staleness | retained Lean theorem | `formal/lean/OmegaProper/Decision/CertificateStaleness.lean` | Staleness bridge instance. |
| Answerable scope | retained Lean bridge | `formal/lean/OmegaProper/Decision/AnswerableScope.lean` | Reachability-indexed bridge. |

## Finite Instruments And Witnesses

| Result | Status | Omega path | Migration target |
| --- | --- | --- | --- |
| Ensemble span | retained finite instrument | `omega/adapters/finite_relational/ensemble_span.py` | finite lab fixture. |
| Relational composability | retained finite instrument | `omega/adapters/finite_relational/relational_composability.py` | finite lab fixture. |
| Joint recovery compatibility | retained bridge instrument | `omega/adapters/finite_relational/joint_recovery_compatibility.py` | finite lab fixture. |
| Joint-tier reduction audit | retained calibration checkpoint | `omega/adapters/finite_relational/joint_tier_reduction_audit.py` | finite lab calibration. |
| Order sampling harness | retained finite calibration | `omega/adapters/finite_relational/order_sampling.py` | ORBIT(order) lab fixture. |
| CompensationClaim / NOLP v0 | retained finite harness | `omega/adapters/finite_relational/compensation_claim.py` | same-frame compensation instance. |

## Bridge / Public Artifacts

| Artifact | Status | Omega path | Migration target |
| --- | --- | --- | --- |
| Public loop note | retained public bridge | `docs/public/does_the_loop_close_soundly_v0.md` | public lineage note only. |
| Internal loop bridge | retained internal bridge | `docs/research_notes/omega_theory/does_the_loop_close_soundly_internal_bridge_v0.md` | bridge note if needed. |
| Finite lens spec | Alpha founding debt | `docs/research_notes/omega_theory/finite_lens_invariance_spine_spec_v0.md` | `Alpha/Core/GuardTheorem.lean`. |
| Static staleness protocol | closed by Lean theorem | `docs/research_notes/omega_theory/static_compensation_certificate_staleness_protocol_v0.md` | staleness bridge provenance. |

## Archive-Only

```text
quantum rungs;
large-deformer instruments;
Hopf / H2 commentary;
patienthood sketches;
cross-valuer compensation speculation;
manifesto-like fragments;
older exploratory Future Field / RFS notes.
```

These may be cited by lineage only. They do not migrate into Alpha Core.

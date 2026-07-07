# Migration To Alpha v0

Status: migration map / successor-spine plan
Scope: retained Omega artifacts and their intended Alpha destinations
Claim boundary: process only; not theorem closure, not validation, not value,
not standing, not agency, not identity, not Omega validation

## Relation

```text
omega (frozen) is the laboratory notebook: the complete, unrewritten record of
how these results were found -- protocols, dead ends, witnesses, timestamps --
preserved as evidence. alpha is the monograph: the retained results refounded on
their minimal spine, every artifact carrying a provenance link
(omega@hash:path) back to the notebook. omega shows the search; alpha shows the
structure. Claims live in alpha; testimony lives in omega.
```

## Migration Rule

```text
retained theorem:
  migrates iff it becomes an instance of a Core parametric statement;

retained witness:
  migrates as finite fixture plus recomputation test;

bridge / preregistration:
  migrates to docs/bridges/ only, with no implementation;

frozen speculation:
  stays archive-only;

historical note:
  stays in Omega, with at most a one-line lineage pointer.
```

## Generator Signatures

Alpha v0 should use:

```text
REACH;
LIFT;
LENS;
ORBIT;
GATE;
LEDGER(residue).
```

Anything unsignable is either a candidate sixth generator, a bridge, residue,
finite evidence, or archive-only.

## Migration Table

| Omega artifact | Status | Generator signature | Alpha destination | Notes |
| --- | --- | --- | --- | --- |
| `Decision/CertificateStaleness.lean` | retained theorem | LENS + LIFT(register growth) | `Alpha/Instances/Staleness.lean` | Narrow fixed-domain coverage theorem. |
| `Decision/AnswerableScope.lean` | retained theorem | REACH | `Alpha/Bridges/AnswerableScope.lean` | Named to avoid moral import. |
| Robust corridor / containment stack | retained theorem family | REACH + GATE | `Alpha/Instances/Corridor.lean` | Refactor as instances after Core reach exists. |
| Adaptive fixed-world corridor | retained theorem family | REACH + LIFT(info) | `Alpha/Instances/Adaptive.lean` | Finite strictness witnesses remain finite evidence. |
| Recovery-aware corridor | retained theorem family | REACH + GATE + LEDGER(register) | `Alpha/Instances/Recovery.lean` | Includes phantom/recovery reflection as lens instances later. |
| Loss / expansion dominance | retained theorem family | ORBIT + profile order | `Alpha/Instances/Profiles.lean` | Should be compressed under a parametric dominance theorem. |
| Order sampling harness | retained finite instrument | ORBIT(order) | `Alpha/Lab/OrderSampling/` | Evidence tag finite forever. |
| CompensationClaim / NOLP v0 | retained finite harness | GATE + certified cover | `Alpha/Instances/Compensation.lean` | Same-frame only. |
| Ensemble span | retained finite witness | non-marginal finite evidence | `Alpha/Lab/Jointness/` | Instrument, not population value. |
| Relational composability | retained finite witness | non-marginal finite evidence | `Alpha/Lab/Jointness/` | Registered coupling instrument. |
| Joint recovery compatibility | demoted bridge | LENS + recovery bridge | `Alpha/Lab/Jointness/` | Not an independent axis. |
| Colonization axis | retained finite discovery signal | LENS tower / debt open | `Alpha/Bridges/Colonization.md` | Await guard theorem before promotion. |
| Finite lens guard theorem | Alpha founding debt | LENS | `Alpha/Core/GuardTheorem.lean` | Not landed in Omega. |
| AuthorityRecord | preregistration only | LEDGER(authority) | `Alpha/docs/bridges/` | No implementation until standing/authority prerequisites exist. |
| Valuer-frame transformation | preregistration only | LENS + LEDGER | `Alpha/docs/bridges/` | Requires guard theorem. |
| Hopf / H2 obstruction hunt | frozen/preregistration | bridge only | `Alpha/docs/bridges/` | No machinery. |
| Quantum / large-deformer branches | frozen | archive-only | lineage pointer only | Do not migrate into Core. |

## Public Compression

Alpha inherits earned results, not Omega's chronology.

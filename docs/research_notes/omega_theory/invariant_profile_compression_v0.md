# Invariant Profile Compression v0

Status: theory compression note
Scope: current finite adapter audits and Layer A audit vocabulary
Claim boundary: taxonomy only; not a proof that all future audits reduce to this table; not value, agency, alignment, or Omega validation

## Compression

The current audit stack can be read through three axes:

```text
distinction:
  what differences are exposed, recovered, separated, or erased?

continuation:
  what future/path/reach/viability facts are preserved, fabricated, or hidden?

compatibility:
  which distinctions or continuations can coexist under a declared presentation,
  carrier, decoder, or joint condition?
```

Each finite audit then has four descriptors:

```text
axis;
transformation class;
tolerance mode;
failure mode.
```

## Current Audit Map

| Audit surface | Axis | Transformation class | Tolerance mode | Main failure mode |
| --- | --- | --- | --- | --- |
| `alpha_laws` | distinction | primitive exposure | exact | decorative/asymmetric labels without laws |
| `sound_presentation` | distinction + compatibility | presentation / quotient | exact forbidden merge | unsound merge |
| `nonfactorization` | distinction | summary / proxy | exact equality | same summary, different target |
| `bounded_recovery` | distinction | observation + decoder family | exact declared decoder class | target not recovered by bounded class |
| deterministic recovery layer | distinction | observation/refinement/garbling | exact | joint failure, decoder-class strictness, stale loss |
| stochastic recovery layer | distinction | stochastic channel + decoder | exact rational support / worst-case | support ambiguity, decoder gap, localization loss |
| `phantom_reachability` | continuation | abstraction / presentation | exact path existence | fabricated future |
| `hidden_reachability_loss` | continuation | stale abstraction | exact path existence | loss hidden by old model |
| stochastic continuation loss | continuation | stochastic transition perturbation | exact rational finite horizon | hit-probability loss hidden by stale abstraction |
| policy-conditioned dynamics | continuation | deterministic policy over stochastic action kernel | exact rational finite horizon | stale policy loss and support-summary non-factorization |
| `carrier_certificate` | distinction + continuation | carrier candidate | exact recurrence/closure | candidate support not certified |
| `carrier_transfer` | distinction + continuation | map/relation transfer | exact contract | transferred carrier not certified |
| joint recurrent support | compatibility | shared safety/carrier condition | exact | individual carrying without joint carrying |
| joint stochastic recovery | compatibility | stochastic channel coupling | exact rational worst-case | same marginal success, different joint success |

## Modes

The repo currently uses these tolerance modes:

```text
exact:
  Boolean or equality-level facts.

exact rational:
  finite probability facts using Fraction arithmetic.

worst-case:
  minimum over source states, avoiding undeclared priors.

declared bounded:
  only a declared decoder/resource class is allowed.
```

Deferred modes:

```text
thresholded:
  pass/fail against an explicitly declared threshold.

prior-relative:
  average success under an explicitly declared source prior.

approximate empirical:
  sampled or estimated claims with confidence/error provenance.
```

## Why This Matters

This compression keeps the project from treating every new audit as a new
ontology. A new result should say:

```text
which axis it lives on;
which transformation it tests;
which tolerance mode it uses;
which false inference it blocks.
```

If it cannot answer those questions, it is probably still speculative.

## Non-Claims

This note does not claim:

```text
these axes are complete;
finite audits validate real systems;
Omega has been defined or measured;
valuerhood or agency is detected.
```

It is a compression map for the current finite invariant-audit framework.

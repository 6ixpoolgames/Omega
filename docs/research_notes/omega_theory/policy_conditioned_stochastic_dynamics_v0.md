# Policy-Conditioned Stochastic Dynamics v0

Status: finite adapter validation note
Scope: exact rational finite MDP-style action kernels under deterministic policies
Claim boundary: synthetic finite policy-conditioned dynamics only; not full MDP policy validation, not stochastic control, not empirical transition validation, not value, agency, alignment, or Omega validation

## Purpose

The earlier stochastic continuation layer used fixed transition kernels. This
note adds the smallest policy-conditioned step:

```text
finite states;
finite actions;
exact rational transition kernel P(s' | s, a);
deterministic policy pi : state -> action;
finite-horizon hit probability.
```

This is still not a full policy-safety framework. It is a finite audit surface
for asking whether policy-conditioned continuation facts are preserved, hidden,
or missed by coarse summaries.

## Fact / Hypothesis Split

The validation runner keeps generated facts separate from hypotheses:

```text
facts.json:
  computed finite values only

hypotheses.json:
  expected interpretation, observed Boolean, pass/fail
```

This prevents the next adapter layer from baking the conclusion into the source
artifact. The family summary references both retained files but does not merge
their roles.

## Implemented Families

### Policy Stale/Reflected Hit Loss

A deterministic policy in a tiny finite MDP-like system loses target hit
probability after perturbation:

```text
before hit probability:    9/10
after hit probability:     1/10
loss amount:               4/5
stale abstraction reports: 9/10
reflected reports:         1/10
```

The hypotheses are evaluated after the facts are generated:

```text
stale_hides_policy_loss;
reflected_reports_policy_loss.
```

### Policy Non-Factorization Through Support Summary

Two policy-conditioned stochastic dynamics have the same coarse support summary:

```text
positive edge count:    4
reachable state count:  3
target reachable:       true
```

but different finite-horizon hit probabilities:

```text
high hit probability: 9/10
low hit probability:  3/5
```

This is the first policy-conditioned non-factorization witness:

```text
same coarse support summary
different policy-conditioned continuation fact
```

## Reproduction

Run:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_policy_dynamics `
  --out-root .tmp\finite_relational_policy_dynamics
```

The retained result summary is:

```text
../validation_results/finite_relational_policy_dynamics_v0.json
```

## Why This Comes Before Full MDP Validation

This layer adds actions and policies but avoids:

```text
policy optimization;
stochastic viability kernels;
learned transition estimates;
reward functions;
large state spaces.
```

The near-term point is narrower:

```text
policy-conditioned continuation facts can be hidden by stale abstraction;
coarse support summaries do not determine policy-conditioned hit probability;
generated facts should be separated from hypothesis interpretation.
```

## Non-Claims

This layer does not claim:

```text
safe policy synthesis;
Gradient Ethics validation;
alignment validation;
agency detection;
Omega measurement.
```

It is a small exact rational bridge from stochastic continuation to
policy-conditioned continuation.

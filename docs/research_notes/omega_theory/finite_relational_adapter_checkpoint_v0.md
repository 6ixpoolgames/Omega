# Finite Relational Adapter Checkpoint V0

Status: adapter checkpoint note
Date: 2026-06-18
Scope: Layer A adapter infrastructure and synthetic validation

## Summary

The finite relational adapter has reached a useful synthetic-validation
checkpoint.

The current pipeline is:

```text
finite source artifact
-> source compiler
-> finite relational IR
-> generic audit engine
-> retained provenance, digests, audit results, and summary
```

Current source layers:

```text
low-level finite relational IR;
derived graph source;
finite grid source.
```

Current generic audit kinds:

```text
alpha_laws;
sound_presentation;
phantom_reachability;
hidden_reachability_loss;
nonfactorization;
carrier_certificate;
carrier_transfer;
presentation_fact_closure.
```

This is still synthetic validation. The adapter currently audits declared finite
toy structures and generated finite hardening cases. It is not yet running
empirical studies over externally measured systems.

## What This Checkpoint Certifies

This checkpoint supports the following narrow claims:

```text
source compilers can target one finite relational IR;
generic audits can run over that IR;
retained artifacts expose source and compiled-model digests;
reserved low-level IR fields are rejected by high-level source compilers;
fixtures cover both positive and negative checks;
generated/adversarial cases can rediscover expected finite failure modes.
generated presentation/fact closure cases can test common-fact shrinkage
without hand-written Lean-only examples;
generated closure cases now include stale/reflected and multi-presentation
family intersections;
generated crosscutting closure stress now checks row, column, and parity
presentations whose full family keeps only constant facts and no ordered
visible state pairs;
generated transport closure checks a transferred endpoint-role fact without
treating transfer as identity;
generated failed-transport closure shows role-label preservation can survive
even when the transfer contract rejects carrier transfer.
the gridworld obstacle source-generator pilot now also checks reflected versus
stale source-reach presentations over the after-reachability fact.
the stochastic continuation layer now checks reflected versus stale hit-status
presentations over an after-hit target fact.
the policy-conditioned stochastic dynamics layer now checks the same
stale/reflected hit-status closure pattern under a deterministic policy.
second-source graph/grid parity now checks that strict asymmetry and recurrent
carrier certification compile to matching finite relational facts and audit
findings after state renaming;
second-source observation-closure parity checks that graph and grid sources
derive the same observation target and matching presentation/fact closure
observed payloads after state renaming.
```

The retained validation summary is:

```text
docs/research_notes/validation_results/finite_relational_adapter_validation_v0.md
```

That retained summary records:

```text
15 fixture smoke cases;
15 generated/adversarial cases;
source digests where a source compiler is used;
compiled/model digests;
audit counts;
findings;
all-passed status;
commands used;
claim boundary.
```

## What This Does Not Certify

This checkpoint does not show:

```text
that a real-world substrate has been correctly modeled;
that a passing audit implies deployment safety;
that an adapter has discovered value, agency, valuerhood, identity, or Omega;
that the finite source abstraction is empirically correct;
that carrier transfer is object identity or recoverability.
```

The adapter proves only facts relative to the declared finite structure and the
declared audit roles.

## Carrier Transfer Status

The adapter now has a narrow two-snapshot transfer audit:

```text
carrier_transfer
```

It checks:

```text
source carrier certificate succeeds;
target carrier certificate succeeds;
declared correspondence maps source endpoints to target endpoints;
declared correspondence covers the source carrier into the target carrier.
```

The positive fixture is:

```text
carrier_transfer_pass.json
```

The negative fixture is:

```text
carrier_transfer_fail_missing_return.json
```

The negative fixture matters because a declared endpoint correspondence is not
enough. The target support must still carry the recurrent return structure
needed for certification.

## Why This Is The Right Pre-Empirical Checkpoint

The core danger for adapter work is self-validation: letting a source compiler
or fixture smuggle in the exact facts the generic audit is supposed to test.

The current checkpoint pushes against that danger by requiring:

```text
one normalized audit surface;
source/compiled artifact retention;
source and compiled digests;
reserved-field rejection for high-level sources;
positive and negative fixtures;
generated/adversarial hardening cases;
CI-protected adapter smoke.
```

That makes the next phase less likely to confuse an adapter pass with empirical
truth.

## Current Empirical-Adjacent Pilot

The first empirical-adjacent finite pilot is now the gridworld obstacle
insertion generator:

```text
gridworld obstacle insertion:
  before dynamics has a path;
  after dynamics may lose the path;
  stale abstraction still reports the before path;
  reflected source-reach status reports after-dynamics reachability;
  adapter detects hidden reachability loss and source-reach fact closure.
```

This remains small, finite, and controlled, but it crosses from fixture
hardening into an instrumented-substrate workflow. The source is generated by
environment code, compiled into finite relational IR, and audited by the same
generic audit engine.

## Next Phase

The next phase should broaden empirical-adjacent source-generator coverage
without jumping to large models:

```text
additional generated grid or automaton closure cases;
broader generated closure stress tests against the same finite relational IR;
retained summaries that report both hidden-loss and invariant-closure facts.
```

The purpose is still adapter discipline, not external empirical validation.

## Non-Goals For The Next Phase

Do not start with:

```text
LLM evaluations;
frontier model behavior;
large stochastic MDPs;
unbounded empirical claims;
new source compilers without a concrete audit need;
claims about value, agency, or Omega.
```

The next phase should establish that the adapter can audit a finite substrate
generated by code outside the fixture format while preserving the current
claim boundary.

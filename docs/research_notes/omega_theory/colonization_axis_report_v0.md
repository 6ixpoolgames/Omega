# Colonization Axis Report v0

Status: retained finite discovery report / repricing note
Scope: Batch D report for the colonization-axis protocol and finite witness audit
Claim boundary: not lushness, not value, not moral standing, not agency, not identity, not global lens invariance, not Omega validation

## Verdict

Against the preregistered table in:

```text
colonization_axis_protocol_v0.md
```

the retained v0 verdict is:

```text
separated
```

The result is finite and registered-chain-relative. It does not prove a global
colonization order, global lens invariance, lushness, value, standing, or
Omega validation.

## Audit Trail

Protocol commit:

```text
bc505d3 Preregister colonization axis protocol
```

Witness/audit commit:

```text
e947bea Add colonization axis witness audit
```

Retained run:

```text
docs/research_notes/validation_results/finite_relational_colonization_axis_v0/20260706_181108/
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_finite_relational_colonization_axis.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

## Candidate Pair

The retained pair is:

```text
Branching B:
  branching_B

Basin F:
  basin_F
```

Both systems satisfy the state bound:

```text
|X| = 4 <= 12
```

## Control-Panel Equality

The preregistered control panel matched exactly:

```text
viable-state count:
  4 = 4

start-state corridor membership:
  true = true

viable-word counts:
  h=1: 2 = 2
  h=2: 4 = 4
  h=3: 8 = 8

recurrence class count:
  1 = 1

own-maintenance score:
  0 = 0

entropy proxy at h=3:
  3.0 = 3.0

leading-lambda proxy:
  2 = 2
```

The matching constraint is load-bearing. The separation claim depends on these
equalities.

## Colonization Separation

The retained certified-chain profiles differ:

```text
branching_B:
  certified partition count: 5
  certified chain count: 10
  includes chain signature: 1-2-4

basin_F:
  certified partition count: 2
  certified chain count: 1
  chain signature: 1-4
```

The registered order comparison found:

```text
branching_B colonization-refines basin_F:
  true

basin_F colonization-refines branching_B:
  false
```

The separating matched chain is:

```text
branching_B: 1-2-4
basin_F:     1-4
```

with strict surplus at the intermediate level.

## Demotion Gauntlet

### 1. Lens / Presentation Audit

The v0 audit checked that the registered chains are certified under the finite
harness and that the strict-surplus chain has the declared transport match:

```text
registered_chains_certified:
  true

strict_surplus_has_chain_transport:
  true
```

Caveat:

```text
This is not a global lens-invariance theorem.
```

### 2. Converse Witness Attempt

The retained converse attempt uses two systems with the same colonization
profile and different declared joint behavior:

```text
same_colonization_profile:
  true

joint_behavior_differs:
  true
```

This prevents overreading the coordinate as determining the older corridor or
joint-effect surfaces.

### 3. Scalar-Shadow Check

The scalar-shadow check used chain signatures:

```text
left:  1-3-6
right: 1-2-6
```

The obvious scalar summaries matched:

```text
level_count:
  3 = 3

max_branching_ratio:
  3.0 = 3.0
```

but the order still separated:

```text
order_separates:
  true
```

This blocks the immediate reduction:

```text
just use level count or max branching ratio.
```

## Repricing

The sprint promotes the following from speculative phrase to live candidate
coordinate:

```text
cross-scale certified viable refinement
```

It does not promote:

```text
lushness as value;
lushness as a scalar;
colonization as global theorem;
colonization as moral standing;
colonization as Omega validation.
```

Practical repricing:

```text
colonization / cross-scale viable refinement:
  live candidate coordinate

lushness:
  still open; now has one finite candidate component

ColonizationOrder.lean:
  plausible but deferred until audit or at least one independent retained pair

Helmholtz / curl interpretation:
  still interpretation, not formal structure
```

## Claim Boundary

This report supports only:

```text
there exists a retained finite pair, under the v0 registered-chain definition,
where ordinary control-panel quantities match and certified viable-refinement
structure separates.
```

It does not support:

```text
that richer-is-better;
that lushness is derived;
that cross-scale refinement has moral force;
that the coordinate is globally lens-invariant;
that the coordinate survives arbitrary presentation changes;
that value, agency, standing, identity, or Omega has been derived.
```

## Next

Do not immediately build the full Lean order unless auditors accept the finite
definition.

The clean next options are:

```text
1. find one independent retained pair under the same protocol;
2. prove a small registered-chain order in Lean, with no lushness/value claims;
3. return to the prior queue: vortical witness suite, Senchal/loop-closure
   synthesis, or endogenous register/no-laundering.
```

## Public Compression

```text
The finite colonization-axis audit found a separated signal: two systems match
ordinary viability, word-count, recurrence, entropy, and maintenance summaries,
but differ in certified cross-scale viable-refinement structure. This makes
colonization a live candidate coordinate for descriptive lushness, not a proof
of value or moral standing.
```

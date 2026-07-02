# Closure Discovery V0

Status: adapter characterization note
Scope: generated finite presentation/fact closure discovery
Claim boundary: finite adapter-relative discovery; not empirical substrate validation, not value, not agency, not Omega

## Purpose

Earlier closure pilots answered a useful but weaker question:

```text
given a declared family of presentations and declared candidate facts,
which candidate facts are common to every presentation?
```

That can certify a supplied candidate surface, but it can still overfit to the
facts we chose to list. Batch F adds a discovery path:

```text
generate a small substrate;
derive or choose a seed fact;
generate all finite presentations of the carrier;
generate all Boolean predicate and ordered-pair facts;
compute closure(seed);
record surplus without predeclaring expected surplus.
```

The decisive output is:

```text
nonconstant surplus target facts
```

If that set is empty, the closure did not generate positive nonconstant
structure beyond the seed. If it is nonempty, the generated presentation
universe forced additional finite structure.

## Implementation

The generator lives at:

```text
omega/adapters/finite_relational/closure_discovery.py
```

The retained validation runner is:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_closure_discovery `
  --out-root .tmp\finite_relational_closure_discovery
```

The runner retains:

```text
summary.json
family_summary.json
cases.json
representative model.json
representative model_digest.txt
representative observed_closure.json
representative summary.json
```

## Families

The current finite discovery sweep has three families.

```text
predicate_seed_partition_sweep:
  all Boolean seed predicates over three states.

reachability_seed_graph_sweep:
  all loop-free directed graphs on three states;
  seed predicate is derived as can-reach-goal.

viability_seed_graph_sweep:
  all loop-free directed graphs on three states;
  seed predicate is derived as the finite viability kernel under all-safe states.
```

Each family records both positive and collapse controls. The important point is
that the controls are discovered by classification after the sweep; the cases
do not include expected surplus fields or declared audit pass/fail expectations.

## Current Result

The retained Batch F run reports:

```text
case_count: 136
nonconstant_surplus_case_count: 50
collapse_case_count: 86
```

By family:

```text
predicate_seed_partition_sweep:
  8 cases;
  6 nonconstant-surplus cases;
  2 collapse cases.

reachability_seed_graph_sweep:
  64 cases;
  32 nonconstant-surplus cases;
  32 collapse cases.

viability_seed_graph_sweep:
  64 cases;
  12 nonconstant-surplus cases;
  52 collapse cases.
```

This is not a claim that nonconstant surplus survives every adversarial
presentation class. It says that, over these small generated universes, closure
sometimes forces nonconstant structure and sometimes collapses. Both outcomes
are retained.

## Redundancy Classification

The first cleanup pass classifies the current surplus into easy closure
consequences versus unclassified surplus:

```text
seed-complement target facts: 50
unclassified nonconstant target facts: 0
seed-separation visible-pair facts: 200
unclassified visible-pair facts: 0
```

This is deliberately not a canonical implication basis. It only separates the
obvious v0 redundancies:

```text
seed complement:
  if a seed predicate is forced, its complement is also constant on exactly the
  same admissible presentation fibers.

seed separation:
  if a seed predicate has different truth values on two states, admissible
  presentations cannot merge those states, so ordered cross-fiber visible-pair
  facts are forced.
```

The current sober read is therefore:

```text
the generated closure engine produces facts beyond the seed;
the current v0 positives are explained by complement and separation effects;
the richer dynamic-surplus bucket is empty in this sweep.
```

The next useful closure work should broaden the fact language before claiming
positive dynamic content from closure discovery.

## Reading The Result

The positive cases are modest but meaningful:

```text
seed constraints can force complement target facts and visible-pair facts
without those facts being predeclared.
```

The collapse cases are equally important:

```text
constant or globally uninformative seeds admit every presentation,
so no nonconstant target fact survives closure.
```

This is the adapter version of the generate-versus-certify question:

```text
does closure produce structure beyond what was supplied?
```

The current answer is:

```text
yes on some small generated finite substrates;
no on collapse controls;
not yet established generically or empirically.
```

## Non-Claims

This note does not claim:

```text
real-world substrate validity;
generic positive content at scale;
agency;
identity;
value;
valuerhood;
Omega;
that this closure universe is the final admissibility universe.
```

## Next Questions

The natural next extensions are:

```text
larger finite carriers with sampling rather than exhaustive enumeration;
seed facts derived from path-lifting and observed-word language surfaces;
held-out generated families with no hand-selected positive cases;
canonical implication bases for the generated presentation/fact context.
```

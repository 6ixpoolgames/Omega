# Omega Decision Arbitration v0

Status: ODT2 scaffold / registered arbitration under incomplete value
Scope: finite least-violation arbitration over a declared candidate frontier
Claim boundary: not final value, not correct standing relation, not moral
standing, not valuerhood, not aggregation theory, not Nash bargaining, not
Arrow/Sen theorem, not max-entropy default, not stochastic risk, not agency, not
identity, not selfhood, not quantum mechanics, not Omega validation

## Purpose

ODT0 licenses. ODT1 compares. ODT2 arbitrates only when a candidate frontier
remains unresolved and only relative to registered arbitration data.

ODT2 v0 is intentionally procedural:

```text
finite candidate frontier
+ declared Nat-valued violation score
-> exists a least-violation candidate
```

The theorem proves that the procedure respects the registered order. It does
not prove that the registered order is morally final.

## Relation To ODT0 And ODT1

ODT0 answers:

```text
May this action or plan be used at all?
```

ODT1 answers:

```text
Does one already-licensed outcome surface dominate another under the declared
outcome preorder?
```

ODT2 begins only when ODT1 leaves a finite frontier unresolved and an external
registration supplies arbitration data.

## Registered Arbitration

The Lean scaffold defines:

```text
NatViolationFrame:
  candidates : Finset Option
  nonempty   : candidates.Nonempty
  violation  : Option -> Nat
```

The candidate predicate is just membership in the registered frontier.

## Least-Violation Fallback

A candidate `x` is least-violation when:

```text
x is registered as a candidate
and
violation(x) <= violation(y)
for every registered candidate y.
```

The Lean theorem proves:

```text
exists_leastViolation:
  every nonempty finite NatViolationFrame has a least-violation candidate.
```

The noncomputable chooser:

```text
leastViolationChoice
```

selects such a candidate, and:

```text
leastViolationChoice_spec
```

proves that the selected candidate satisfies the registered minimality
condition.

## Authority Hole

ODT2 v0 does not decide:

```text
whose standing counts;
which harms or violations matter;
which tie-breakers are legitimate;
whether the Nat score is the right score;
whether one violation point is commensurable with another;
whether arbitration should be allowed at all.
```

Those are typed holes for later standing/valuer layers or explicit external
registration. This file only proves the finite least-violation procedure.

## Toy Example

The retained Lean example has three options:

```text
a -> 2
b -> 0
c -> 1
```

The theorem `toy_b_is_leastViolation` proves that `b` is least-violation for
the registered frame. The chooser theorem proves that any selected least
violation has registered score `0`.

## Nonclaims

ODT2 v0 does not claim:

```text
final value;
correct standing relation;
moral standing;
valuerhood;
aggregation theory;
Nash bargaining;
Arrow/Sen theorem;
max-entropy default;
least-violation legitimacy;
stochastic risk;
agency;
identity;
selfhood;
quantum mechanics;
Omega validation.
```

## Next Steps

Possible next steps are documentation and interface work, not authority claims:

```text
frame-stability criteria under certified presentation changes;
explicit tie handling;
typed authority records;
least-violation interaction with ODT0 licensing and ODT1 frontiers.
```

## Public Compression

ODT2 begins as registered arbitration: when ODT1 leaves a finite frontier
unresolved, a declared violation order can select a least-violation option. The
theorem proves the procedure respects the registered order, not that the order
is morally final.


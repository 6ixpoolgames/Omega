# Omega Decision Dominance v0

Status: research note / formal specification / thin Lean scaffold
Scope: finite preorder dominance over ODT0-licensed option outcome surfaces
Claim boundary: not final value, not aggregation, not arbitration, not agency, not identity, not valuerhood, not moral standing, not probability-aware risk handling, not stochastic Blackwell theory, not quantum mechanics, not Omega validation

## Purpose

ODT0 licenses. ODT1 compares.

ODT1 v0 is a small value-parametric comparison layer over already-licensed
option outcome surfaces. It does not choose a best action. It does not define
value. It does not aggregate competing standing claims. It returns partial
comparison structure and failure witnesses.

Public compression:

```text
ODT1 compares ODT0-licensed options by dominance over declared continuation
outcomes. The comparison is value-parametric, not value-free: the outcome
preorder and admissible valuation class are registered commitments. The layer
returns partial orders and proof-carrying incomparability certificates rather
than forcing a scalar best action.
```

## Relation To ODT0

ODT0 asks:

```text
May this action or plan be used at all?
```

ODT1 asks:

```text
Given already-certified outcome surfaces, does one option dominate another
under the declared outcome preorder?
```

The v0 Lean layer keeps this bridge abstract:

```text
LicensedOption W
  Achievable : W -> Prop
  nonempty   : exists w, Achievable w
```

In later work, `Achievable` should be produced by an ODT0 `LicenseVia` or
`PlanLicense` plus a certified outcome-surface compiler. ODT1 v0 does not
force that integration.

## Outcome Preorder

Let:

```text
W : continuation outcome type
<= : declared preorder over W
A, B : W -> Prop
```

where `A` and `B` are achievable outcome surfaces for two already-licensed
options.

The preorder is ledger content. ODT1 does not derive the correct preorder and
does not claim that any declared preorder is morally complete.

Lean file:

```text
formal/lean/OmegaProper/Decision/Dominance.lean
```

## Hoare / Angelic Dominance

Definition:

```text
HoareDominates A B
  := forall b, B b -> exists a, A a and b <= a
```

Reading:

```text
Every B-achievable outcome is no better than some A-achievable outcome.
```

This is the opportunity or angelic order. It asks whether A can match or exceed
each B possibility somewhere in A's surface.

Checked lemmas:

```text
hoare_refl
hoare_trans
```

## Smyth / Demonic Dominance

Definition:

```text
SmythDominates A B
  := forall a, A a -> exists b, B b and b <= a
```

Reading:

```text
Every A-achievable outcome is at least as good as some B-achievable outcome.
```

This is the guarantee or demonic order. It asks whether even A's outcomes have
a B floor beneath them.

Checked lemmas:

```text
smyth_refl
smyth_trans
```

## Plotkin / Both-Cases Dominance

Definition:

```text
PlotkinDominates A B
  := HoareDominates A B and SmythDominates A B
```

Checked lemmas:

```text
plotkin_refl
plotkin_trans
```

This is still not arbitration. It is a stronger partial comparison relation.

## Failure Certificates

Dominance failure is proof-carrying.

Hoare failure:

```text
HoareFailureCertificate A B b
  := B b and forall a, A a -> not (b <= a)
```

Meaning:

```text
b is a B-achievable outcome that no A-achievable outcome reaches or exceeds.
```

Smyth failure:

```text
SmythFailureCertificate A B a
  := A a and forall b, B b -> not (b <= a)
```

Meaning:

```text
a is an A-achievable outcome with no B-achievable lower/floor outcome beneath it.
```

Checked equivalences:

```text
not_hoare_iff_exists_failure_certificate
not_smyth_iff_exists_failure_certificate
```

These use classical reasoning, as expected: they move from a negated universal
dominance claim to an explicit separating witness.

## Value-Parametric Reading

ODT1 is value-parametric, not value-free.

The structural dominance relations use a declared preorder. A separate
valuation class can be placed over that preorder. The v0 Lean bridge defines:

```text
MonotoneValuation (v : W -> Nat)
  := forall x y, x <= y -> v x <= v y

UpIndicator b w
  := if b <= w then 1 else 0
```

Checked lemma:

```text
upIndicator_monotone
```

This is not a full acceptance theorem. It is a small bridge showing how
monotone valuation discipline relates to the declared order.

## Finite Examples

Example file:

```text
formal/lean/OmegaProper/Decision/DominanceExamples.lean
```

### W1: Incomparability

Outcome type:

```text
{a,b,c}
```

with discrete preorder.

Surfaces:

```text
A = {a,b}
B = {b,c}
```

Checked result:

```text
W1_incomparable
```

This uses three outcomes. The note intentionally avoids the false claim that
overlapping non-nested sets exist on two outcomes.

### W2: Angelic/Demonic Divergence

Outcome chain:

```text
low < mid < high
```

Surfaces:

```text
A = {low, high}
B = {mid}
```

Checked result:

```text
W2_angelic_demonic_diverge
```

Truth table:

```text
A Hoare-dominates B: true
B Hoare-dominates A: false
A Smyth-dominates B: false
B Smyth-dominates A: true
```

This is the key ODT1 warning: opportunity and guarantee comparisons are
different orders.

### W5: Valuation-Class Relativity

Outcome chain:

```text
low < high
```

Surfaces:

```text
A = {high}
B = {low}
```

Checked structural result:

```text
A Hoare-dominates B
A Smyth-dominates B
```

Then a nonmonotone valuation is defined:

```text
prefersLow low  = 1
prefersLow high = 0
```

Checked result:

```text
prefersLow_prefers_low
prefersLow_not_monotone
```

Interpretation:

```text
Under monotone valuations, high dominates low.
Under arbitrary valuations, a declared valuer can prefer low to high.
Therefore the admissible valuation class is real ledger content.
```

## Acceptance Theorem Roadmap

The intended later theorem shape is:

```text
Hoare dominance
  iff every monotone valuation weakly prefers A by best-case value.

Smyth dominance
  iff every monotone valuation weakly prefers A by worst-case value.
```

This requires finite optimization machinery over nonempty finite outcome
surfaces. It is not part of v0.

## Blackwell Positioning

ODT1 is Blackwell-shaped but does not prove Blackwell.

The deterministic finite Blackwell comparison is a conservativity target:
deterministic experiments correspond to presentations, and dominance should
recover the existing factorization criterion in a later wrapper theorem.

Do not read this note as:

```text
ODT1 proves Blackwell.
```

Read it as:

```text
ODT1 supplies a finite order-theory surface designed to receive a later
deterministic Blackwell conservativity wrapper.
```

## Deferred Items

Not implemented here:

```text
ODT2 arbitration
ODT3 tiling/reflection
standing or valuerhood
aggregation
Nash / Arrow / Sen
max-entropy or Omega-sampling defaults
least-violation fallback
stochastic dominance
Le Cam deficiency
Farkas separation
Blackwell theorem wrapper
dimension groups
approachability
quantum licensing
Hilbert spaces
density operators
agency detection
identity or selfhood
moral standing
```

## ODT2 Stub

ODT2 is registered arbitration under incomplete value.

It should be a calculus parameterized by standing and valuation commitments. It
is not a theory of standing. It should only open after ODT1's structural
dominance layer is stable.

## Non-Claims

ODT1 v0 does not claim:

```text
final value
correct valuation class
aggregation
arbitration
agency
identity
selfhood
valuerhood
moral standing
probability-aware risk
stochastic Blackwell theory
quantum mechanics
Omega validation
```

It defines partial dominance, proves certificates, and returns
incomparability when the declared structure does not decide.

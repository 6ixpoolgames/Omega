# Baseline Witness Theorem Schema

Status: theory note for witness-suite compression.

The v0 witness suite should now be compressed into common schemas rather than
expanded with more one-off examples. This note states the shared pattern in a
form that can guide future Lean transfers.

## Generic Pattern

Many retained witnesses instantiate this shape:

```text
There exist finite systems S1 and S2 over a declared carrier/panel such that:

  baseline_summary(S1) = baseline_summary(S2)

but

  declared_target(S1) != declared_target(S2).
```

The declared target may be:

```text
declared recovery;
loss profile;
joint success;
merge soundness;
class soundness;
consequence profile.
```

The point is not that the baseline summary is useless. The point is that the
baseline summary does not determine the declared consequence-bearing fact.

## Coordinate Split Schema

Several witnesses use a finite carrier with a declared coordinate and a
nuisance coordinate:

```text
X = D x N
```

The construction arranges two systems or abstractions:

```text
S_declared carries or recovers D
S_nuisance carries or recovers N
```

The matched baseline is chosen so that:

```text
baseline_summary(S_declared) = baseline_summary(S_nuisance)
```

while the declared target distinguishes them:

```text
declared_recovery_D(S_declared) succeeds
declared_recovery_D(S_nuisance) fails
```

This schema covers the current reachability-like, information-like, rank-like,
control-like, optimization-like, and viability-like families at finite depths.

## Pairwise Soundness Schema

Some witnesses are about proposed identifications or classes rather than
declared recovery:

```text
same chain evidence does not imply class soundness;
same compression score does not imply merge soundness;
same coarse partition does not imply exact consequence profile.
```

The shared form is:

```text
coarse_evidence(A) = coarse_evidence(B)

but

exact_profile_or_soundness(A) != exact_profile_or_soundness(B).
```

These are closest to the current Lean consequence stack because they can be
stated as exact finite merge-block / merge-allow facts.

## Lean Transfer Strategy

Do not try to formalize all thirteen patterns at once.

Preferred order:

```text
1. exact finite soundness/profile counterexamples;
2. finite coordinate-split recovery counterexamples;
3. common finite schema over X = D x N;
4. parameterized finite families;
5. infinite-family theorem only after the finite schema is stable.
```

Current finite Lean transfers:

```text
reachability / declared recovery
mutual information / declared recovery
chain evidence / class soundness
compression score / merge soundness
coarse bisimulation / consequence profile
```

Recommended next finite Lean transfers:

```text
observation rank / declared recovery
control reach / declared recovery
```

## Search Before More Witnesses

Before adding a new retained witness pattern, prefer asking whether a finite
search can rediscover or stress the pattern:

```bash
python -m omega.baseline_witnesses.search --match-baseline mutual_information --separate declared_recovery --states 8 --trials 10000
python -m omega.baseline_witnesses.search --match-baseline reachability --separate declared_recovery --states 8 --trials 10000
```

Search output is supporting evidence only. It does not replace retained
artifact regeneration, focused tests, or Lean transfer.

## Claim Boundary

The schema does not claim:

```text
all baseline summaries fail;
all coarse summaries are invalid;
declared targets are automatically meaningful;
finite counterexamples transfer to arbitrary substrates;
Omega is validated.
```

It claims only:

```text
for the declared finite constructions, the matched baseline does not determine
the declared consequence/recovery/soundness target.
```

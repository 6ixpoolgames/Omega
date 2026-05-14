# Minimal DAR Rule-Space Persistence

DAX-G0 changes the primitive-branch posture from custom substrate design to
rule-space audit.

The current primitive definitions are:

```text
distinction = difference
asymmetry   = consequence
relation    = dependence
```

In the smallest one-dimensional cellular rule space:

```text
distinction:
  q > 1 symbols

relation:
  radius r > 0 neighborhood dependence

asymmetry:
  nontrivial temporal update plus irreversible, directional, or
  non-left-right-symmetric consequence
```

The purpose of DAX-G0 is not to choose an interesting world. It enumerates the
elementary cellular automata rule space:

```text
q = 2
radius = 1
rule_count = 256
```

and asks whether nontrivial persistence appears as a detectable phase.

The target is not frozen global order, whole-grid periodicity, or raw chaotic
activity. The target is:

```text
compact pattern identity through transformation
```

Operationally, this means localized or semi-localized structures that persist
with contrast, recurrence up to shift, and some material turnover. Static
blocks, immediate extinction, and global chaotic activity are controls, not
successes.

DAX-G0 is still not an Omega validation probe. A positive result would only show
that the minimal DAR-capable rule space contains nontrivial persistence and that
such persistence is enriched among relation-dependent and asymmetric or
irreversible rules. It would motivate a follow-up anatomy probe, not a theory
claim.

## DAX-G1 Update

DAX-G1 ran that anatomy probe. It confirmed four robust emitter-like persistence
motif rules:

```text
169, 225, 73, 109
```

These rules survived horizon/ring-size checks and light perturbation, and the
major collapse, frozen, chaotic, identity, and shift controls were rejected.

The update is scientifically mixed. The persistence motifs look real, but the
strong G0 enrichment story narrows under stricter filtering:

```text
DAR-complete enriched after filter: false
DAR-asymmetric enriched after filter: false
relation-dependent enriched after filter: true
asymmetry-dependent enriched after filter: false
```

The interaction sidecar was also negative:

```text
composition-positive motifs: 0
best stable product rate: 0.000
```

So the correct interpretation is:

```text
minimal rule space contains robust local persistence motifs;
relation-dependence remains the live primitive signal;
asymmetry and composition are not yet established by G1.
```

## DAX-G2 Smoke Update

DAX-G2 made the smallest principled expansion beyond ECA:

```text
q=3, radius=1
q=2, radius=2
```

The budgeted smoke produced encouraging hits:

```text
q3/r1 confirmed motifs: 6
q2/r2 confirmed motifs: 3
q3/r1 relation positives: 4
q3/r1 asymmetry positives: 5
q3/r1 composition positives: 4
```

But the guardrail failed:

```text
controls_rejected: false
q3/r1 control leaks: 18
q2/r2 control leaks: 16
```

So G2 should be read as:

```text
minimal expansion is promising enough to continue;
the current expanded-space persistence classifier is too permissive;
full G2 scale-up should wait for a metric guardrail revision.
```

## DAX-G2b Update

DAX-G2b applied the needed matched-control guardrail. The q=3/r=1 control leaks
were resolved, and one q=3/r=1 candidate survived as a clean
control-adjusted-positive rule:

```text
q3r1_s1_0002
```

Profile:

```text
adjusted_persistence: 0.0734
relation_load_bearing_adjusted: 0.0755
asymmetry_load_bearing_adjusted: 0.1686
local_phase_fakeout_rejected: true
composition_adjusted_delta: 1.000
dominant_interaction_outcome: new_motif
```

The previous headline candidate `q3r1_s5_0016` remains interesting for
relation/asymmetry load-bearing, but its interaction signal is emission-only:

```text
reclassification: emission_only
```

Current implication:

```text
q=3/r=1 is now justified as the next primitive-branch trunk,
but the trunk should be guardrailed from the start.
```

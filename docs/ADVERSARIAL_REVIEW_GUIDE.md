# Adversarial Review Guide

This guide invites hostile review of the baseline witness suite.

The project is not asking reviewers to accept Omega. The useful question is
whether the finite non-reduction witnesses actually show what they claim under
their declared controls.

## Start Here

Read:

```text
docs/BASELINE_WITNESS_SUITE_V0.md
docs/BASELINE_WITNESS_SMOKE.md
docs/BASELINE_WITNESS_FAMILY_SMOKE.md
docs/KNOWN_REDUCTIONS_AND_BASELINES.md
docs/CLAIMS_LEDGER.md
```

Then reproduce:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1
```

## Attack Questions

Use these as review prompts:

```text
Which witness is trivial or tautological?
Which baseline summary is too weak to be worth defeating?
Which construction secretly changes the object being measured?
Which witness reduces to a standard theorem already known under another name?
Which witness should be deleted from v0?
Which stronger matched controls would be fair?
Which declared recovery/consequence target is post-hoc or under-justified?
Which family extension merely pads the one-off witness?
Which result depends on finite toy artifacts that obviously vanish at scale?
Which Lean conversion is too far from the Python witness it claims to anchor?
Can the hand-built witness be rediscovered by finite adversarial search?
```

## Fair Stronger Controls

A useful attack should propose a stronger replacement gate. Examples:

```text
match full source/target support, not only counts;
match per-source reachable target count signatures;
match transition determinism and edge counts;
match class-count and class-size signatures;
match marginal summaries and then test joint/profile recovery;
declare the recovery target before scoring;
mutate retained summaries and verify the smoke rejects them;
search for counterexamples rather than hand-building them.
```

## Search Entry Point

The current search helper is intentionally small. It searches finite channel
candidates for matched-baseline / different-declared-recovery patterns.

Examples:

```bash
python -m omega.baseline_witnesses.search --match-baseline mutual_information --separate declared_recovery --states 8 --trials 10000
python -m omega.baseline_witnesses.search --match-baseline reachability --separate declared_recovery --states 8 --trials 10000
```

It does not claim exhaustive search or substrate-general discovery. Its job is
to make the hand-built witness patterns easier to attack and rediscover.

## What Would Falsify a Witness

A witness should be weakened, revised, or deleted if:

```text
the retained summary cannot be regenerated;
the matched baseline controls are not actually matched;
the separated target fact is computed from a different carrier or panel;
the witness status remains true after destroying the declared target;
the same result follows only because the comparison was chosen post hoc;
the witness claims more than the artifact proves.
```

## What Would Strengthen the Suite

High-value improvements:

```text
promote a witness to a small exact Lean theorem;
add an adversarial search reproduction for a hand-built witness;
replace a weak baseline with a stronger matched baseline;
make a Python runner cross-platform;
add mutation tests that corrupt the relevant retained fact;
write the theorem schema that multiple witnesses instantiate.
```

## Review Boundary

Do not treat a successful attack on a witness as an attack on every part of the
project. The suite is deliberately modular. A fair review can say:

```text
keep these witnesses;
revise these controls;
delete these witnesses;
do not infer this larger claim.
```

That is the intended review mode.

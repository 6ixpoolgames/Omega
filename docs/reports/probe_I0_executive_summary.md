# Probe I0 Executive Summary

Probe I0 was a longer invariant-stack audit of the trajectory-native branch. It
asked whether a cumulative stack of single-Omega-style invariants could reject
the known T1/T1F fakeouts while still retaining the coupled multifield target.

## Run

- Script: `scripts/historical_probes/probe_I0_invariant_stack_audit.py`
- Results: `probe_I0_invariant_stack_audit_results/`
- Scale: `15000` trajectories, `180` seeds, `300` bootstraps
- CPU: 18 workers
- GPU: used for metric batches throughout
- Runtime: about 47.3 minutes
- Thermal result: max GPU temperature `49 C`, no thermal throttle events

## Invariant Scores

```text
I1 viability:                           1
I2 ordered distinction persistence:     2
I3 component non-erasure:               3
I4 counterfactual affordance relevance: 2
I5 minimal recoverability:              1
I6 horizon coherence:                   1
```

The strongest individual invariant was component non-erasure. Ordered
distinction persistence and counterfactual affordance relevance were
diagnostically useful but not sufficient. Viability, recoverability, and horizon
coherence were either too close to raw survival or too strict under the current
thresholding.

## Ablation

The ablation is the main result:

```text
S1: retention 0.444, known rejection 0.556, holdout rejection 0.556
S2: retention 0.111, known rejection 0.917, holdout rejection 0.833
S3: retention 0.111, known rejection 1.000, holdout rejection 0.833
S4: retention 0.000, known rejection 1.000, holdout rejection 0.944
S5: retention 0.000, known rejection 1.000, holdout rejection 1.000
S6: retention 0.000, known rejection 1.000, holdout rejection 1.000
```

Adding invariants improves false-positive rejection, but it also destroys
coupled retention. S5 is the best apparent stack by rejection: it rejects all
known controls and both holdouts. But it retains none of the coupled target, so
it is not a scientific pass.

This means the invariant stack acts like an overstrict rejection filter rather
than a recovered mathematical object.

## Interpretation

Probe I0 does not falsify the broader Omega project. It does narrow the search.
The trajectory-native invariant branch has now failed three ways:

- T1: simple trajectory geometry admitted noise/time-shuffle fakeouts.
- T1F: ordered structure improved diagnostics but still admitted endpoint and
  one-component fakeouts.
- I0: stacked invariants reject fakeouts, but only by rejecting the coupled
  target too.

The clean conclusion is:

```text
Demote the trajectory-native branch for now.
Return to COM fiber-transport formalization.
```

The positive lesson is methodological. The workflow can now run CPU/GPU
validation passes at useful scale, generate holdout controls, and expose whether
an apparent witness survives ablation. Here, it did not.

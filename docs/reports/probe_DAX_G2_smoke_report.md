# Probe DAX-G2 Smoke Report

Date: 2026-05-14

Script:

- `scripts/historical_probes/probe_DAX_G2_persistence_phase_map_minimal_rule_spaces.py`

Result directory:

- `results/historical_probes/probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results/`

## Purpose

DAX-G2 asks whether G1's missing invariants, especially asymmetry and
composition, were absent because ECA is too small or because the persistence
object itself is limited.

This smoke tested two minimal expansions:

- q=3/r=1: more distinction richness.
- q=2/r=2: more relation context.

## Run

- q=3/r=1 sampled rules: `350`
- q=2/r=2 sampled rules: `350`
- ECA anchors: `33`
- stage 1: `T=192`, ring `256`, `48` seeds
- stage 2: `T=512`, ring `256`, `64` seeds
- stage 2 cap: `90`
- workers: `18`
- runtime: about `3.1` minutes

GPU was not used. The workload is many small cellular automaton simulations and
motif bookkeeping, which fits CPU multiprocessing better than dense GPU kernels.

## Main Result

```text
ECA_anchor confirmed motifs: 2
q3_radius1 confirmed motifs: 6
q2_radius2 confirmed motifs: 3

q3_radius1 relation positives: 4
q3_radius1 asymmetry positives: 5
q3_radius1 composition positives: 4

q2_radius2 relation positives: 2
q2_radius2 asymmetry positives: 1
q2_radius2 composition positives: 2
```

Best candidate:

```text
space: q3_radius1
rule_id: q3r1_s5_0016
stratum: S5_asymmetric_neighbor_dependent
confirmed_fraction: 0.75
recurrence_up_to_shift: 0.772
material_turnover_rate: 0.234
relation_dependence_delta: 0.0276
asymmetry_dependence_delta: 0.0785
post_perturbation_survival_rate: 1.000
composition_outcome: emission
frozen_order_index: 0.0157
chaos_index: 0.101
```

## Guardrail Failure

```text
controls_rejected: false
q3_radius1 control leaks: 18
q2_radius2 control leaks: 16
```

The expanded spaces did improve over ECA on the headline smoke readouts, but
the control leak blocks interpretation. The current classifier allows too many
symmetric or center-dominant controls into persistence-positive classes.

## Interpretation

The smoke is promising enough to continue the q=3/r=1 branch. It is not strong
enough to scale the full G2 main pass. The immediate issue is metric
admissibility:

```text
persistence exists,
but load-bearing persistence is not yet separated cleanly from control leakage.
```

The composition readout is also preliminary. Several positives are broad
emission outcomes, not yet stable compositional motif algebra.

## Recommendation

Run a DAX-G2 metric guardrail revision before any larger phase map:

- separate generic persistence from load-bearing persistence;
- require control-adjusted relation/asymmetry deltas;
- make symmetric/self-control leakage a hard blocker;
- refine interaction composition so emission, chaos, and stable products are
  separated more cleanly.

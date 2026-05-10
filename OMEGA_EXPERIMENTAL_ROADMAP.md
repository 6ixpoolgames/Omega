# Omega Experimental Roadmap

Status: working roadmap after the first single-world and larger CPU validation probes.

Stance: skeptically open. Treat Omega as a candidate formal object until it produces definitions, discriminators, and failure modes that survive controls.

## 1. Current Empirical Position

The current executable object is:

```text
I_T^C(s) = H(F_T(s) / C)
```

where `F_T(s)` is the set of viable trajectories from state `s` to horizon `T`, `C` is a coarse-graining, and `H` is Shannon entropy over distinguishable viable macro-trajectory classes.

The first finite-world sanity check showed that the implementation can separate:

- raw reachability from viable trajectory diversity;
- survival from future diversity;
- noise/swamp branching from structured viable futures;
- rigid survival from non-degenerate future space.

The larger CPU probe showed that the workflow can run many randomized finite-world variants in parallel on local hardware.

Important limitation: the larger pass is primarily an environment and workflow validation. Because trajectory enumeration is capped, many final-horizon `raw_count` values saturate at `max_traj`, so final-horizon values should not be treated as unbiased estimates of the invariant.

## 2. Hardware / Workflow Baseline

Machine profile observed by Python:

- logical CPUs: 24
- calibrated heavy CPU profile: 18 worker processes
- observed CPU usage: approximately 80%
- calibrated command:

```powershell
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_MAX_THREADS='1'
.\.venv\Scripts\python.exe larger_omega_cpu_validation.py --workers 18 --worlds 90 --max-traj 18000 --horizons 6,7,8 --out-dir omega_cpu_validation_results_18worker_calibration
```

Use this as the default "heavy but usable" local workload. Reserve 22+ workers for stress testing only.

## 3. What The Probe Revealed

Environment:

- The local Python environment is capable of long multi-process jobs.
- Process-level parallelism is the right default for these enumeration-heavy tests.
- `18` workers is the current practical CPU target.
- The result pipeline can write CSV and JSON artifacts reliably.

Modeling:

- `I_region`, `I_viab`, and `I_random` do not collapse completely into survival or raw reachability.
- Rigid attractors behave correctly as a survival/Omega separator.
- Noise swamp behavior is a useful diagnostic for "raw entropy is not structured viability."
- Random coarse-graining often produces higher entropy than meaningful coarse-grainings. This is expected but dangerous: high entropy alone is not evidence of admissible structure.

Main warning:

- Coarse-graining admissibility is now the central problem. Without an admissibility criterion, random labels can look "rich" while being semantically empty.

## 4. Roadmap Overview

The project should proceed through gated phases. Each phase must define what would count as failure before the run.

### Phase A: Estimator Integrity

Goal: make `I_T^C(s)` numerically trustworthy in finite worlds.

Tasks:

- Replace naive capped enumeration with explicit sampling modes:
  - exact enumeration when feasible;
  - stratified trajectory sampling;
  - Monte Carlo trajectory sampling with confidence intervals;
  - capped enumeration marked as biased/truncated.
- Track truncation status per `(world, start, T)`.
- Report effective sample size and confidence intervals.
- Add repeatability checks across seeds.

Pass criteria:

- Exact and sampled estimates agree on small worlds within tolerance.
- Truncated runs are flagged and excluded from formal comparisons.
- Increasing sample budget changes estimates smoothly rather than erratically.

Failure criteria:

- `I_T^C` rankings reverse under modest sample-budget changes.
- Capped enumeration dominates the result.

### Phase B: Coarse-Graining Admissibility

Goal: distinguish meaningful abstractions from entropy-inflating labels.

Candidate admissibility tests:

- predictive sufficiency: macro-state predicts future viable macro-trajectory distributions;
- stability under perturbation: similar microstates map to similar macro-futures;
- compression with retained transport: fewer labels without destroying viable transition structure;
- intervention sensitivity: macro labels preserve differences that affect viability;
- null rejection: random labelings should fail at least one admissibility test.

Metrics:

- macro predictive loss;
- transition consistency;
- viable transport preservation;
- compression ratio;
- random/null percentile score.

Pass criteria:

- region and viability-signature coarse-grainings beat random coarse-grainings on admissibility even when random has higher raw entropy.

Failure criteria:

- random coarse-grainings remain competitive after admissibility scoring.

### Phase C: Controlled World Battery

Goal: test the invariant across many worlds whose structural features are independently labeled.

World families:

- open field;
- trap basin;
- resource corridor;
- reversible loop;
- bottleneck;
- rigid attractor;
- noisy/slipping dynamics;
- dead branch maze;
- mixed worlds with controlled feature ratios.

Experimental design:

- generate many worlds per family;
- vary energy budget, trap density, resource density, noise, and bottleneck width;
- evaluate multiple horizons;
- compare exact/sampled estimates;
- include random and adversarial coarse-grainings.

Primary questions:

- Does `I_T^C` track structured viable futures rather than survival?
- Does it penalize noise-only branching?
- Does it penalize irreversible traps?
- Does it reward recoverable/reversible structure?
- Does horizon extension reveal bottleneck compression?

### Phase D: Baseline Comparison

Goal: determine whether Omega's invariant is just a relabeling of known measures.

Baselines:

- raw trajectory count;
- viable trajectory count;
- reachable state count;
- reachable state entropy;
- survival fraction;
- controllability/reachability score;
- empowerment-like action influence score;
- viability kernel size;
- graph centrality and conductance metrics.

Pass criteria:

- `I_T^C` explains separations that at least some simpler baselines miss.
- The difference is stable across world families and horizons.

Failure criteria:

- a simpler baseline matches all diagnostic separations with less machinery.

### Phase E: Field Dynamics

Goal: test whether moving according to local changes in the invariant produces distinctive dynamics.

Candidate dynamics:

```text
s_{t+1} ~ P(s_t, a_t)
a_t selected by estimated positive change in I_T^C
```

Controls:

- random walk;
- survival-maximizing policy;
- shortest-path-to-resource policy;
- entropy-maximizing policy;
- myopic reachable-state maximizing policy.

Questions:

- Does gradient-following `I_T^C` avoid traps without collapsing into rigid attractors?
- Does it preserve recoverability better than survival maximization?
- Does it overvalue random/noisy areas?

Failure criteria:

- `I_T^C` dynamics behave indistinguishably from survival or reachable-entropy heuristics.

### Phase F: Multifield / Fiber Transport

Goal: return to the later Omega branch only after the single-object invariant is stable.

Objects:

- macro nodes from admissible coarse-grainings;
- fibers as viable micro-trajectories realizing macro nodes;
- certified transport as lower-rank viable structure preserved across macro transitions.

Core test:

```text
Do coupled dynamics produce certified transport components more often than topology-preserving nulls?
```

Controls:

- shuffled dynamics;
- rewired transition graphs preserving degree;
- randomized coarse-grainings;
- uncoupled agents;
- static topology-only controls.

## 5. Immediate Next Experiments

Experiment 1: exact-vs-sampled estimator check.

- small grids: 5x5, 7x7;
- horizons: 1-8;
- exact enumeration where possible;
- Monte Carlo estimates at increasing budgets;
- output estimator error curves.

Experiment 2: admissibility scoring for coarse-grainings.

- compare region, viability-signature, random, and adversarial coarse-grainings;
- report entropy and admissibility separately;
- explicitly penalize high-entropy random labels that do not preserve predictive structure.

Experiment 3: controlled family sweep.

- generate 100-1000 worlds per family;
- run at the calibrated 18-worker CPU profile;
- compute confidence intervals and effect sizes.

Experiment 4: baseline redundancy analysis.

- regress or classify diagnostic labels using all baseline metrics;
- test whether `I_T^C` contributes additional explanatory power.

## 6. Decision Gates

Gate 1: numerical trust.

- Do not interpret theory results until estimator bias is controlled.

Gate 2: admissible abstraction.

- Do not claim scale/coarse-graining support until random coarse-grainings are rejected by principled criteria.

Gate 3: baseline non-redundancy.

- Do not call Omega a distinct scientific object if simpler baselines match its discriminators.

Gate 4: dynamics.

- Do not claim field dynamics until invariant-guided dynamics beat or differ meaningfully from simple controls.

## 7. Working Standard For Evidence

Evidence should be reported as:

- hypothesis;
- operational definition;
- worlds/data;
- estimator;
- controls/nulls;
- result;
- failure modes;
- interpretation boundary.

Avoid:

- claims that the theory is validated;
- interpreting hand-designed toy worlds as external evidence;
- treating high entropy as inherently meaningful;
- treating survival as sufficient;
- treating random coarse-graining success as harmless.

## 8. Updated Roadmap Judgment

The roadmap does change after the probe.

Before the probe, the obvious next step was "more worlds." After the probe, the more important next step is estimator and abstraction discipline:

1. control enumeration/sampling bias;
2. define admissible coarse-graining;
3. only then scale world families and compare baselines.

The hardware is adequate. The limiting factor is now experimental design, not compute.


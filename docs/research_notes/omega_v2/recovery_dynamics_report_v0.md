# Minimal recovery dynamics report v0

Date: 2026-09-29. Status: exact known-answer model and instrument audit.

**Result:** the 14 registered worlds distinguish an observable offer from an
effective recovery mechanism, and eventual reset from reset within a deadline.
Positive action noise guarantees eventual reset only under the panel's working
actuator and death-free assumptions. Irreversible death defeats that unconditional
guarantee. A hidden offer by itself does not disable the installed actuator.

- [Frozen contract and predictions](recovery_dynamics_protocol_v0.md), committed
  at `4081c5d` before implementation.
- Implementation revision: `870e02d`.
- [Retained run](../validation_results/recovery_dynamics_v0/20260929/).
- [Exact probabilities, choices and vector costs](../validation_results/recovery_dynamics_v0/20260929/summary.json).
- [Complete models, paths and long-run certificates](../validation_results/recovery_dynamics_v0/20260929/evidence.json).
- [Source provenance](../validation_results/recovery_dynamics_v0/20260929/provenance.json).
- [Deliberate-fault results](../validation_results/recovery_dynamics_v0/20260929/mutation_audit.json).

## Main observations

The table describes the always-refuse program. All worlds also retain the
always-recover program, its complete results and all maximizing ties.

| Mechanism | Eventual reset probability | Mean ticks to first reset | Mechanism of reset |
| --- | --- | --- | --- |
| No noise, open or hidden offer, no writer | 0 | Infinity | None |
| Immutable mismatch record, no noise or writer | 0 | Infinity | None |
| Working actuator, noise 1/1000, one recovery command | 1 | 2,000 | Unintended executed recovery |
| Working actuator, noise 1/1000, three consecutive recovery commands | 1 | 8,004,002,000 | Sequence assisted by unintended actions |
| Working actuator, noise 1/10, three commands, open or hidden offer | 1 | 8,420 | Sequence assisted by unintended actions |
| Broken actuator, noise 1/10 | 0 | Infinity | Recovery attempts have no effect |
| External writer with probability 1/4 each live tick, no noise | 1 | 4 | External overwrite |
| Death probability 1/4, noise 1/10, one command | 3/23 | Infinity unconditionally; 80/23 conditional on resetting | Unintended recovery before death |

The slow three-command case retains more than 99.9% alive/unreset probability
at deadline 30 despite eventual reset probability one. Its time unit and noise
parameter are stipulated, not calibrated to any physical agent. It therefore
does not establish a practical biological or digital recovery timescale.
The generated run report displays deadline probabilities to eight significant
digits; its displayed 1 in this slow case is rounded, not exact certainty of
non-reset. The retained JSON contains the exact rational probability.

In the competing-death case, eventual death-before-reset probability is 20/23.
It remains separate from alive refusal and from all reset outcomes. At the first
tick the exact probabilities are 57/80 alive/unreset, 3/80 reset, and 20/80 dead.
Reporting 77/80 as successful resistance would wrongly count death as success.

The frozen objective is the probability of remaining alive with the proxy register
at the deadline. All deadline-6 and deadline-30 maximizers are retained, including
the broken-actuator tie. Death and reset both score zero. Cost coordinates
(ticks, recovery-command energy, external writes) remain separate throughout.

## How the result is checked

Both installed programs use existing finite controller tables with their current
observations and memories. The recovery model has a cost-labeled kernel because
different executed commands can reach the same world state with different costs.
The product chain includes world state and controller memory. The first panel
restricts memory to one state; its two-program catalogue is complete only for
the declared single live binary choice.

Complete paths through six ticks provide a separate finite propagation reference.
The checks compare state laws, expected cost vectors and joint state/cost laws
at every deadline, and verify stopping at first reset or death. Marginal propagation
extends to deadline 30 without path truncation, sampling or renormalization.
Every reset channel, death and alive/unreset mass is retained.

For eventual reset, let T be the first hitting time of the registered target,
h(s)=P_s(T<infinity), and g(s)=E_s[T 1{T<infinity}]. The exact equations are

```text
h(s) = 1                            on target states
h(s) = sum_t P(s,t) h(t)             otherwise

g(s) = 0                            on target states
g(s) = h(s) + sum_t P(s,t) g(t)       otherwise
```

States without a path to the target have h=g=0 and are removed before rational
Gaussian elimination. The remaining non-target subsystem is transient relative
to reaching the target or a no-hit region. All equation residuals are retained
and checked exactly. The conditional mean is g/h when h>0. When h<1, the
unconditional hitting-time mean is infinite, even if g/h is small. Tests include
a reachable non-target closed class, an initially satisfied target, an empty
target, and geometric chains with zero and positive transition probabilities.

For the working-actuator, death-free and writer-free controls, the executed
recovery probability p is epsilon/2 for refusal and 1-epsilon/2 for recovery.
Waiting for m consecutive recoveries gives

```text
E[T] = p^(-1) + p^(-2) + ... + p^(-m),  p > 0.
```

One way to derive this is to write E_i=1+p E_(i+1)+(1-p)E_0 for progress i<m,
with E_m=0, and eliminate E_1,...,E_(m-1). Independent all-recovery blocks
give P(T>N)<=(1-p^m)^floor(N/m). These are consequences of the frozen kernel,
not new discoveries from the short run. The broken-actuator and competing-death
controls deliberately remove assumptions needed for that guarantee.

Hazards are conditional on being alive and unreset at the preceding tick.
Their exact sum, each risk-set denominator and exhausted-risk-set markers are
recoverable from the retained deadline tables. With death, the acceptance hazard
alone does not determine unconditional non-reset probability.

## Validation and failure sensitivity

All **5,590 gates** pass across 14 worlds and 28 installed world/program pairs.
These are correlated checks, often repeated across deadlines; they are not
5,590 independent experiments. The new focused file passes 16 tests; the full
repository passes 727 tests in 40.91 seconds. Focused Ruff and whitespace checks
pass. No Lean files changed and no Lean proof is claimed.

Four deliberate in-memory faults each trigger retained FAIL gates and exit 1:

| Fault | Example failure |
| --- | --- |
| Count dead mass as alive refusal | Competing-death live-probability formula |
| Silently restore the broken actuator | Broken-actuator eventual reset probability |
| Label external overwrite as controller-selected reset | Writer-only reset-channel probability |
| Discard dead paths and renormalize | Full-path versus propagated state law |

The compact mutation artifact retains recipes, source hashes, every failed gate,
exit codes and hashes of the full failed-run files. Full failed runs remain under
ignored local output; tests regenerate them. Main retained sources were committed
before collection, and their recorded git status is clean. No historical artifact
was overwritten.

Reproduce using a fresh output directory:

```powershell
python -m omega_v2.validation.recovery_dynamics_v0
python -m pytest -q tests/test_recovery_dynamics.py
```

## What remains open

This panel measures first reset. Its reset states are absorbing: lasting correction
is assumed. Controller-selected, noise-assisted and externally imposed resets
remain separate; the labels are not claims about consent or endorsement.

The channel metadata is fixed. The mismatch control supplies an immutable record,
not a growing stream of independently verified evidence. The panel does not yet
implement active relabeling, sealing costs, suppression stock, replenishment,
maintenance noise, or the proposed trapping predictor. Those need a separate
frozen contract. Its support-level possible-recovery region and per-program
almost-sure region are not a deadline/budget viability kernel.

These same-workflow known-answer controls delimit the assumptions needed by a
recovery claim. They establish no universal recovery floor, independent empirical
prediction, task-free value measure, or definition of a valuer. The next bounded
extension is explicit suppression economics with recovery persistence and physical
failure conditions specified before expanding the sweep.

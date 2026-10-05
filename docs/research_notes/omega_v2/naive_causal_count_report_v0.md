# Naive causal count v0: thermal and fueled continuation

2026-10-05. Exploratory run requested by the user. No required winner, noise
filter, value label, new physical rule or fitted coefficient.

The naive counts show genuine horizon- and preparation-dependent crossovers.
They do not establish that generative branching dimensionality beats thermal
continuation. A dilute thermal system already has extensive dependency cones;
binding and fuel can either increase early counts or reduce later counts by
slowing movement. Stronger-binding comparisons favor a dispersed fueled
preparation in many cells, but their equilibrium baseline is often assembled.

## What was counted

Every native event becomes a node. Incoming edges record the last physical
events that wrote arguments read by the current rule: position, conformation,
bond presence/absence, occupancy and shared fuel. This is **rule provenance**,
not a proof that each parent is necessary under a counterfactual intervention.
Initial facts are retained by the simulation as boundary conditions, not
invented events. Identically zero coefficients remove the corresponding rate
dependency, while physical guards remain.

For each realized history and each horizon:

- `N`: every event, including fluctuations and dead ends.
- `C = N + R`: sum of future-cone sizes, where `R` is the number of ordered
  ancestor-descendant pairs. A source is included in its own cone. Reconvergent
  descendants count once within a cone; overlaps between different sources
  are counted repeatedly.
- Mean/max cone size, forks, mergers, depth and maximum depth-layer breadth.
- All nonempty directed dependency paths after transitive reduction, including
  singleton paths. Their exact integer counts are archived. Both
  `mean(log2(max(1, routes)))` and `log2(mean(routes))` are reported. The first
  convention retains zero-event histories rather than conditioning them away.

The main graph includes fuel. A second diagnostic projection omits only fuel
register edges. Both use the **same histories and physical probabilities**.
It is not a second simulation or a claim that those dependencies are unreal.

Counts are exact for these declared finite graphs; their averages estimate
native expectations by Monte Carlo. **This is not exhaustive enumeration of
the alternative multiway future.** Graph layer breadth is not physical or
fractal dimension, and a directed dependency path is not an Everett branch.
Clock/race counterfactuals and blocked alternatives are not reconstructed by
last-writer provenance.

## Scope and computation

Replayed all 7,776 archived corridor histories, then simulated 1,728 new dilute
histories under unchanged reversible lattice chemistry. Total: **9,504
histories and 2,507,339 events**, of which 1,050,919 are newly simulated.
Replay, dilute preparation and new simulation/counting took **30.32 seconds
with ten worker processes**. Analysis and implementation time are additional.

The existing panel has 16 particles on sides 8/7/6, bond strengths 1/2/3 and
catalytic barriers 0/1/2. The dilute panel has side 12 and strengths 0/1/2,
with the same barriers. Cuts are 0/1/5/10/20. Each cell has 96 existing or 64
new histories, grouped into four independent preparation chains. The three
preparations are equilibrium, the same equilibrium configurations refueled,
and dispersed unbound fueled configurations. Each has the same matter and
rules at its parameter coordinate; equilibrium and fueled preparations do
**not** match available free energy. The two fueled preparations share fuel
but generally differ in configuration and ensemble free energy.

New equilibrium samples use 4,000 preparation sweeps, then 16 samples per
chain at 128-sweep spacing. Basic split-Rhat across reported observables is
0.949–1.014; these are approximate MCMC draws, not certified exact equilibrium
samples. Preparation sweeps never count as physical events. Mean initial
largest components are 2.44, 3.14 and 5.77 of 16 particles at strengths 0/1/2;
mean bonds are 2.45, 4.03 and 7.92. Thus the first two dilute cases are the
closest gas-like controls here, not a bond-free ideal gas.

## 1. A transient excess over the dilute thermal count

Side 12, zero bond energy, catalytic barrier zero. Zero bond energy does not
remove the reversible bond variable or its constraint on collective motion.

| Horizon | Thermal events | Dispersed fueled events | Thermal cone sum C | Dispersed fueled C | C ratio |
|---:|---:|---:|---:|---:|---:|
| 1 | 43.58 | 52.78 | 125.03 | 161.67 | 1.293 |
| 5 | 219.22 | 217.42 | 3,514.64 | 3,559.13 | 1.013 |
| 10 | 439.34 | 380.00 | 21,160.69 | 16,750.73 | 0.792 |
| 20 | 860.61 | 685.22 | 135,845.75 | 92,222.42 | 0.679 |

The early difference in C is +36.64 with estimated chain SE 2.04; the final
difference is −43,623 with SE 3,986. Four-chain errors are descriptive, not a
multiple-comparison validation. The near tie at horizon 5 should not be
treated as a precise crossover location.

This excess exists without catalysis. It is an excess of the declared counts,
not yet identified generativity. The dispersed preparation starts unbound
and mobile, with extra fuel and a different conformation distribution. Fuel
promotes bonds, and bonded components move collectively with a rate decreasing
with component size. At T=20, 821 of the thermal preparation's 861 events are
motions, versus 629 of 685 for the dispersed fueled preparation. Mean largest
component is 2.59 versus 3.81. These observations support a mobility/assembly
trade-off, not a decomposition proving its separate causal contributions.

The thermal graph is not a collection of inconsequential isolated events:
motion writes positions and vacancy records that later motions and reactions
read. Its mean event cone contains about 156 events. Thermal fluctuations
have not been deleted or assigned zero extent.

## 2. Stronger-binding contrasts can remain above equilibrium

Selected T=20 means; all comparisons use dispersed fueled versus equilibrium.
The last column omits fuel-register edges on both sides.

| Side / binding / barrier | Event ratio | Cone-sum ratio | Cone-sum ratio without fuel edges |
|---|---:|---:|---:|
| 12 / 0 / 0 | 0.796 | 0.679 | 0.581 |
| 12 / 1 / 0 | 0.866 | 0.823 | 0.712 |
| 12 / 2 / 0 | 1.183 | 1.531 | 1.324 |
| 8 / 2 / 2 | 1.347 | 1.868 | 1.640 |
| 6 / 2 / 2 | 1.599 | 3.051 | 2.736 |
| 6 / 3 / 2 | 3.993 | 13.379 | 12.142 |

The strongest contrast is against a nearly system-spanning equilibrium
assembly, not dilute gas. At side 6, binding 3, barrier 2, equilibrium's mean
largest component at T=20 is 15.68 particles. The dispersed fueled preparation
has a mean 14.44 at that cut but retains its earlier mobile development in the
accumulated counts. Later assembly does not erase that history.

Across the original 27 parameter cells at T=20, dispersed fueled has higher
mean C in 21 and higher event count in 19. Without fuel edges, the C count
advantage remains in 18. In the dilute panel it has higher C in 3/9 cells,
all at binding 2; the weak-binding thermal controls win the other six.
These cell totals describe this grid; they are not a probability over
physical regimes or an ethical vote.

## 3. Refueling an existing assembly is a different experiment

Refueled equilibrium has higher mean C at T=1 in 26/27 original cells, but
lower mean C at T=20 in all 27. It also loses at T=20 in all nine dilute cells.
For side 6, binding 2, barrier 2:

| Horizon | Equilibrium C | Refueled-equilibrium C |
|---:|---:|---:|
| 1 | 10.86 | 19.22 |
| 20 | 3,364.30 | 2,361.29 |

This is a cleaner configuration-matched fuel intervention than the dispersed
comparison, though it deliberately changes available free energy. More fuel
and early reaction ancestry do not force a lasting advantage in these counts.

Increasing catalysis from barrier 0 to 2, with preparation and energy law
fixed, gives mixed count changes. In original refueled cells at T=20, C rises
in 7/9 sample means, by roughly 6–23%, and falls in two. Many differences are
small relative to their four-chain errors. In dispersed preparations there
is no broad clear T=20 catalytic lift beyond those errors. No claim that
catalysis must monotonically increase this count is supported.

## 4. Branching adds information, but also a counting problem

Cone count can favor a history family without a higher event count. In the
original panel at T=20, two such dispersed-versus-equilibrium mean comparisons
occur (side 7 or 6, binding 1, barrier 0). Both cease to favor dispersed in C
when fuel-register edges are omitted. They do not establish an independent
local-composition advantage; the shared resource is part of their explanation.

Route counting is more sensitive still. At side 6, binding 2, barrier 2,
refueled equilibrium has mean log2 routes 13.52 versus 13.23, despite fewer
events and smaller cones. But log2 **mean raw routes** is 14.59 versus 15.36,
reversing the mean ranking. The mean-log difference is also smaller than its
estimated SE. Removing fuel edges removes its positive mean-log difference.
Thus this example is not a demonstrated branching victory. Retaining native
weights requires reporting exactly which statistic is averaged.

There is a simple analytical limitation: n independent event nodes have
C=n; a dependency chain of n nodes has C=n(n+1)/2. The chain also has that
many directed subpaths. This counts accumulated dependency, not independent
dimensions. Repeated forks and reconvergences can create many paths without
creating equally many independent future outcomes. No “branching dimension”
has been inferred from these counts.

## What this advances

The naive count was worth running. It exposes real transient and persistent
regions of excess relative to a matched-law thermal preparation, while
allowing thermal motion and its consequences to win. It also locates why a
positive result cannot automatically be credited to generativity: mobility,
fuel-mediated ancestry, equilibrium aggregation and route multiplicity all
matter.

Keep this profile as the first causal-count baseline. The next measurement
should add the **lawful alternatives at residual cuts**, preserving rates,
timing and joint constraints, so the same instrument sees continuation left
available as well as activity that occurred. Do this on a small common
physical subsystem before another broad chemistry sweep. Changing the count
to guarantee that gas loses would defeat this experiment's purpose.

## Reproduction and evidence

- [Protocol](naive_causal_count_protocol_v0.md).
The runner generates a local `naive_causal_count_v0/` directory containing the
manifest and source hashes, group means and chain errors, all 576 contrasts,
the complete T=20 comparison table, per-history graph archives and new physical
trajectories. These generated outputs are kept out of Git. The code, protocol
and this report provide the published reproduction path.

Run `python -m omega_v2.validation.naive_causal_count_v0 --workers 10` in a
fresh output directory (`--out`); existing results are protected from overwrite.
Then run `python -m omega_v2.validation.naive_causal_count_analysis_v0` for
the default output. Five focused tests passed for reconvergent DAG counts,
independent events, shared fuel, zero-coefficient dependencies, released sites
and newly produced catalytic templates. Every archived physical replay matched
its recorded final state.

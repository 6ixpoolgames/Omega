# VAL0-CT: Constructor Task Algebra Probe

Single-field proto-Omega validation under Constructor Theory

## Purpose

VAL0-CT defines the first post-CA validation design in Constructor-Theory-native task algebra language.

The goal is modest:

> Test for proto-Omega signatures in constructor-style task space.

VAL0-CT does not validate Omega. It does not test full valuerhood, multifield compatibility, lineage, ethics, or civilization-scale structure. It tests the earliest operational precursor:

> reachable task-space that remains future-bearing across horizons.

In compressed form:

```text
Constructor Theory:
  possible / impossible task space

VAL0-CT:
  single-field proto-Omega probe

Omega overlay:
  reachability refined by future reachability preservation
```

The primary question is:

> In generated constructor-style task algebras, does persistence-conditioned reachability predict long-horizon reachability retention better than raw reachability and matched controls?

This treats Omega as a refinement of reachability, not a separate substrate metric. Differentiation from raw reachability is hoped for in sufficiently structured algebras, but collapse to reachability in low-resolution algebras is diagnostic rather than fatal.

## Boundary and stance

Constructor Theory provides the native language:

```text
substrates
attributes
tasks
constructors
possible / impossible transformations
task composition
task repertoires
```

Omega provides the overlay:

```text
reachability refinement
persistence-conditioned reachability
recoverable reachability
propagating structured branching
pseudo-Omega / lock-in detection
```

The boundary is:

> Constructor Theory gives the possible-task space. Omega begins as a filter over which reachable task structures preserve future reachability through time.

VAL0-CT is therefore a single-field, constructor-theoretic proto-Omega probe.

It asks whether task-space futures can remain future-bearing, not whether they are ethically good or fully Omega-compatible.

## Why not start with toy agents?

VAL0 deliberately avoids beginning with a toy agent world containing hand-labeled variables such as:

```text
health
energy
resources
repair actions
reproduction actions
reward functions
gridworld survival
```

That route is tempting but risks several errors:

```text
hand-labeling Omega properties
overfitting to substrate variables
confusing action names with task roles
smuggling validation targets into the environment
```

Instead, VAL0 begins one level higher: generated task algebras.

The task-algebra approach tests the structure Omega should care about before committing to a particular embodied substrate.

Later probes can instantiate successful task algebra patterns in embodied worlds.

## Minimal constructor-style task algebra

For VAL0, use the smallest task-algebra object that still captures distinction, relation, and asymmetry.

A minimal algebra is:

```text
A = (X, T, K, ⊢, ⊥, cost, reliability)
```

Where:

```text
X:
  attributes / task-relevant distinctions

T:
  tasks / transformations between attributes

K:
  approximate constructors

⊢:
  enabling relation: tasks open future tasks

⊥:
  obstruction / incompatibility relation: tasks close future tasks

cost:
  resource or complexity cost of performing tasks

reliability:
  probability or robustness of task success
```

This is intentionally lean.

Deferred unless needed:

```text
explicit substrates Σ
parallel composition ⊗
lineage / successor constructors
epistemic correction
multi-constructor corridors
full embodied environment dynamics
```

Sequential composition is implicit in task paths. A task can enable or obstruct future tasks, so executing a task updates the available task structure.

Honesty note:

> VAL0-CT is not a full physical Constructor Theory derivation. It is a finite operational model of Constructor-Theory-style possibility structure.

## Possible, available, and impossible

VAL0 must distinguish possible, available, and impossible.

```text
possible:
  not forbidden by algebraic invariants or obstruction relations

available:
  reachable from the current repertoire under horizon, cost, reliability,
  and constructor constraints

impossible:
  forbidden by obstruction or invariant, not merely expensive or currently inaccessible
```

This distinction matters because Omega is a refinement of reachability. A task that is unavailable now is not necessarily impossible. A task that is possible in the algebra may still be unavailable from the current state.

## Approximate constructors

Use approximate constructors rather than ideal constructors.

Definition:

```text
K is an ε-constructor for task τ over horizon h iff:
  K performs τ with reliability ≥ 1 - ε
  and retains capacity to perform τ again within horizon/cost bounds
```

This is closer to real valuers and real systems, which are bounded, degrading, probabilistic, and repair-dependent.

Constructor capacity may change over time as tasks are performed, enabled, obstructed, or degraded.

## Distinction, relation, and asymmetry in task algebra

VAL0 should remain grounded in the primitive triad.

```text
distinction:
  attributes and tasks differ

relation:
  tasks enable, obstruct, and compose into future task-space

asymmetry:
  different task choices induce different future repertoires
```

Asymmetry is the engine of the simulation.

Given a task algebra state `A_t`, two available tasks may produce different future algebras:

```text
τ_a(A_t) -> A_{t+1}^a
τ_b(A_t) -> A_{t+1}^b
```

and:

```text
R0(A_{t+1}^a, H) ≠ R0(A_{t+1}^b, H)
```

or:

```text
R1(A_{t+1}^a, h, H) ≠ R1(A_{t+1}^b, h, H)
```

Task-space asymmetry can be measured as consequence dispersion over candidate tasks:

```text
Avail(A_t) = {τ_1, τ_2, ..., τ_n}
F(τ_i) = future-repertoire features after applying τ_i

asymmetry(A_t) = dispersion({F(τ_i)})
```

Low asymmetry means most choices lead to similar future task-space. High asymmetry means some choices preserve or expand future task-space while others close, collapse, or lock it.

Agency becomes meaningful only when constructors select among asymmetric task options.

## Task repertoire

Define:

```text
R(K, A, h, C)
```

The available task repertoire for constructor `K` in algebra `A` over horizon `h` under constraints `C`.

Possible repertoire measurements:

```text
task count
reachable task nodes
task diversity
composition closure size
minimal cost
reliability
obstruction exposure
```

The validation object is not a grid trajectory. It is repertoire evolution:

```text
R_t -> R_{t+1}
```

At each step, constructors choose tasks, tasks update the algebra, and the repertoire is recomputed.

## Proto-Omega target

VAL0 scans for proto-Omega signatures, not Omega.

Definition:

> Proto-Omega is task-space structure where reachable possibility remains future-bearing across time.

VAL0 signature:

```text
reachable task-space
that preserves future reachability
across horizon sweep
without collapsing into terminal lock-in or noise
```

Non-claims:

```text
not full Omega
not moral value
not complete valuerhood
not multifield compatibility
not lineage / civilization-scale validation
```

Proto-Omega is the temporal connective tissue between Alpha and Omega:

```text
Alpha:
  initial possible task structure

Proto-Omega:
  structures that preserve future reachability through time

Omega:
  asymptotic compatibility of value-bearing possibility
```

## R-level operationalization

### R0: raw reachability

Raw reachability asks:

> Where can the task algebra get?

Definition:

```text
R0(A, h):
  tasks reachable from current algebra state within horizon h
```

Operationally:

```text
start from currently available tasks
apply enabling and obstruction rules up to depth h
count or characterize reachable task nodes / attributes / constructor capacities
```

R0 is both a baseline and the base substrate of Omega. Omega is not separate from reachability; it is a refinement of reachability.

### R1: persistence-conditioned reachability

R1 asks:

> Where can the task algebra get that still leaves futures open?

Definition:

```text
R1(A, h, H):
  reachable tasks within h whose resulting algebra states retain
  nontrivial reachability over continuation horizon H
```

Detection:

```text
for each reachable task/path τ within h:
  apply τ -> A'
  compute R0(A', H)
  τ is R1-positive if R0(A', H) remains above threshold
```

R1 is the primary proto-Omega signal in VAL0.

It is not the Omega metric. It is a minimal Omega-derived refinement of reachability.

Because R1 can be confounded with lookahead, all R1 comparisons must use matched planning budgets against R0-lookahead baselines.

### R2: perturbation-recoverable reachability

R2 is a sidecar, not the primary VAL0 target.

Definition:

```text
R2(A, h, H, P):
  R1-positive states that retain reachability after perturbation p ∈ P
```

Detection:

```text
apply τ -> A'
apply perturbation p -> p(A')
compute R0 or R1 from p(A')
```

R2 tests whether future-bearing reachability survives shocks.

### R3: propagating structured reachability

R3 is an exploratory lushness sidecar.

Definition:

```text
R3:
  branching that continues enabling further structured branching
```

Detection ideas:

```text
branch survival across depth
non-convergence of branches
non-noise downstream task structure
composition persistence
```

R3 is where lushness enters VAL0, but only lightly.

### R4: composition-compatible reachability

R4 asks whether reachable branches remain compatible under sequential or parallel composition.

This is probably deferred unless cheap to implement.

```text
R4:
  reachable task branches that remain compatible under composition
```

R4 becomes more central in multifield probes.

## Lushness, propagation, and noise

Lushness is not identical to Omega.

Definition:

> Lushness is structured branching that propagates.

Related terms:

```text
propagation:
  branch structure carries forward by enabling further structured branching

noise:
  branching without stable causal/compositional carry-forward

sterile branching:
  distinguishable immediate branches that terminate, converge, or fail to enable
  further meaningful branching
```

Omega filters lushness for recoverable value-bearing compatibility. VAL0 only probes the earliest task-space precursor: whether reachability propagates rather than collapsing immediately.

## Horizon sweep and resolution diagnostics

VAL0 should not fix one horizon.

Proto-Omega is temporal connective tissue. It must be evaluated by how reachability propagates across horizons.

Sweep:

```text
h:
  near-term reach horizon

H:
  continuation horizon used by R1

T:
  held-out long-horizon outcome window
```

Example grid:

```text
h ∈ {1, 2, 4, 8}
H ∈ {4, 8, 16, 32}
T ∈ {16, 32, 64}
```

Interpretation:

```text
R1 ≈ R0:
  possibly low-resolution algebra; not automatic failure

R1 predicts T better than R0:
  evidence that future-preserving reachability is distinguishable

R0 beats R1:
  possible R1 misspecification or outcome is only raw reachability
```

Low-resolution cases should be classified, not discarded:

```text
low obstruction
low asymmetry
shallow horizon
dense graph where everything remains reachable
sparse graph where nothing remains reachable
```

## Constructor policies

VAL0 is a policy tournament in constructor task-space.

Constructors choose among available tasks according to policies. They are not necessarily intelligent agents. Agency enters only as task selection under asymmetric consequences.

Policy classes:

```text
random:
  choose available tasks randomly or cost-weighted

persistence:
  preserve constructor's current task capacity

R0 / raw reachability maximizer:
  maximize near-horizon raw reachability

R0-lookahead:
  same planning horizon and compute budget as R1,
  but optimizes raw future reachability

empowerment-like:
  maximize constructor-controlled task diversity

R1 / persistence-conditioned reachability:
  maximize reachability that leaves future reachability open

pseudo-Omega / lock-in:
  maximize local or self reachability while obstructing broader future reachability
```

R1 must not receive more planning budget than the baselines.

If R1 wins, the interpretation should be:

> Given equal horizon and compute budget, preserving future reachability outperformed maximizing raw reachable task count.

not:

> R1 won because it looked farther ahead.

## Baselines

Constructor-Theory-native baselines:

```text
constructor persistence:
  does K retain defining task capacity?

raw reachability:
  R0 task count / reachable nodes

R0-lookahead:
  same planning budget as R1, optimized for raw future reachability

repertoire size:
  size of R(K, A, h, C)

composition closure size:
  number of tasks reachable under composition closure

empowerment-like task influence:
  diversity / channel capacity of tasks K can cause

local viability:
  preservation of K's own local repertoire
```

Differentiating from reachability is hoped for, but not required in every low-resolution algebra because Omega is a refinement/subset of reachability.

## Simulation loop

For each generated task algebra `A0`:

```text
for each horizon pair (h, H):
  compute R0(A0, h)
  compute R1(A0, h, H)

for each constructor policy π:
  set A = A0

  for t in 1..T:
    for each constructor K:
      Avail_K = available tasks for K
      choose τ ~ π(Avail_K, A)

    apply chosen tasks
    update enabled / obstructed task sets
    update costs and reliabilities if applicable
    apply optional perturbation
    record R0, R1, asymmetry, obstruction, lock-in indicators

  compute long-horizon reachability retention
```

Tasks can enable or obstruct future tasks. This is what makes the dynamics asymmetric and temporally meaningful.

## Primary outcome

Keep the outcome simple.

Primary outcome:

```text
long_horizon_reachability_retention
```

One possible form:

```text
LHR(A_0, A_T, h) = R0(A_T, h) / R0(A_0, h)
```

Binary alternative:

```text
persistent = R0(A_T, h) > threshold
```

Report both local and global forms where possible:

```text
local LHR:
  reachability retained for constructor K

global LHR:
  reachability retained in the whole algebra / field
```

VAL0 should care primarily about global retention, but local/global divergence is informative for pseudo-Omega diagnostics.

Avoid defining the primary outcome as an Omega score.

## Pseudo-Omega / lock-in detection

Pseudo-Omega is a locally self-propagating task family that preserves or expands itself while degrading broader proto-Omega / Omega-relevant task structure.

VAL0 detector:

```text
local reachability or constructor persistence rises
while global R1, R2, R3, or long-horizon reachability retention falls
```

Examples:

```text
terminal attractor
lock-in family
proxy task family
self-amplifying obstruction family
```

For VAL0, pseudo-Omega is mainly a negative diagnostic: it tests whether raw reachability or local persistence can be misleading.

## Generated task algebras

Generate multiple families, not one hand-built graph.

Ingredients:

```text
constructors K_i
attributes X_j
tasks T_k
enabling relations
obstruction relations
cost / reliability labels
perturbation operators
lock-in / terminal structures
noise-branching structures
structured-branching structures
```

Generation knobs:

```text
task graph density
enabling density
obstruction density
constructor specialization
cost tightness
reliability noise
enabling asymmetry
obstruction asymmetry
lock-in seed strength
branching propagation depth
perturbation rate
```

The generator must include asymmetric consequences. If the task graph is too flat, every policy will look similar and R1 will collapse to R0.

VAL0 should include families with and without enough structure for R1 to differentiate from R0.

## Controls and nulls

Controls:

```text
degree-matched random task graphs
rewired enabling edges
shuffled obstruction relations
cost/reliability shuffles
task-label permutations
terminal-attractor controls
noise-branching controls
low-resolution algebras where R1 should collapse to R0
```

Purpose:

> Test whether R1 signal is real temporal structure rather than graph density, task count, arbitrary labels, or planning-budget advantage.

## Validation hypotheses

Primary hypothesis:

> Persistence-conditioned reachability, R1, predicts long-horizon reachability retention across structured task algebras better than raw reachability and matched controls.

Nuanced interpretation:

```text
If R1 collapses to R0:
  diagnostic of low resolution, not automatic failure

If R1 differentiates and predicts better:
  proto-Omega signal

If R1 does not predict held-out persistence in structured algebras:
  R1 is misspecified or insufficient
```

Secondary hypotheses:

```text
R2 predicts shock recovery better than R0/R1
R3 distinguishes propagating lushness from noise branching
pseudo-Omega seeds show high local reachability but low global LHR
horizon sweep reveals bands where proto-Omega signal is detectable
```

## Success, failure, and ambiguity

### Success

```text
R1 predicts long-horizon reachability retention better than R0 in structured algebras
R1 does not spuriously outperform in low-resolution controls
pseudo-Omega cases show high local reachability but weak global LHR
horizon sweep reveals interpretable temporal bands
```

### Failure

```text
R1 adds no predictive value in structured algebras
R1 only tracks degree / task count / planning budget
R1 is unstable across generator families
pseudo-Omega cases are not distinguishable from proto-Omega cases
```

### Ambiguity

```text
R1 works only in hand-designed algebras
R1 collapses to R0 broadly
R2/R3 sidecars outperform R1 but are harder to interpret
```

## Relation to single-Omega and multifield Omega

VAL0-CT is single-field proto-Omega validation under Constructor Theory.

Single-field version:

```text
one task algebra
one field of reachability
one constructor-space ecology
one notion of future-bearing task preservation
```

Question:

```text
does this field preserve future reachability?
```

Multifield Omega begins later, when multiple task fields interact:

```text
A_1, A_2, ..., A_n
```

with cross-field enabling, obstruction, dependence, and composition.

The key transition is:

```text
single-field R1:
  reachable tasks in one field that preserve future reachability in that field

joint-R1:
  coupled task paths that preserve future reachability across multiple fields
```

A later multifield metric:

```text
compatibility gap:
  sum of individual R1_i - joint_R1
```

A large compatibility gap means fields look viable separately but cannot remain viable together.

## Roadmap beyond VAL0

```text
VAL0-CT:
  single-field proto-Omega
  R1 predicts long-horizon reachability retention

VAL1-CT:
  coupled fields
  joint reachability and compatibility gap

VAL2-CT:
  local/global divergence
  pseudo-Omega task families

VAL3-CT:
  corridors
  mutually future-bearing task pathways

VAL4-CT:
  scale composition
  higher-order fields vs component fields

VAL5-CT:
  lineage / successor fields
  propagation across generations
```

VAL0 intentionally defers:

```text
lineage continuity / successor constructors
full epistemic correction
multi-constructor mutual corridors
embodied substrate instantiation
full valuerhood
civilization/ecology-scale field viability
```

Reason:

> VAL0 only tests whether proto-Omega reachability structure exists in task algebras.

## Open problems by ownership

### Constructor-Theory-native

```text
approximate constructors
possible vs available vs impossible
task composition and closure
constructor composition
task algebra generation
```

### Omega-overlay

```text
proto-Omega signature definition
R1/R2/R3 operational validity
pseudo-Omega detection
Omega-compatible lushness beyond VAL0
```

### Interface

```text
avoiding smuggled labels
matching planning budgets
connecting task algebras to embodied worlds
choosing horizon sweeps
determining when R1≈R0 means low resolution versus misspecification
```

## Implementation sketch

Possible data structure:

```text
directed typed task graph / hypergraph
constructors as task-capacity nodes
tasks as transformations between attributes
enabling edges
obstruction edges
cost/reliability labels
perturbation operators
```

Simulation loop:

```text
generate algebra family
compute R0/R1 across horizon sweep
run policy tournament to T
measure long-horizon reachability retention
compare R1 policy against R0-lookahead and controls
run R2/R3 sidecars
report resolution diagnostics
```

R1 can be expensive because it requires simulating candidate tasks and recomputing future reachability. VAL0 should allow bounded horizons and sampled estimation:

```text
R1_sampled:
  evaluate a sampled subset of available task paths
  estimate future reachability retention
```

All policies compared against R1 should use matched planning and sampling budgets.

## Final thesis

VAL0-CT tests for proto-Omega as temporally persistent reachability in constructor-style task algebras.

If Omega is the asymptotic compatibility structure of value-bearing possibility, then its first detectable precursor should be reachable task-space that remains future-bearing across horizons.

VAL0 asks whether persistence-conditioned reachability detects that precursor better than raw reachability in sufficiently structured algebras, while treating collapse to reachability in low-resolution algebras as diagnostic rather than fatal.

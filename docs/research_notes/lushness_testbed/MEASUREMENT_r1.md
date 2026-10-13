# Shared measurement contract r1

Status: initial design, 2026-10-13. Defines a versioned readout; not a claim that
one finite grain is the universal physical resolution. Applies with
[initial spec](INITIAL_SPEC_r1.md).

## 1. Canonical dynamics

For a fixed implemented controller, let x include the full declared sufficient
state. Aggregate elementary rates into Q(x,y) for x != y; the diagonal is minus
the exit rate. Physical channels may remain available as separate metadata or
physical event marks when justified. Representation duplicates are aggregated.
Declared physical events leaving x unchanged require an event process in addition
to Q if a readout counts them. Solver null events are never physical marks.

Engine reaction IDs, molecule IDs and integer prefactors do not establish physical
distinctions. A rate 2*k may be two distinguishable outcomes or two matches with
one resolved outcome. Audit the mapping; do not automatically add log2(2) entropy.

Both engines must implement the same rates including volume/combinatorial factors.
Q is a generator, not a normalized row probability and not a list of species.

"Physical randomness" means stochastic variation represented in the modeled
world, including controller decisions. It does not mean quantum-certified or
microscopically simulated randomness. A software pseudorandom draw can sample a
physical model law. Conversely, a random solver seed or shuffled numerical index
does not add a physical alternative. Fixed-seed reproducibility of the calculation
does not turn the stipulated stochastic world into a deterministic world.

Decision entropy is included through the declared joint physical history. For a
resolved decision A and subsequent state Y, H(A,Y|x) = H(A|x) + H(Y|A,x).
If A is omitted from the readout, H(Y|x) = H(A,Y|x) - H(A|Y,x). Thus an automatic
extra H(A|x) can double count or count information omitted from the declared grain.
Transient decision records missed between sample times are a resolution loss,
not grounds to declare their underlying randomness unreal. No persistence/value
test is imposed on their admission at a grain that resolves them.

## 2. Primary finite-resolution history breadth

For observation cadence delta, obtain P_delta = exp(delta Q). This is the CTMC
transition law, not I + delta Q. Computational uniformization may evaluate it, but
the artificial Poisson/null-event history is excluded from the objective.

For a known initial state x0 and T = n*delta:

    g_delta(x) = - sum_y P_delta(x,y) log2 P_delta(x,y)
    ell_n(x0) = sum_(j=0..n-1) [P_delta^j g_delta](x0)
    L_n(x0) = 2^ell_n(x0).

Store ell in bits, avoiding overflow. This counts complete sequences of observed
configurations, not only endpoints. Developments that reconverge after a sampled
distinction remain distinct from the original root. Developments that occur
entirely between samples may be missed: this is a declared limitation, not a
justification for calling it a complete microscopic history measure.

Use full Markov states for this identity. A projected observation process usually
has memory; do not reuse the identity on an arbitrary lumped matrix. Exact lumping
must preserve both future law and the declared measurement, or implement the
appropriate hidden-state calculation.

Primary cadence and sensitivity cadences are frozen together. A smaller numerical
solver step is a convergence check. A different measurement cadence is a different
readout whose rankings can legitimately differ. No universal delta -> 0 entropy
limit is assumed. Absolute values across grains are not interchangeable.

## 3. Secondary readouts

| Readout | Definition/scope | Status |
|---|---|---|
| Finer physical configuration history | Same law with justified sites/records resolved | Small calibration where explicit lift exists |
| Embedded jump chain | r(x,y)=Q(x,y)/q(x) over state-changing exits | Conditional outcome breadth per jump; separate activity |
| Timing | Exit rates, waiting distributions, counts per physical horizon | Primary timing diagnostics |
| Marked event history | Law over physically declared event marks/times | Requires separate likelihood/grain contract |
| Persistence/Rule A | Retained distinctions under an explicit memory/readout test | Optional, not defined or selected by this draft |

Fixed-jump and fixed-time horizons are different queries. Continuous waiting-time
entropy is differential, unit-dependent; do not add it to discrete jump entropy
and call the result a canonical number of futures. If timing is binned, specify
the bin rule and a joint outcome/timing law, including multiple jumps per bin.

Source attribution (chemistry, physical controller noise, stochastic costs,
arbitration) uses an explicit joint history/event model or named ablation. Marginal
source entropies need not add to total entropy. Any chain-rule allocation states
its order and interaction terms. Report resource bills and cost randomness even
when an exact additive entropy attribution is unavailable.

## 4. Numerical methods and reporting

Small cases: enumerate reachable states, calculate P_delta with error control,
and calculate breadth by recursion. Check stochastic row sums, nonnegativity,
semigroup composition and agreement with a second tiny reference. Record numerical
tolerances; floating-point propagation is not symbolic exact arithmetic.

Sampled check when P_delta rows are evaluable: average
    -sum_j log2 P_delta(X_j,X_(j+1))
over independent trajectories. Report Monte Carlo uncertainty and numerical row
error separately. Event-path density from a Gillespie trace is a different
quantity and cannot substitute for these transition probabilities. If scalable
state-transition entropy estimation is unresolved, label that mode unsupported;
do not silently use reaction-label frequencies or unique-trajectory counts.

One-hot initial states carry zero preparation entropy. For a preparation prior,
report mean conditional breadth-in-bits E_x[ell_n(x)] separately from entropy of
the unconditioned mixture. They are different queries.

For rate/offset results, inspect closed classes and stationarity, and retain
Poisson/propagation residuals. A finite-horizon lead is not a long-run result.
No-solution, resource cap and unsupported readout are statuses, not zero scores.

## 5. Invariance and sensitivity suite

Expected invariances: passive renaming; reaction file order; bookkeeping channel
split with unchanged aggregated rates and outcomes; artificial identity
checkpoints; consistent unit conversion; proven readout-preserving quotient.

State splitting is invariant only with an explicit representation-equivalence
map and unchanged physical readout. Splitting into actual distinguishable states
can add breadth. Do not demand invariance under that physical modification.

Expected sensitivities to examine: temporal cadence; physical spatial/event grain;
controller observation and horizon; physical lifetime; noise/cost mechanism;
inventory. Preserve every ranking flip and classify its cause. A flip is a robust-
interpretation warning, not automatically a failed implementation.

Any diagnostic counterfactual has a new query/model identifier. It must not
overwrite the primary objective or quietly introduce a persistence threshold.

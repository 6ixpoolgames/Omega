# Sol weighted trajectory-covering proposal: assessment

2026-10-05. A mathematically legitimate candidate for exploration. Not an
adopted lushness invariant, ethical bridge or new chemistry result.

## Candidate and established mathematical setting

Use the native, frame-conditioned law P_T on complete resolved histories, with
physical timing and resource accounting. For a stated frame/resolution F_r,

    d_abs(g,h) = integral_0^T 1[F_r(g(t)) != F_r(h(t))] dt,
    d_frac = d_abs/T,
    N(epsilon,alpha) = smallest number of epsilon balls whose union
                       has P_T probability at least alpha.

This does avoid the one-time occupation identity. Native joint path laws and
the geometry of whole histories enter the formula. The probability of the
union counts its probability mass once, including higher intersections.

For a specified finite trajectory alphabet and admissible centers, this is
equivalently a fixed-length lossy description problem with excess-distortion
probability at most 1-alpha: choose a codebook of representative histories;
covered histories have a representative within epsilon. Optimization here is
over descriptive centers, not physical policies or probability weights.

Sources: [Kostina and Verdu, Fixed-length lossy compression in the finite
blocklength regime](https://arxiv.org/abs/1102.3944);
[Vershik, Dynamics of metrics in measure spaces and their asymptotic
invariants](https://arxiv.org/abs/0912.2123). The latter supplies neighboring
averaged-metric entropy mathematics, not a theorem about this chemistry.

## Small exact check: temporal information survives

Consider a stationary fair symmetric two-state CTMC with flip rate lambda.
Observe it at times 0, 1/3, 2/3, 1. Its sixteen possible observed histories
have exact probabilities from transition flip probability

    u = (1-exp(-2*lambda/3))/2.

Use four-coordinate Hamming distance divided by four. Enumerate all sixteen
possible centers and all 65,536 codebooks; evaluate each union's probability
under the full four-time joint law. This was calculated directly during the
assessment, without Monte Carlo or changing the chemistry.

| lambda | N at epsilon=0, alpha=.90 | N at epsilon=.25, alpha=.90 | N at epsilon=.25, alpha=.99 |
|---:|---:|---:|---:|
| .05 | 2 | 2 | 3 |
| 1 | 11 | 3 | 4 |
| 10 | 15 | 4 | 4 |

Every one-time marginal is .5/.5 in every case. The covering profile therefore
distinguishes some temporal laws that occupancy cannot. These are exact
combinatorial minima up to ordinary floating-point probability evaluation for
this four-sample restriction, NOT exact continuous-time covering numbers.

For the continuous-time fractional mismatch distance between two independent
draws, the mean is .5 at all lambda. The distribution nevertheless changes:

    Var(d_frac) = 1/(8*lambda*T)
                  - (1-exp(-4*lambda*T))/(32*lambda^2*T^2).

Thus even a mean pairwise-distance shortcut would miss this example. At T=1
the variance is .234134413, .094322364, .0121875 for the three rates above.

## Main scientific limitation: the specified distance

Whole-state equality gives the same instantaneous distance to a one-bit
difference and a difference across an entire apparatus. It retains when
histories agree, but does not itself measure physical magnitude, locality or
residual consequence of their disagreements. Any bijection of state symbols
preserves this distance, even when it does not preserve the adapter's physical
relations. A richer family of physically specified frames may recover some
of what a whole-state profile misses; it should not be replaced by an
arbitrary weighted sum of preferred features.

A single probability-one history has N=1, whether it describes a static
configuration or a complicated deterministic construction. This is a boundary
case revealing what the extent measures, not a proof that every stochastic or
all-frame application must fail. Rapid independent thermal fluctuations can
increase covering extent and can dominate whole-state mismatch. Noise must
remain; no noise-deletion repair or required thermal loser follows.

Conversely, a process that makes a useful continuation highly reliable can
concentrate the path law and reduce covering numbers. Faster reversible
switching can increase them. Neither sign alone proves increased/decreased
access, recovery or lushness. Test these separately rather than calling any
particular direction an axiom.

Joint interactions constrain the native path law, which is an advantage. A
covering profile is still a compression of that law and geometry, not a
complete invariant of all causal couplings or physically allowed compositions.

## Continuous-time support is not automatically finitely coverable

Finite state space does not bound the number of jumps. A two-state CTMC with
positive flip rate has support containing binary histories oscillating on
successively finer dyadic intervals. Distinct such histories disagree for
T/2, even though each has finitely many jumps. Hence for epsilon<T/4 in
absolute distance (epsilon<1/4 fractionally), no finite ball cover can contain
the whole support. Full-mass closed-ball covers would also have to contain
the support, so N(epsilon,1) is infinite in this example.

For alpha<1 a finite cover can be obtained: bound the jump count with a stated
tail probability, then discretize the jump times of the retained strata. Keep
the excluded probability in the original denominator. This is an approximation
at a declared coordinate, not declaring rare/noisy paths physically irrelevant.

The full support need not have the finite box dimension suggested by the
proposal. Even when covering asymptotics exist, N(epsilon) is not itself a
countably additive measure; existence of a dimension does not imply existence
of a finite nonzero Minkowski content. Treat asymptotics as later hypotheses.

## Timing, records and finite implementation choices

- Fractional and absolute distances are scale conversions at fixed T:
  N_frac(epsilon,alpha,T)=N_abs(T*epsilon,alpha,T). They are not independent
  diagnostics. Prefer absolute physical-duration tolerance for checking that
  a fixed early divergence remains distinguishable after a common suffix;
  retain the fractional view if desired. The full horizon profile preserves
  early differences even when a normalized long-horizon summary dilutes them.
- Shared suffixes reduce pairwise distance, but covering extent does not
  automatically decompose additively into separate prefixes plus one shared
  suffix. Probability of a union and additivity of structural extent differ.
- The distance on full paths can be a pseudometric under frame projection or
  differences only at isolated instants. Endpoint records or physically
  distinct reaction marks may need explicit representation. An unmarked state
  trajectory does not identify reaction channels with identical state updates.
  The current chemistry distinguishes native fuel and catalytic channels in
  event records; merely naming otherwise identical channels adds no physics.
- A common consistent relabeling is harmless. Optimizing a separate relabeling
  at each time could erase physical motion, routing and history, and is not
  authorized.
- Centers must be specified: all physical paths, all histories of a finite
  resolved alphabet, or only sampled histories are different optimization
  problems. A sample-based greedy cover is an estimate/bound, not an exact
  minimum for the original continuous-time law.

## Recommended disposition

Proceed with this as a trajectory-covering extent hypothesis, keeping the
name distinct from an established lushness measure. The next finite probe
should include Sol's temporal-persistence, kinetic and reconvergence cases,
plus a decoupled thermal fluctuation, a deterministic/reliable construction,
and a changed downstream coupling under matched activity where feasible.
Use one stated resolution and full native probabilities, with no required
winner. Report where the metric explains a tie or ordering. Do not enlarge the
chemistry or tune a distance to rescue a preferred result first.

Part 2 of Sol's proposal overstates what has been achieved: harm, repair,
generativity and ecology are not yet derived from covering extent. The useful
advance is a concrete metric-measure extent that can fail, and a direct link
to established mathematics. The next burden is empirical/mathematical
discrimination on this fixed candidate, not a uniqueness theorem.

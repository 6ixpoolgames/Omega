# Weighted trajectory-covering probe v0

2026-10-05. User authorized "Run it" following the Sol path-covering assessment.
This records the definition and scope before the numerical run, without a
required winner or a permission gate for subsequent exploratory revisions.

## Definition

Use actual native history probabilities and whole-state equality in each
declared physical frame. Distance is integrated mismatch in physical time;
fractional distance divides it by the horizon. Cover a fraction alpha of the
original law by a union of balls about admissible physical histories. Do not
renormalize away failures, rare events or thermal fluctuations. No added
feature weights, reaction bonuses, probability priors or chemistry changes.

## Exact finite-resolution panel

CTMC observations at 0,T/4,T/2,3T/4, each held for T/4 for this finite
resolution's distance. This is exact for the projected four-observation law,
not an exact full jump-time integral or a bound on the continuum profile.
Native transition matrices are exp(Q*T/4). All positive-probability histories
and all their centers are enumerated. Closed balls; fractional tolerances
0,.25,.5; probability depths .5,.9,.99,1; horizons .5,1,4.

Cases:
- Stationary symmetric binary switching at .05,1,10: identical one-time laws,
  different persistence. Initial law fair.
- Fixed-zero symmetric binary switching at .1,1,10: unchanged support,
  accelerated reversible access. Report first-hitting probability separately.
- Fixed fair source plus a decoupled, initially zero binary register, flip
  rates 0,.1,10. Same two-register carrier; source, auxiliary and whole frames.
- Matched-activity coupling pair: source S is static and fair; error E starts
  zero and switches 0->1 at .1 and 1->0 at 1. In the coupled apparatus D=S xor E;
  in the disconnected apparatus D=E. Both have the same pathwise clock/rate
  law in (S,E), but only one destination depends on S. Inspect frames S,D,SD,
  retaining physical register roles. No output-label permutation establishes
  causal equivalence of these two physical wirings.
- Finite-support complete timed paths: two equiprobable histories disagree
  on [.25,.75) and then share a suffix, at horizons1,2,4; absolute tolerances
  .2,.4,.6 plus fractional .25. A scheduled three-stage construction succeeds
  with probability .5,.9,.99,1; failure has its original probability. Compare
  deterministic idle only as a diagnostic, not as a matched thermodynamic
  preparation. These are mathematical controls, not new chemical mechanisms.

## Continuous-time sampling check

For stationary and fixed-zero binary processes at rates .05,1,10, T=1,
generate64 native training histories and2048 independent evaluation histories
per case. Compute exact integrated mismatch between supplied paths. Centers
are restricted to training histories. Fit alpha=.9 at absolute epsilon=.25
and .5. Solve the finite empirical cover with a bounded MILP, reporting both
objective bounds if not certified optimal. Evaluate selected centers on the
independent sample and report Wilson95% intervals for covered mass. These
intervals concern a fixed fitted cover, not the unknown global optimum.

This stage estimates a continuous-law cover's performance; it does not certify
the population covering number. Save seeds, all paths, probabilities, centers,
generator matrices and distance data needed to reproduce results. A finite
empirical alpha=1 is not used as a surrogate for full CTMC support.

## Interpretation

The three initial controls test temporal sensitivity, kinetic sensitivity and
retention of finite prefixes. The added cases challenge noise sensitivity,
probability concentration and physical coupling. No directional ranking is
stipulated as lushness. Equal volumes need not imply equal objects. Gas remains
consequential; a binary thermal register is not the full lattice-gas comparison.
Covering numbers are finite-resolution extents, not additive measures. No
fractal dimension or quantum branch-counting result is sought here.

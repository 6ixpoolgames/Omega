# Continuous trajectory-covering center check

Supplement to path_covering_report_v0.md. The metric and native laws are unchanged.
The first run optimized centers drawn from64 training histories. This check
uses three specified admissible centers and fresh samples; no center selection
is based on the evaluation samples.

At T=1 and absolute epsilon=.5, constant-zero and constant-one histories cover
every binary history: their distances to a path sum to one. They are admissible
under every positive-rate stationary binary process. Thus true N is at most two,
even where a particular fitted two-center empirical cover generalizes poorly.

One admissible path switches once at .5. Its covering probability is exactly
(.5)*(1+exp(-lambda)). Complement symmetry makes distances symmetric about .5.
The only positive atom at .5 is the no-jump mass exp(-lambda); jump-time densities
make the remaining distance law nonatomic. Any balanced finite-jump center has
this same mass, and unbalanced centers have mass .5. Thus this is also maximal
single-center mass among finite-jump centers, and gives the exact N below.

| Rate | Balanced-center exact mass | Fresh observed mass (95% interval) | Exact N at alpha .90 |
|---:|---:|---|---:|
| 0.05 | 0.975615 | 0.975342 (0.970129–0.979664) | 1 |
| 1 | 0.683940 | 0.673340 (0.658821–0.687534) | 2 |
| 10 | 0.500023 | 0.497803 (0.482500–0.513110) | 2 |

The slow-process empirical optimum was two because random sampling missed
a center that approximates both constant histories. Its true optimum here is
one. That is a center-approximation error, not a change to the physical field.
At tolerance .25 the initial fast-process undercoverage remains unresolved;
none of its fitted counts is promoted to a population covering number.

The exact half-horizon result is a calibration of the estimator, not a new
lushness ordering. Probability-depth and distance-scale coordinates matter.

Reproduce: `python -m omega_v2.validation.path_covering_center_check_v0`.
All fresh paths and the center definitions are in path_covering_v0/center_check/.

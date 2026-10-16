# FHP-I density, size and re-rooting probe v0

2026-10-07. Registered before executing the follow-up. No required winner.

Retain the existing FHP-I collision-then-stream law and complete-future
effective breadth. Report log2 L = expected cumulative stochastic pair
collisions, avoiding exponent overflow and biased averages of exponentiated
trajectory estimates. No new physics, persistence replacement or time-averaged root.

Panels: periodic sides 6 and 12, densities 0.5 and 1 particle/site. Within each
panel match N, zero vector momentum, kinetic energy, lattice and rule. Across
sizes N grows with area; per-particle rates are supplementary comparisons.
Horizons 1, 4, 16, 32, 64, 128 physical ticks.

Predeclared roots: opposite pairs on even/even sites at density 0.5 and on a
checkerboard at density 1 (pair orientation cycles with x+y); the inverse-streamed
version of that pattern; separated horizontal counterstreams in upper/lower
half rows, subsampled at even x for density 0.5. These are geometrical gas
preparations, not claimed constructors. Counterstreams provide a deterministic
zero-branching control under this law.

Thermal reference: independently sample uniform exclusion configurations of N
slots, reject nonzero total vector momentum. This samples the invariant uniform
fixed-(N,P) sector exactly, up to PRNG sampling. It is not asserted to be a
single ergodic component. Larger-component enumeration is out of scope, so
any advantage remains potentially influenced by unconditioned extra invariants.
Use 512 independent continuations per root and 512 independent thermal roots,
one continuation each. The latter estimates mean rooted log breadth, without
adding initial-ensemble entropy. Also estimate stationary mean instantaneous
collision count from the independent initial thermal sample.

Re-root at cuts 0,16,64. At each nonzero cut retain the first 16 simulated
presents (no outcome selection), and run 64 fresh continuations per present for
32 ticks. Each estimate conditions on that exact state. Report their mean and
range; uncertainty of the mean uses the 16 independent outer roots, not 1024
independent roots. At cut zero fixed preparations need only one root with512
continuations; thermal uses independently sampled exact roots. Aggregate means
describe sampled present populations, not a time-averaged physical state.

Report Monte Carlo standard errors and approximate 95% intervals on log breadth,
including comparisons against the independent thermal trajectories. These are
exploratory coordinate-wise intervals, not multiple-testing-adjusted declarations.
Record late-window branching rate (ticks64-128) and fresh residual breadth;
an accumulated lead alone does not establish a sustained growth-rate advantage.

Check vectorized updates against the existing exact tiny-state implementation,
conservation and the exact tiny-root expected collision count. Raw arrays stay
in ignored results/local_runs; publishable artifacts are source, tests and notes.
Reference search for reactive lattice gases is separate; do not modify this law.

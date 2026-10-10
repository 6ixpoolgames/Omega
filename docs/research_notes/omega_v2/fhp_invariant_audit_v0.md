# FHP-I alternating invariant audit

2026-10-07. Runner: `omega_v2/validation/fhp_invariant_audit_v0.py`.
Raw compact output is ignored under `results/local_runs/fhp_invariant_audit_v0/`.

## Finding

The even-torus FHP-I update has three exact additive quantities that alternate
sign each tick. They follow directly from the velocity parities and the stated
pair/triple collision table. With `n_d(x,y)` the occupancy of channel `d`, and
velocity order as in `lattice_gas.py`, one convenient basis is

```
Qy  = sum_xy (-1)^y   [ n1+n2-n4-n5 ]
Qx  = sum_xy (-1)^x   [ n0-n2-n3+n5 ]
Qxy = sum_xy (-1)^(x+y) [ n0+n1-n3-n4 ]
```

Each satisfies `Q(X[t+1]) = -Q(X[t])` for every allowed realization of the
collision choices. Therefore its magnitude and zero/nonzero status are exact
sector labels across time. A uniform fixed-(N,P) ensemble includes many such
labels; it is stationary as a mixture, but it is not the sector-conditioned
reference for a preparation with fixed values of these quantities.

The pair-grid and aimed-grid preparations have `Qx=Qy=Qxy=0` in all four tested
side/density panels. Sampled uniform fixed-(N,P=0) thermal references generally
do not. Across 128 samples per panel, the mean Euclidean norm of the three
orthonormalized alternating coordinates was 0.44 and 0.64 at side6 densities
.5 and1, and 0.44 and 0.61 at side12. The minimum was numerically zero in the
side6, density.5 sample; all other minima were positive. These are coordinates
normalized by the global slot-space Euclidean metric, so the magnitudes are
panel-specific and should not be compared across sizes as thermodynamic
quantities.

The local linear-constraint solve finds three time-independent additive
invariants, corresponding to particle number and the two momentum components,
and three `-1` modes on both even sides6 and12 (floating-point rank tolerance
`1e-10`). The explicit formulas above are exact and span those `-1` modes.
All 576 sampled one-tick
updates (including both preparations and thermal samples over both sizes and
densities) preserved the three fixed invariants and flipped each alternating
quantity exactly. The local linear equations cover every
single-particle stream and every pair/triple collision outcome; sampling is a
separate implementation check.

## Implication for the scaling result

This is a concrete invariant-sector mismatch. The large pair-grid versus
uniform-sector excess, and the smaller fresh-root excess, may arise in part
from comparing different alternating-invariant sectors. The result does not
show that these three labels explain the measured branching-rate excess: a
sector-conditioned thermal comparison is still needed, and nonlinear or
nonadditive invariants may remain. Nor does it imply the pair-grid is
uninteresting; it identifies its physical sector more precisely.

The next clean audit is to sample uniformly at fixed `(N,P,Qx,Qy,Qxy)` matching
the pair-grid labels, then repeat the same native continuation-rate and fresh
projection measurements. This would separate a preparation effect within its
sector from the difference caused by mixing sectors in the reference.

No parent files, FHP rules, or scaling outputs were changed. No exhaustive
state graph, full invariant classification, or generativity claim is made.

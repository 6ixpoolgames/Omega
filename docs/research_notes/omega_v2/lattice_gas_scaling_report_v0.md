# FHP-I breadth: density, size and fresh-present projections

2026-10-07. Exploratory follow-up under the unchanged published FHP-I rule.
Protocol: [lattice_gas_scaling_protocol_v0.md](lattice_gas_scaling_protocol_v0.md).
Runner: `omega_v2/validation/lattice_gas_scaling_v0.py`.

## Result

Both predeclared pair preparations exceeded the uniform fixed-(N,P) thermal
reference in cumulative log breadth and in late-window branching rate in all
four panels. Fresh projections from sampled states at cut64 retained an
advantage too. This is stronger than a retained early-history lead, but it is
not an own-component comparison or a demonstrated self-maintaining constructor.

The readout remains exactly

    log2 L_x(n) = E_x[sum_{t=0}^{n-1} number_of_pair_collision_sites(X_t)].

Thus the experiment measures weighted future branching under this gas rule.
Nothing in it separately measures useful construction or realized value.
Complete sequences are the candidate's bearer; reconvergence does not erase
their earlier differences relative to the original root.

## Design and computation

Sides6/12, densities0.5/1 particle per site, 512 independent continuations per
fixed preparation. Reference:512 independent uniform fixed-N exclusion samples
conditioned on zero momentum, one continuation each. No entropy of initial
uncertainty was added. All particles have equal kinetic energy, so matching N
also matches kinetic energy. No reactions, external drive or energy tax added.

Native time horizon128, supplementary horizons1,4,16,32,64. Re-root at16/64:
16 exact states sampled without selection from each ensemble, 64 new32-tick
continuations per state. Means across roots are reported, not a time-averaged
state. Uncertainty of those means uses independent outer-root clusters.

The run took9.0 seconds locally using vectorized numpy, without worker spawning
or materializing a future tree. Two smaller agents handled sampler/testing and
reference lookup. Raw arrays and numerical summaries are ignored under
`results/local_runs/lattice_gas_scaling_v0`; only compact notes and source belong
in version control. Seed20261007. No commit or push performed this turn.

## Cumulative extent and continuing production

Values below are bits (log2 L), not raw L. The thermal column is the mean of
rooted log breadth, equivalent to log2 of its geometric-mean L. It is not log2
of the arithmetic-mean L. Differences of hundreds of bits should not be read
as equivalent ratios of value.

| Side | Density | N | Thermal bits at128 | Pair grid bits at128 | Excess, approximate95% CI | Aimed grid bits at128 |
|---|---:|---:|---:|---:|---:|---:|
| 6 | .5 | 18 | 77.07 | 336.63 | 259.55 [255.74,263.37] | 335.72 |
| 6 | 1 | 36 | 197.13 | 447.75 | 250.62 [244.69,256.55] | 447.33 |
| 12 | .5 | 72 | 275.37 | 614.56 | 339.19 [333.70,344.68] | 609.66 |
| 12 | 1 | 144 | 749.33 | 943.84 | 194.51 [189.77,199.25] | 927.82 |

Counterstreams had zero branching at every horizon. Their horizontal rows never
meet: deterministic transport is an analytic zero-entropy control, not evidence
that all persistent organization lacks branching.

| Side | Density | Thermal bits/tick, ticks64-128 | Pair grid bits/tick | Pair/reference rate ratio |
|---|---:|---:|---:|---:|
| 6 | .5 | .6023 +/- .0288 | 2.5718 +/- .0144 | 4.27 |
| 6 | 1 | 1.5444 +/- .0327 | 3.1705 +/- .0498 | 2.05 |
| 12 | .5 | 2.1536 +/- .0324 | 4.1920 +/- .0422 | 1.95 |
| 12 | 1 | 5.8502 +/- .0337 | 6.3102 +/- .0377 | 1.08 |

Plus/minus values are approximate95% Monte Carlo half-widths. Aimed-grid rates
are2.5740,3.2427,4.2322,6.3065 respectively. Coordinate-wise intervals are not
adjusted for multiple comparisons; no universal asymptotic ranking follows.

Larger size weakens the relative rate advantage at each tested density.
At density1, the pair-grid advantage falls from roughly105% to8%. We have two
sizes, not a finite-size scaling law. Finite-torus recurrences and unresolved
invariants can still explain persistence of a rate difference.

## Fresh roots:32 ticks of future breadth

The following projections start anew at the sampled present. Earlier bits are
not included. Values are ensemble means of conditional log2 L from exact roots.

| Side | Density | Pair at cut0 | Pair at cut16 | Pair at cut64 | Thermal at cut64 |
|---|---:|---:|---:|---:|---:|
| 6 | .5 | 89.19 | 83.07 | 83.91 +/-1.02 | 19.09 +/-4.15 |
| 6 | 1 | 133.74 | 115.77 | 105.97 +/-6.16 | 48.11 +/-6.00 |
| 12 | .5 | 199.75 | 154.89 | 141.99 +/-6.15 | 75.91 +/-5.47 |
| 12 | 1 | 328.66 | 222.89 | 199.45 +/-4.73 | 189.73 +/-5.00 |

The final panel's fresh excess is about9.72bits (combined approximate95%
interval2.83 to16.60), much smaller than its original-root accumulated excess.
Its continuation advantage is decaying; a large accumulated difference alone
would obscure that fact. The run does not determine whether the remaining
advantage eventually vanishes or reflects a different invariant component.

## Checks and limitations

The sampler agrees with the existing collision table and streaming orientation;
local collision outcomes, conservation and bitstate conversion are checked.
An exact8-tick side3 root has6 expected pair-collision bits;8192 sampled paths
return6 exactly (a phase-regular check, not an independent uncertainty test).
An additional nonconstant-count exact-law comparison is in the sampler tests.
The reference sampler and clustered re-root statistics received a focused
independent code review. All15 targeted tests passed; focused Ruff checks passed.

Uniform fixed-(N,P) is invariant because collisions are doubly stochastic and
streaming permutes configurations. Extra invariants do not invalidate it, but
they prevent calling it the unique equilibrium reached from each preparation.
No component enumeration was attempted at these larger sizes. Both grid
preparations are highly ordered and may select atypical invariant sectors.

This establishes finite-horizon super-reference branching for these preparations
at larger N, including residual branching from later roots. It does not establish
that construction beats thermal behavior within the same full invariant sector,
that the advantage persists indefinitely, or that the candidate identifies value.
It also does not justify replacing the user's complete-future measure with an
endpoint or persistence measure.

## Recommended next move

Keep this gas adapter as a calibration. Before calling its sustained rate excess
generativity, audit conserved sublattice/line quantities or use a published
collision-rule extension that removes the relevant spurious invariants, then
repeat with that change explicitly declared. Longer runs alone cannot remove
an invariant-sector mismatch.

For constructive dynamics, use a separate published reactive lattice-gas
adapter with declared stoichiometry and resource/energy handling. The reference
review in `reactive_lattice_gas_options_2026-10-07.md` separates that route from
a deterministic reversible aggregation model. Do not silently add stochastic
branching to the latter merely to make this readout nonzero.

# Residual sharing, local fuel and mobility: results v0

2026-10-05. Exploratory implementation and crossed probe authorized together.

**Main finding:** fuel locality changes timed continuation while preserving the
matched equilibrium law. Faster transport converges to the previous shared-pool
model. The catalytic two-binding advantage survives the slow-transport case
tested here. Mobility changes physical trajectories without changing equilibrium.
These are results about this adapter; no lushness extent has been selected.

## Scope and implementation

Run `run_20261005T083647Z`: 23.09 seconds, up to ten workers.
Two shared generators (768 states each), eight local generators (2,560 each),
and 16 mobile laws with 3,072 trajectories / 467,127 physical events.
The exact panel has no motion (full 2x2 occupancy). The mobile panel uses four
particles on a 4x4 lattice, four preparations, and 48 trajectories per cell.
The finite-sample uncertainties below are Monte Carlo standard errors, not a
phase-boundary or robust-corridor certificate.

The history atlas retains every event, timing, rule provenance, prefix density,
cut and incoming particle-rename map. Equal complete residual states reuse a
continuation table. Fuel allocation remains part of residual identity. All
enabled channels, including untaken ones, retain successor states and rates.
This is a lazy native residual table plus history records, not exhaustive
mobile multiway enumeration or a completed concurrency equivalence.

## Exact transport result

Maximum total-variation discrepancy from the shared-pool endpoint law, across
unbound, seeded, adjacent, opposite and equilibrium preparations and horizons
0.25, 1 and 4. All have the same projected initial law; local allocations start
conditionally mixed. This compares complete projected state laws, not bond means.

| Fuel transport | No catalysis | Catalytic barrier 2 |
|---|---:|---:|
| 0.05 | 0.08432827 | 0.22214240 |
| 1 | 0.02181533 | 0.12702655 |
| 20 | 0.00151720 | 0.01366717 |
| 400 | 0.00007798 | 0.00076234 |

The same equilibrium distribution does not imply the same continuation law.
Even at equilibrium the two-event history probabilities differ with transport,
although all one-time projected equilibrium laws agree. Conditional rate
averaging is exact at initialization; finite-rate local depletion then retains
memory in the projected process. The reported lumpability defect remains
nonzero at finite transport; fast convergence is an averaging limit.

Probability that the next two chemistry events both bind with fuel by time 1,
from exposed/unbound F=B=2. Reservoir hops may occur between them; all other
chemistry events compete normally. The suffix after success is unrestricted.

| Fuel model | No catalysis | Catalytic barrier 2 |
|---|---:|---:|
| Shared | 0.175875 | 0.362281 |
| 0.05 | 0.174092 | 0.325966 |
| 1 | 0.174681 | 0.337514 |
| 20 | 0.175740 | 0.359397 |
| 400 | 0.175868 | 0.362129 |

With no opening bond there is no opening template. The first binding can
create one and change the next residual law. This conditional construction
advantage survives the local-fuel extension in this case; it is not a result
that all structured arrangements dominate thermal continuation.

For the adjacent two-bond preparation, barrier 2 and slow transport 0.05, the
same timed probability is 0.429846 versus 0.613270 with shared fuel. Spatial
supply therefore matters materially even though total stock and equilibrium
are matched. These values use B=2, unlike the earlier B=4/F=2 witness.

## History and residual sharing

- Barrier 0: 153 marked prefix nodes through depth two share 70 complete residual states.
- Barrier 2: 161 marked prefix nodes through depth two share 70 complete residual states.
- Analytic two-switch control: seven prefix nodes share four residual states;
  two different two-event histories return to the root. Their timed cylinder
  probabilities sum to 1 - 1.2 exp(-0.2) at T=1, as required by the native clock.
- The sampled mobile records cache 13,613 residual states across laws.

These counts describe storage and retained distinctions. They are not a
definition of possibility volume. Independent orders remain in the archive;
no diamond-based removal of physical timing was introduced.

## Mobility and combined effects

For an unobstructed n-particle component, changing gamma=1 to gamma=0.5
multiplies its translation rate by sqrt(n). The energy law is unchanged.
The exact mobile three-particle check confirms common equilibrium. The
sampled four-particle panel then measures consequences including encounters,
assembly and depletion rather than presuming their direction.

Paired differences at T=10 for the seeded/fueled preparation: gamma=0.5 minus
gamma=1. Each pair uses the same initial physical configuration, with independent
dynamics seeds; SE is computed from the 48 paired outcome differences.

| Barrier | Fuel model | Move count difference +/- SE | Bond difference +/- SE |
|---|---|---:|---:|
| 0 | Shared | 10.250 +/- 3.234 | -0.042 +/- 0.193 |
| 0 | 0.1 | 8.229 +/- 3.213 | 0.125 +/- 0.192 |
| 0 | 1.0 | 7.104 +/- 3.453 | -0.062 +/- 0.185 |
| 0 | 10.0 | 6.208 +/- 2.793 | 0.083 +/- 0.188 |
| 2 | Shared | 2.833 +/- 3.085 | 0.125 +/- 0.208 |
| 2 | 0.1 | 5.854 +/- 3.017 | -0.021 +/- 0.182 |
| 2 | 1.0 | 2.958 +/- 3.343 | 0.021 +/- 0.177 |
| 2 | 10.0 | 13.062 +/- 3.544 | -0.125 +/- 0.210 |

The panel does not establish a uniform mobility benefit for assembly or
generativity. Endpoint bond differences are small relative to this sample's
uncertainty. Catalytic construction and local transport remain active under
both mobility laws; there is no manufactured required winner.

At transport 10, the four ideal reservoir molecules generate about 400 hops
over ten time units. Those events stay in the physical archive. Their count
cannot be read as an automatic 400-unit lushness gain. Comparisons to the
old model use a common chemistry projection while retaining full histories.

## Thermodynamics, sampling and reproducibility

- Maximum exact detailed-balance flux error: 1.78e-15.
- Equilibrium marginal error: 1.39e-17.
- Conditional-average generator error: 1.13e-13.
- Maximum propagated mass error: 3.09e-13.
- Total entropy production uses the system term via KL decrease; equilibrium
  values vanish to numerical precision. It is a consistency diagnostic.
- Equilibrium sampler split R-hat: {'bonds': 1.0076531728592768, 'exposed': 1.0238394022006279, 'largest': 1.0098483874109407, 'log_weight': 1.0092131507105178}.
  This uses the retained chain diagnostic trace, including its recorded burn-in
  segment, and is not a convergence certificate. Only 48 baseline states were
  retained; uncertainty from residual chain correlation is not fully captured
  by the simple trajectory SE. The exact full-occupancy results do not depend
  on this sampler. The mobile equilibrium control may contain assemblies.
- Generated files at analysis: approximately 17.35 MiB, local/ignored.

Run:

```powershell
.venv/Scripts/python.exe -m omega_v2.validation.lattice_refinement_v0 --workers 10
.venv/Scripts/python.exe -m omega_v2.validation.lattice_refinement_analysis_v0 --run run_20261005T083647Z
```

All initial states, timed events, provenance, residual channels, exact
generators and laws, manifests and paired contrasts remain in the ignored run
directory. Source and written reports are the publication artifacts.

## What this changes next

The model now exposes spatial resource memory and mobility without losing its
thermodynamic reference or earlier histories. The useful next extent attempt
can operate on retained joint residual laws and compare shared versus local
resource coupling. It should preserve the demonstrated kinetic differences
without treating reservoir hopping, residual cache count or path density as
the answer by definition. No broader chemistry sweep is needed merely to
establish that these refinements are executable.

[Protocol](lattice_refinement_protocol_v0.md) ·
[Rationale and assessment](sol_modelling_refinement_assessment_2026-10-05.md)

# Boundary scan and next compounding substrate

The user asked whether the losing boundary is informative and whether established
models permit compounding catalytic capacity. This is an exploratory follow-up,
not a pre-registered phase-transition test.

## Boundary scan performed

Same105-state model, chemistry, matched roots and breadth definition. Fix k=1,
scan31 logarithmically spaced diffusion values d=.1 to100 at six dt values.
Primary contrast: ready-minus-separated fresh4-unit log2 breadth at cut4,
subtracting the corresponding contrast with k=0. This is the incremental
placement advantage associated with allowing autocatalysis, not the raw benefit
of switching catalysis on at a fixed root.

| dt | Positive-to-negative bracket in d |
|---:|---|
| .0125 | 7.94 to10.00 |
| .025 | 6.31 to7.94 |
| .05 | 6.31 to7.94 |
| .1 | 6.31 to7.94 |
| .2 | 19.95 to25.12 |
| 1 | No sign change in .1 to100 |

At d=10, incremental advantages are -.02015,-.02757,-.01871,-.00488,+.00131,
and+.00194bits in the above dt order. These are small relative to slow-diffusion
advantages. The negative sign survives several finer observation intervals,
so it is not confined to one coarse observation. The moving boundary prevents
calling this a unique physical collapse threshold. No continuous-time entropy
limit or convergence of threshold as dt->0 has been established.

This is useful sensitivity data: the claim "catalysis stops winning at diffusion
d" needs a specified readout resolution and contrast. It does not show catalytic
chemistry ceased occurring or ceased compounding at those parameters. Nor is high
diffusion a global worst case; it is one stress on local placement advantage.
Additional broad sweeps of this four-molecule patch have diminishing value.

Runner: `omega_v2/validation/reactive_boundary_v0.py`; raw summary ignored under
`results/local_runs/reactive_boundary_v0`. Run took about2seconds. No physics
or metric changed; numerical matrices reused the checked finite model. Lint
passed after an iteration-style fix. No push.

## Established routes for compounding

Farmer, Kauffman and Packard, *Autocatalytic replication of polymers* (1986),
[primary paper](https://oms-inet.files.svdcdn.com/production/files/autocatalyticreplication.pdf).
Their polymers undergo reversible joining/cleavage; products can catalyze other
reactions. Catalytic capabilities are assigned model chemistry, including random
assignments, not a folding-derived molecular theory. The original simulation
uses concentration dynamics, supplied food and outflow, and omits uncatalyzed
reactions. A stochastic implementation with explicit resource handling would
therefore be an adaptation, not a verbatim reproduction.

This is the stronger next candidate for constructive generativity: newly formed
species can change which transformations proceed rapidly. Keep one fixed
chemistry per comparison, and sample chemistry assignments independently of
measured breadth, rather than choosing networks for a winning result. Any claim
that the effect generalizes needs more than one network realization.

For a simpler spatial replication control, Wu and Higgs, *The origin of life is
a spatially localized stochastic transition* (2012),
[primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC3541068/), specifies local
catalytic replication with diffusion and crowding. Vacancies stand for resources;
that is not explicit closed energetic accounting. Useful for expanding catalytic
populations, less direct for new catalytic functions than the polymer chemistry.

The current Schlogl law already permits more X to create more catalytic pairs.
Our selected four-molecule preparations did not grow net X over the reported
intervals, and the fixed three-species repertoire cannot create new reaction
functions. That makes the current patch a mechanism calibration, not an adequate
test of broad constructive generativity. The recommended next work is a small
stochastic polymer-chemistry specification with resource/reversibility assumptions
declared before running, leaving the same breadth candidate unchanged.

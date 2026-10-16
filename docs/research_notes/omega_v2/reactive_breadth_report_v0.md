# First reactive breadth probe: local autocatalytic enabling

2026-10-07. Exact 105-state calculation, not a fitted reward model.
See [protocol](reactive_breadth_protocol_v0.md) for choices fixed before execution.

## What was and was not designed

We selected the published Schlogl mechanism A <-> X, B+2X <->3X
([Boon et al., eq173](https://arxiv.org/pdf/comp-gas/9512001)). We implemented it
using standard stochastic mass-action reaction and neighbor diffusion in a
closed two-voxel RDME. This is an explicitly adapted model, not replication of
the paper's exclusion lattice-gas rules or its reservoir-driven simulations.
The two voxels are one local spatial edge, not a developed2D chemistry.

Autocatalysis is specified in the chemical law. It was not discovered emerging
from a simpler particle theory. The measured consequence of that law is tested.
No reward, optimizer, catalyst bonus or favorable term was added to the breadth
formula. The generator evolves without knowing the readout. Event counts are
separate observables. Code terminology was changed from Markov "rewards" to
"observables" after the user correctly asked whether rewards were being designed.

This is a minimal replication/enabling mechanism. It does not implement general
construction, new reaction capabilities, repair, ecology or a value criterion.

## Physics and references

Four molecules, species A/X/B, equal standard chemical potentials, unit voxel
volume, symmetric diffusion. Forward and reverse rates satisfy detailed balance
with pi proportional to product1/n_i!, conditioned on the active component
total(A+X)>=2. There is no chemical inflow; the isothermal solvent/heat bath is
implicit. This is not an isolated microscopic energy model. Spatial mass action
assumes local mixing; no continuum-refinement claim or realistic elementary
three-body chemistry is made. Standard RDME setting:
[Hellander, hierarchical RDME algorithm](https://pmc.ncbi.nlm.nih.gov/articles/PMC6964990/).

For every k>0,d>0 tested, the active component is irreducible. At k=0 it splits
into3 components: the autocatalytic ablation is a changed law, not another
preparation under the same law. The stationary mixture still exists there.

Matched preparations, species order A,X,B:

* ready: (0,2,1)|(1,0,0): B starts beside the X pair;
* separated: (1,2,0)|(0,0,1): A starts beside the X pair, B is next door.

Both have global A1/X2/B1, site particle occupancies3+1, and pi=1/96. Thus the
point-root preparation free energy -kBT log pi is equal in this model. Physical
preparation protocol costs are not separately modeled. Other references are
the stationary reacting ideal mixture and random placements of the same A1/X2/B1
composition. Neither is the earlier FHP fluid gas. The stationary reference has
a different distribution of species totals from the exact prepared roots.

## Measurement

K_dt=exp(dt Q). The unchanged effective-breadth hypothesis on the sampled complete
state sequence is log2 L=H(X_dt,...,X_T|X_0=x). Resolutions dt=.05,.2,1,
horizons T=1,4,16, diffusion d=.1,1,10, autocatalytic rate k=0,.1,1,10.
The full CTMC law is retained; this readout does not resolve intermediate events
between observations. No entropy of continuous event times, random scheduler
labels, or initial ensemble uncertainty is silently added.

Fresh projection at4 for the next4 units means E_x[ell_(X4)(4)], an exact average
over separately rooted future scores. It is not a time-averaged root or the
entropy of the mixed present. Expected total activity and forward/reverse
reaction counts use the exact integrated CTMC law, independently of dt.

## Results

At k=1, the ready-minus-separated differences in log2 breadth are:

| Diffusion d | dt | Total through16 | Fresh at4, next4 | Increase in fresh placement advantage vs k=0 |
|---:|---:|---:|---:|---:|
| .1 | .05 | 33.7735 | 8.5264 | 7.6964 |
| .1 | .2 | 17.7001 | 4.3368 | 3.5883 |
| .1 | 1 | 4.3762 | 1.0238 | .7473 |
| 1 | .05 | 5.1684 | .9468 | .9468 |
| 1 | .2 | 1.8925 | .3073 | .3073 |
| 1 | 1 | .2337 | .0466 | .0466 |
| 10 | .05 | -.0424 | -.0187 | -.0187 |
| 10 | .2 | .0600 | .0013 | .0013 |
| 10 | 1 | .0290 | .0019 | .0019 |

Slow/moderate transport preserves a benefit from co-location, and autocatalysis
increases it over the reaction ablation. Fast transport largely removes the
placement distinction; small residual rankings depend on temporal resolution.
These are exact finite calculations to floating-point accuracy, not significance
tests or a phase diagram from nine choices. The full12-law/3-resolution sweep
is retained in the ignored numerical summary; no winning coordinate was selected
as the definition.

For d=.1,k=1,T=4, ready vs separated has:

| Observable | Ready | Separated |
|---|---:|---:|
| Forward autocatalytic events | 1.6539 | .9698 |
| Reverse autocatalytic events | 1.4132 | 1.2137 |
| Mean X molecules at4 | 1.6185 | 1.3783 |
| Total physical events | 17.6093 | 14.9777 |

Ready undergoes net forward autocatalysis and ends with more X than separated.
Both begin with2 X, so this is not net total X population growth: the independent
X->A reaction also acts. Many autocatalytic events are reversed. It would be
incorrect to describe the gross forward count as lasting constructed capacity.

At dt=.2 in this same panel, ready's fresh breadth exceeds the stationary
reacting-mixture mean by3.2871bits and matched-composition placement mean by
1.3739bits. Those are within this reactive adapter; no numerical cross-adapter
comparison to FHP was performed.

## What this supports

Published autocatalytic chemistry can make spatial placement improve subsequent
weighted branching, with fixed material stock, equal model preparation free
energy and no output bonus. There are parameter regions where that advantage
survives fresh rooting. There are also weak or reversed differences.

The measurement is not algebraically identical to total activity here: with
k=0,d=.1,T=4 both preparations have13.6 expected events, while their sampled-path
breadths differ. Nevertheless, for active autocatalysis both event counts and
breadth change. This probe does not isolate an effect of constructive retention
independent of additional stochastic reaction activity. The k=0 ablation is
not an activity-matched nonconstructive chemistry. This limitation matters.

## New FHP correction

[The invariant audit](fhp_invariant_audit_v0.md) found three exact alternating
linear quantities on the even tori. Grid preparations have all three zero;
the broad fixed-(N,P) thermal references generally do not. Thus the earlier
rate excess is still a valid difference against that broad reference, but it
cannot yet be attributed to within-sector organization or generativity.
The amount explained by this mismatch is unmeasured. Do not carry its ratios
forward as a matched-sector defeat of gas.

## Next discriminating experiment

Use the same published chemistry to compare long-lived production of catalysts
against mostly reversed turnover, with matched preparation resources. Report
the rate of retained downstream enabling alongside gross activity and breadth;
do not add it as a reward. An activity-matched kinetic control would then help
separate increased reaction opportunities from rearrangement of their outcome
weights. Only after that local mechanism is understood should the RDME edge be
expanded into a2D lattice. Its chemical channels and thermodynamic assumptions
must stay explicit.

Separately, FHP needs a thermal reference conditioned on the additional invariant
labels (or a published rule extension that removes them). Merely running longer
cannot repair an invariant mismatch. No new extent formula is proposed here.

## Artifacts and checks

Model: `omega_v2/finite/closed_schlogl.py`; runner:
`omega_v2/validation/reactive_breadth_v0.py`; tests:
`tests/test_closed_schlogl.py`. All24 combined reactive/FHP tests passed.
Generator row errors below1e-14, detailed-balance residual below2.8e-17; native
transition matrices checked stochastic. Full reaction sweep took approximately
0.1seconds. Raw summary stays ignored in `results/local_runs/reactive_breadth_v0`.
No commit/push performed. Broader molecular or ethical conclusions remain open.

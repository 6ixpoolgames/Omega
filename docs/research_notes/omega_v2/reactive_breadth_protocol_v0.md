# Closed Schlogl reaction-diffusion breadth probe v0

2026-10-07. Declared before run. No required winner.

Published reaction mechanism: Boon et al., Lattice Gas Automata for Reactive
Systems, eq173, printed p43: A <-> X; B+2X <-> 3X.
https://arxiv.org/pdf/comp-gas/9512001
We adapt this mechanism to the standard reaction-diffusion master equation
(RDME), not a reproduction of their exclusion-based LGA or open reservoir
parameters. RDME reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC6964990/ .

Two equal, well-mixed neighboring voxels (one local edge of a spatial lattice),
four molecules total, species A,X,B. Local propensities:
A->X: a; X->A: x;
B+2X->3X: k*b*x*(x-1); reverse: k*x*(x-1)*(x-2).
These use ordered falling-factorial mass-action convention; factorial constants
are absorbed into k. Unit voxel volume, c1 sets time unit, diffusion per molecule
per directed edge d. All species diffuse equally. No species labels encode value.
Equal standard chemical potentials and reverse/forward constants give the
conditional multinomial equilibrium pi(s) proportional to product 1/n_i!.
There is no external chemical feed. This is an isothermal mesoscopic model,
not microscopic energy-conserving dynamics: solvent/heat are implicit, all species
have equal assigned standard energy and mass. No claim of an actual molecular
three-body mechanism or arbitrary spatial continuum refinement.

Restrict to the common active closed component total(A+X)>=2. A+X=0/1 cannot
reach two catalysts; reverse autocatalysis cannot lower the count below2. Check
irreducibility for k>0 and detailed balance exactly to numerical tolerance.

Two exact roots, counts ordered (A,X,B) at each voxel:
ready: (0,2,1)|(1,0,0); separated: (1,2,0)|(0,0,1).
Same species totals, occupied-site multiplicities3+1, equilibrium probability
and therefore equal excess free energy of the point-root distribution. Only
which substrate is locally beside the X pair differs. No claim that different
physical laboratory preparation protocols have equal implementation costs.

References: (1) stationary ideal reacting mixture on that component; (2) dispersed
placement ensemble with the same global A1,X2,B1 composition, each molecule
independently assigned to either voxel, with native combinatorial weights.
The second is not stationary. Neither is the previous FHP fluid gas; no cross-
adapter numerical comparison. No initial-ensemble entropy added to rooted scores.

Sweep k=0,.1,1,10 and d=.1,1,10; k=0 is a declared reaction ablation (changes law,
splits components). Do not treat it as a same-law thermal comparison. For each
use exact K_dt=exp(dt Q), dt=.05,.2,1; observe complete state sequences on that
physical sampling grid, to T=1,4,16. This retains the Shannon breadth candidate
but resolves CTMC histories only at dt; intermediate events are not all observed.
No fictitious uniformization clock or jump-count clock. Report dt dependence.

Compare total log2 breadth, fresh future from the distribution of actual states
at T=4, and integrated expected reaction/transport activity. Compute the fresh
quantity E[ell_(X4)(4)] as an ensemble of exact-root future projections, not entropy
of the mixed present or a time average. Track expected X and forward/reverse
autocatalytic event counts. Construction evidence is limited to production of
additional catalysts; morphology, reusable new transformations and value are absent.

The decisive contrast is whether a matched prepared arrangement gives greater
fresh breadth, and whether enabling autocatalysis changes that contrast over k=0.
A positive raw breadth change when reactions are added is insufficient by itself.
Do not pick a winning dt or parameter after seeing results. Raw outputs ignored
under results/local_runs/reactive_breadth_v0. No push this turn.

# Sol's local-field and distinguishability direction

2026-10-05. Assessment of the user-supplied discussion against current code and
primary literature. No dynamics rewrite, new metric adoption or simulation.

## Recommendation

Borrow the local-observable and stochastic-field viewpoint. Keep quantifying
possibility extent as the main task. The current covering run exposed a loss
of physical relations in the whole-state mismatch distance; it did not show
that more elaborate substrate physics is needed to resolve that loss.

The physical field Phi(x,t) is a description of the substrate along a history.
The continuation field is the weighted, relational collection of such
histories, their compatibility and residual processes. These are different
levels. Calling both a field must not substitute the substrate's spatial
volume or its linear response for continuation extent.

Bounded distinguishability belongs to a frame. A difference invisible to one
frame remains in the encompassing object and may have consequences elsewhere.
An inaccessible difference is not physically deleted. Use the existing frame
conditioning and restriction machinery; no new value prior is needed.

## What the chemistry already supplies

The inspected lattice_chemistry.py and protocol already specify excluded local
occupancy, two conformations, nearest-neighbor bond energies, square-local
catalytic templates, reversible reaction channels, explicit thermal units,
and separate native resource accounting. Mechanism-wise detailed balance is
specified. Symmetry, dimensionless energies and kinetic controls are already
part of the model, not new requirements discovered by this proposal.

An exact field representation can put occupancy/conformation on lattice
sites and bonds on nearest-neighbor links, preserving constraints and the
current generator. Particle IDs remain replay bookkeeping. This is a useful
change of representation without changing physical trajectories.

Two actual locality approximations remain:

- The fuel/waste inventory is well mixed: a reaction changes the supply factor
  seen by distant reactions without explicit fuel transport.
- Whole rigid bonded components move in one update; their rates depend on
  component size. This is an effective collective-motion rule, not a generator
  made exclusively from bounded-support updates independent of aggregate size.

These are declared physical approximations, not implementation bugs. Spatial
fuel diffusion or explicit local mechanical relaxation would change the
physics and should be a separate version responding to an identified question.

Stochastic reaction-diffusion field formulations already exist. Doi-Peliti
methods recast classical jump processes in field-theoretic notation; they do
not turn probability distributions into quantum amplitudes. A field-theory
translation would not itself improve or validate our physical assumptions.

Sources: [Peliti, original lattice birth-death path integral](https://math.pku.edu.cn/teachers/litj/notes/stoch_topics2017/lect05/Peliti1985.pdf);
[del Razo, Lamma and Merbis, modern stochastic reaction-diffusion treatment](https://arxiv.org/abs/2409.13377).

## Distinguishability is principled but not uniquely supplied

The cited [Hou et al. paper](https://arxiv.org/abs/2305.07597) does discuss the
Bures metric and its relation to pure-state Fubini-Study geometry. It does not
derive our trajectory distance or a unique local mixed-state metric.
Mixed-state monotone geometries form a family:
[Petz and Sudar](https://arxiv.org/abs/quant-ph/0102132).

Operational discrimination also depends on available measurements, locality,
time, records and resources. Restricted measurement families induce different
distinguishability norms: [Matthews, Wehner and Winter](https://arxiv.org/abs/0810.2327).
This matches the programme's frames, but does not justify an unrestricted
laboratory capable of every measurement at no cost.

For classical perfectly resolved configurations, distinct point distributions
are already maximally separated by total variation (and distinct orthogonal
classical encodings by quantum trace distance). Importing a quantum metric
name therefore does not automatically give a graded physical distance.
The physical observation map or accessible comparison operation matters.
Uncertainty is not generally a hard pixel size below which states become the
same; discrimination depends on the complete operation and its resources.

One principled finite route is to specify native observation channels to local
and joint records, then compare their resulting record laws under the existing
frame conditions. This can calibrate distinguishability without changing the
actual weights of histories. Whether it supplies a useful covering distance
remains a candidate question, not a uniqueness claim.

## Local discrepancy integrals need joint structure

For realized classical lattice histories, summing site discrepancies over time
is an understandable alternative to one whole-state mismatch bit. It remains
a modeling choice about spatial measure and the relative treatment of site,
bond and resource variables. Bonds live on links; different property types do
not acquire a common unit merely by appearing in the same vector.

If d_state instead compares one-site probability distributions or quantum
reduced states, summing it loses joint information. The classical ensembles
{00,11} and {01,10}, each with equal weights, have identical single-site
marginals and disjoint joint supports. The Bell states (00+11)/sqrt(2) and
(00-11)/sqrt(2) likewise have identical one-qubit states and orthogonal joint
states. Every sum of their one-site marginal distances is zero while an
appropriate joint readout distinguishes them. These examples do NOT show
that distance on realized classical configurations automatically loses the
same information; the two proposed objects must be distinguished.

Therefore retain joint regions, link records and their physical relationships.
Do not resolve the previous whole-state compression by discarding correlations
in a collection of single-site marginals. The last probe's local destination
frame recovered11of36 distinctions hidden in whole-state covers; it supplies
an immediate finite comparison before any field-theory rewrite.

## Response is part of the object, not the complete object

Linear response detects propagation near a state or ensemble. It does not
exhaust nonlinear composition or distributions of failure and recovery. For
f(u,v)=u*v at (0,0), both first derivatives vanish although a simultaneous
finite change to (1,1) changes the output. A response derivative alone can
miss exactly this kind of joint enabling.

The repo already has native-event residual response calculations. Preserve
their finite changes and full future laws; a response function can summarize
them or help characterize coupling. A large response is not automatically a
large extent, and a small response is not automatically absent continuation.

## Coarse-graining and parameter claims

Project the same fine history law to declared coarse frames first. This is
consistent with the existing construction. The projected dynamics need not
remain Markov: omitted variables can produce memory. A newly fitted coarse
generator needs a stated closure approximation, not automatic reuse of Q.
See [Aristoff, Johnson and Perez](https://arxiv.org/abs/2305.20083).

Loss of a distinction after coarse-graining does not prove it is noise or
irrelevant. Fine structures can matter, and fluctuations can have persistent
or collective effects. Study the scale profile without imposing survival of
coarse-graining as an admission test or deleting fine-scale noise.

Symmetry and balance constrain permitted terms and rate ratios; they do not
uniquely determine kinetics, barriers or a truncation. This was explicit in
the current protocol and aligns with [Rao and Esposito](https://arxiv.org/abs/1805.12077).
Dimensionless comparisons are appropriate: E/(k_B*T), barrier/(k_B*T), and
k_reaction*a^2/D when D is a diffusion coefficient. A ratio of a reaction rate
to D without a length scale is not dimensionless. Current lattice hopping
prefactors are rates; restoring lattice spacing a gives D units length^2/time.

Do not call the model a derived effective field theory before supplying its
scale/closure approximation and error regime. A declared effective lattice
reaction/assembly model is already a legitimate starting point. No Planck
cell, relativistic covariance or quantum-gravity assumption is needed.

## Next bounded step

1. Give existing configurations an exactly equivalent site-and-link description.
2. Declare local and joint physical observation frames at a few spatial scales;
   derive all coarse histories from the same retained fine histories.
3. Apply the covering machinery to those frames with explicitly specified
   distance, preserving full weights, temporal dependence and frame relations.
4. Reuse coupling, noise, reliable-construction and reconvergence controls.
   Investigate what each geometry retains; require no favorable gas ranking.
5. Change fuel transport or mechanics only for a demonstrated locality question.

This assesses the proposed borrowing without substituting another broad
physics-development programme for the requested possibility-volume prototype.

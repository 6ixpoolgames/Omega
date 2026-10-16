# C5: exhaustive reactive allocation assay

16 October 2026. Local implementation and initial finite-controller assay.

The scientific question is what complete finite-history lushness prefers among
the available state-dependent policies. Fuel matching and activity matching are
explanatory controls; they do not constrain the primary optimizer. Rates remain
secondary diagnostics. No claim requires a guessed winner to occur.

## Scope and relationship to the spatial experiment

The first exhaustive search uses two fixed-contact apparatus compartments and a
shared stochastic resource. This is a new count-grain adapter reusing the paid
pump, reversible catalysis, fractional banks and physical control construction.
It is **not** a quotient of the mobile friction world. It omits movement,
confinement, discovery and material sinks. It tests allocation, transfer and
conflict of subject; it cannot settle whether spatial confinement is beneficial
or harmful. Apparatus channels are not experimentally certified conscious valuers.

The common controlled substrate contains all reaction channels in all policies.
Installing a different table changes only the local apparatus-to-command
coupling. This is the equal-controller-architecture intervention assumption;
program fabrication, learning and the process of installing a table are outside
this assay. It does not replace the field-first physical programme with an
ontology of available actions.

## Physical state and energy

State is `(packet, D apparatus, S apparatus, D bank, S bank, pump fuel, selector)`.
Packet and fuel are bits; D has two apparatus slots and S one. Both banks have
capacity two with half-unit resolution. The selector has five physical modes.
There are 3,000 states; no state or reaction is removed to make a ranking fit.

Energy is `2 packet + D apparatus + S apparatus + D bank energy + S bank energy
+ 0.5 pump fuel`. Selector conformations have equal internal energy. Reference
density is the product of binomial apparatus multiplicities. All native pairs
use `k sqrt(density(target)/density(source)) exp(-beta DeltaH/2)`, beta = 1.
With the source drive off, every policy obeys detailed balance. The maintained
packet inlet/export are declared work boundaries at rates 0.12/0.015; no
independent controller work source exists.

Each party can capture packet energy, build apparatus with stored energy,
disassemble, and exchange energy with the bath. Apparatus can form thermally;
the world therefore permits reconstruction and is irreducible. S shares the
packet and transfer route with D. At kappa zero there is still resource coupling;
kappa adds cooperative assistance and is not a separability switch.

Basal pump charging and both transfer directions exist in every mode. Charging
moves 0.5 energy from D's bank into the physical fuel bit; extraction/donation
consumes that fuel and transfers one bank-energy unit. Their true reverse
reactions reconstruct fuel and reverse the transfer. Reaction names do not
certify the realized net direction or profit; the full ledger decides those.

## Embodied policy architecture and exhaustive family

Observation is D's local working apparatus count. There is no remote sensing,
belief state or oracle observation channel. Apparatus-dependent kinetics directly
implement the response. At zero working apparatus, active command and catalytic
increments cease; basal selector relaxation and native chemistry remain.

The oracle searches **all 6^2 = 36 deterministic stationary tables** on the two
active observations, one and two working D units. Responses are:

- hold: issue no command;
- idle: command idle mode;
- productive: command the productive mode;
- extract: command the extraction mode;
- donate: command the donation mode;
- combined: command half productive, half extraction allocation.

All tables have the same physical selector, root and channels. Selector mode is
actual memory, included in D's histories and the whole-state histories. A command
takes a finite-rate transition (coefficient 0.08 times working fraction), debits
0.5 D energy, and changes mode. Its reverse refunds fuel. Both endpoints have the
same apparatus observation, so the hardwired conductance respects thermal
reversibility. Four autonomous relaxation routes have total coefficient 0.003,
including when D has no working apparatus. Commanding a mode is not a guarantee
of occupying it continuously. Hold is not the same as commanding idle.

Assisted catalytic capacity is shared: productive allocates (1,0,0), extraction
(0,1,0), donation (0,0,1), combined (0.5,0.5,0), idle (0,0,0) across productive,
extraction and donation assistance. Combined is a feasible allocation, not two
full devices for the price of one. Basal capture assistance is present throughout.
The additional productive capture coefficient is 0.12; pump assistance 0.4 and
charging coefficient 0.08. Operating modes have an additional reversible bank
leak coefficient 0.008 per working D unit. These are distinct physical costs,
not a reward or penalty attached to a mode name. Thermal reverse refunds remain.

This is exhaustive within this controller architecture, not over arbitrary
observations, memory, response rates, continuous allocations or nonstationary
policies. The two apparatus levels are physically asymmetric to make both
observation rows actionable. No 10:1 population is instantiated.

## Measurement and comparisons

Common exact root: packet present, one working unit per party, D bank empty,
S bank one, fuel empty, selector idle (total energy five). Initial-root selection
and controller labels add no entropy.

Whole-field objective is conditional complete sampled-state history entropy at
T = 16, 64, 256, 1024 and cadences 0.125, 0.25, 0.5. Each horizon is a separate
stationary-controller comparison, not receding-horizon optimization. A policy
may spend more or move more matter if its complete continuation ranks higher.

D's subject is its apparatus, bank, pump fuel and selector. S's subject is its
apparatus and bank. Background is the shared packet. D/S objectives are actual
marginal history entropies. They are hidden-Markov processes: report certified
conditioning lower/upper bounds, tightened to two observed steps, rather than
fitting projected Markov chains or substituting coordinate shares.

For each horizon/cadence report:

- the numerical whole-field maximizing set, all constant controls, hold/hold,
  and the best nonconstant table;
- D/S possible maximizing sets: retain every table whose upper bound overlaps
  the greatest lower bound. These are outer sets, not certified optima;
- strict D/S comparisons only when intervals separate, including comparisons
  against hold/hold and the whole-field winner;
- both parties' energy stocks, functioning, capture, construction, signed
  transfer, gross transfer/reversals, pump charging, paid switching and mode use;
- full stationary rate, marginal-rate bounds, expected jumps and temporal finite
  coefficient, as diagnostics rather than alternative primary objectives.

Numerical comparison allowance is at least 1e-5 bits, enlarged by both policies'
sampled-Poisson residual times the number of samples. HMM conditioning bounds
are mathematical bounds evaluated numerically, not interval-arithmetic proofs.
No interval midpoint is used to choose a subject winner. A cadence sign flip is
reported as temporal sensitivity, not selected away. Three clocks are not a
claim of invariance over state grains or all time resolutions.

Mechanism interpretation includes D+/S-/whole-, D+/S-/whole+, all-positive,
all-negative, and unresolved comparisons. Stock loss is not silently relabelled
history narrowing; material profit is not inferred from a positive entropy gain.
No fairness, survival, protection, suffering, consent or domination term is added.

## Engineering and expansion

Modules register background, chemistry, paid pump and selector events separately.
World metadata declares fields/subjects; the analysis is independent of locations
or a fixed state-tuple layout. New observations must declare their physical
coupling. New modes expand the selector and reaction allocation; new population,
composition, spatial discovery or damage modules must declare state, energy,
dependencies and observer ownership. All policy counts are recomputed explicitly.

Validation checks exhaustive table coverage, real switch debits and reverses,
absence of active commands without apparatus, idle charging, shared catalytic
capacity, fractional-grid exactness, state caps, dark detailed balance and both
parties' energy ledgers. A small query checks the streamed two-observation bounds
against the original tensor query; a direct small-history enumeration checks
that bounds enclose actual marginal-history entropy.

Every execution uses the existing immutable-source runner, process-tree wall/RAM
caps and checksum receipts. Smoke: 240 s / 3 GiB; survey: 600 s / 3 GiB per worker,
at most two workers, 4-hour batch budget. Compact JSON/CSV summaries and code
archives are retained; full kernels live only in worker RAM. No scheduled purge,
automatic commit or push is introduced. HDD output is not a substitute for a
bounded-memory algorithm.

Matching realized fuel/activity, opportunity-window reanalysis, spatial steering,
policy uncertainty and larger populations remain follow-ups. They do not block
this primary state-dependent policy comparison.

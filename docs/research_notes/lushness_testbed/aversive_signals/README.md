# Central-wager adversaries: W1/W2 engineering slice

This slice implements costed signalling, escape, obstruction and hijacked
signalling in the existing exact CTMC compiler. It is an engineering substrate,
not a frozen scientific test and not evidence for or against the central wager.
The primary objective remains complete conditional sampled-state history
lushness. Randomness counts. No Rule A, suffering penalty, survival reward,
entropy subtraction or protection bonus is present.

**Update, 14 October:** a separate bounded first scientific registration is now
complete. FIRST_BATCH_PROTOCOL.json froze 32 parameter points and 384 analyses
before execution. FIRST_BATCH_ASSESSMENT.md reports two primary adapter-relative
functional K1 counterexamples, no stronger full-corridor kill, and K2
noninstantiation. The original PROTOCOL_DRAFT.json remains an engineering draft;
it was not relabelled or overwritten. W3/W4 and the full proposed r2 grid remain
future batches.

**Register-control follow-up:** REGISTER_CONTROL_PROTOCOL.json now records a
completed 216-analysis sweep of B, B_R, A0 (also B_T), and A. Physical moment
matching was fitted before new rankings. Independent paid flicker beats B at
the reference; removing blocked response improves breadth; high upkeep reverses
the flicker advantage. See REGISTER_CONTROL_ASSESSMENT.md. These controls explain
the original counterexamples without removing them. B_X and physical k-valued
extensions remain separately scoped in REGISTER_EXTENSION_ROADMAP.md.

## Physical specification

State: stored-energy units, body location (hazard/outside), signal register,
hazard state, environmental patch. Defaults: energy cap 4, quantum 0.5;
204 states including dead bodies at either location. The same register and
environmental states exist in every arm. The environment keeps evolving after
energy-zero death; active physiology and control stop. Body location remains.
There is no independently added immortal controller.

Food is an external input. Every forage attempt pays 0.5 energy; accepted food
adds up to 2 units before the storage cap. Full-store food is rejected and the
attempt still pays its bill. Escape costs 1 energy whether successful or not.
Signal charging moves 0.5 energy from the store into the signal register;
deactivation dissipates it. Upkeep and metabolism dissipate fixed quanta at
declared rates. Thus payment times are stochastic native dynamics, not average
deterministic bills or free abstract random choices. Energy and bath ledgers
close for every state. No equilibrium/local-detailed-balance claim is made
for this open driven, irreversible physiological model.

One actual forage pathway and one motor/escape pathway are represented. A
larger repertoire is deferred until its physically distinct outcomes and costs
are specified. Repeating an event label cannot add entropy in this compiler.
Normal physiology has a basal escape propensity. A tracking or hijacked active
signal shifts the motor propensity toward escape, reducing foraging opportunity.
An obstructed attempt spends energy without moving the body.

Arms E/A/B/C/N follow the proposed functional/blocked/calm/inactive/no-signal
contrasts. D/E-prime/N-prime use one explicitly matched rare-hazard environment.
E-prime is not assumed to qualify as tracking merely because of its name.
Likewise independent signal-on propensity in D does not prove absence of
tracking: downstream state correlations and self-cost can still produce MI.
Every required qualification must be measured before interpreting a comparison.
Signal-off controls do not consult their unused signal bit. C remains a
diagnostic comparator: stopping behaviour changes physiology substantially.

## Measurement and instantiation

Resolved histories use the exact native sampled kernel. Hiding the signal
generally produces a non-Markov observed process. The readout therefore bounds
its history entropy using conditioning inequalities, and validates the bounds
against exact HMM prefix enumeration. No merged CTMC is substituted. An overlap
of broad intervals is unresolved. A compression verdict requires the entire
difference interval to lie within a frozen tolerance.

Tracking diagnostics report both signal/external-hazard mutual information and
signal/future-breadth-drop mutual information. The latter currently uses
one-window energy/location breadth under a signal-disabled counterfactual with
matched environment and escape availability. It is explicitly a local
diagnostic, not full multi-step valuer-history breadth or a finalized T
definition. Signed conditional drops are retained because MI alone does not
establish that the signal tracks narrowing. Disposition is the change in the
normalized native escape propensity at matched physical conditions where both
forage and escape are affordable. Occupancy, obstruction, survival and physical
event/cost integrals are reported separately. No threshold or suffering index
is silently selected to make an arm pass its definition.

Destination-coordinate entropy shares have order hazard, patch, energy,
location, signal, conditioned on the full physical past. These shares add
exactly to sampled-history entropy. They are not a causal decomposition by
native event family: multiple events can occur between samples, and injury can
change signal and energy together. Native event counts are separate readouts.

## Workflow and freeze boundary

Run `python scripts/run_aversive_signal_smoke.py` from the repo. The runner
snapshots source and draft before imports, with a 90-second hard timeout,
512-MiB memory cap and 8-MiB output cap. The smoke checks each arm separately,
withholds scientific arm comparisons and never scores kills. Source snapshots
and raw runs live in ignored local results; compact status documents can be
published. No scientific runner bypassing the freeze is supplied.

Before science, freeze the physiological anchors, energy resolution and bills,
full grid, T/D definitions and thresholds, suffering-index definition, roots,
comparison pairs, tolerances, corridor/kill scoring and compute budget. Separate
an individual adapter-relative counterexample from a stronger corridor-robust
result. Rate ties after death are not complete-history compression ties.
The grid from the discussion is not silently reduced to this smoke configuration.

## Boundaries and extensions

The continuing patch/hazard process is a coarse stochastic baseline, not a
microscopic thermal body/bath model. Post-death chemistry and body dispersal are
not yet represented. The model has no learning, lineages, growing population,
multiple valuers or phenomenal-consciousness claim. Paired arms are mechanism
contrasts, not different roots under one identical generator. They receive the
same environmental prescription; accepted food/work can differ and must be
reported, not called equal absorbed work.

The reusable observation-bound module accepts arbitrary deterministic physical
projections. Native events use WorldSpec/RuleModule and retain dependencies and
energy ledgers for composition. W3 sensitivity search and W4 costed domination
remain separate next modules. A two-valuer design must physically couple access,
confinement and defence, and specify any matched-benefit construction before
ranking. Neither has been implemented or run by this engineering slice.

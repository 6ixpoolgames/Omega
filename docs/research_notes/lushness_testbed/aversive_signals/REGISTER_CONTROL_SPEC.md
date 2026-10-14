# Follow-up: unvarying register, independent flicker and blocked response

This experiment follows the two known K1 points W1-00/W1-08. Selection of those
points is disclosed: this is explanatory follow-up, not held-out confirmation.
Original findings remain intact. No changes to legacy A/B generators are made.

| Arm | Activation | Behaviour | Physical costs |
| --- | --- | --- | --- |
| B | No activation | Normal | Basal physiology |
| B_R | Independent switching | Normal | Register charging and upkeep |
| A0 | Injury-triggered | Normal | Register charging and upkeep |
| A | Injury-triggered | Blocked escape drive | Register charging, upkeep, effort and opportunity |

“Unvarying register” describes B. Its environment and physiology still branch;
it is not an inert universe or a psychological boredom condition. There is no
claim about pleasure or pain in B_R/A0. B_R lacks behavioural reading of the bit,
but shares an energy store: it is not dynamically decoupled from the whole world.
All arms are obstructed, with the same food and stochastic background process.
No semantic bonuses, noise subtraction or persistence filter enter the objective.

## Matching before new scientific ranking

For each parent point, calibrate independent on/off rates to A's expected
signal occupancy time and physical signal-switch count over T64 at upkeep/basal
ratio 0.05. Signal reset at death counts as a physical switch. The fit evaluates
continuous-time physical integrals only, never lushness. Use positive rates and
relative residual <=1e-6; matching failure blocks scientific execution.

The unit charging and upkeep bills are identical. Total charging work need not
match: A can spend energy on a signal charge in an injury event that exhausts
the store without producing a surviving bit. B_R requires enough energy to
activate a live register. This mismatch, death correlations and hazard
correlations are reported. Matching two moments is not matching the complete
register path law. It does not remove activity/cost as causal explanations.

Hold the fitted rates fixed across the upkeep sweep. Recalibrating at each
cost would change both kinetics and costs and obscure the mechanism. Occupancy
and flux will cease to match away from the reference point; report the residuals.

## Prospective first sweep

Upkeep/basal ratios: 0,0.01,0.05,0.1,0.25,0.5,1,2,4. Zero is a limit diagnostic;
charging still costs positive energy. Two parent configurations x nine upkeep
values x four arms x three cadences =216 arm/cadence analyses. Report complete
finite conditional sampled histories at T16,64,256,1024, plus rates and offsets.
The primary readout remains T64 at cadence 0.25. Audits use 0.125 and 0.5,
with the same resolved and hidden-signal bounds as the prior experiment.

Predictions are deliberately falsifiable: B_R beats B at the positive-cost
reference; B_R loses at high upkeep; A0 beats A at the reference. These are
physical model predictions, not assumptions in the ranking. Report all sign
crossings, including multiple or absent break-even brackets. No monotonicity or
simple additive energy penalty is assumed. Independent switching entropy alone
does not determine the coupled-world break-even.

A-B repeats the prior primary comparison. B_R-B tests whether ordinary physical
register variation can compensate for cost. A0-A isolates the consequences of
reading the signal into blocked behaviour. B_R-A0 contrasts independent and
injury-linked activation with normal behaviour. A-B_R checks whether the adverse
arm beats the matched neutral control. No new suffering kill is scored from a
register-control label or a failed tracking qualification.

## Workflow and limits

Calibrate under a separately frozen matching plan and a 120s/512MiB hard cap.
Store the target, achieved moments and fit diagnostics. Then write immutable
REGISTER_CONTROL_PROTOCOL.json including fitted rates, source hashes, complete
grid and predictions. Run a source-identical capped smoke before science.
Scientific cap:600s/512MiB/64MiB output. Do not shrink the grid after observing
rankings or modify rates to obtain a desired crossing.

Exact entropy and energy checks remain mandatory. Raw data and snapshots stay
in ignored local results; compact reports and source are suitable for Git.
The background is a coarse patch/hazard process, not microscopic thermal physics.
All valuers eventually die in this fixture; common tail rates cannot establish
that variation lacks value, or that only exploration creates a sustained rate
increment in maintained worlds. B_X requires a separate costed spatial/resource
module and is not part of this run.

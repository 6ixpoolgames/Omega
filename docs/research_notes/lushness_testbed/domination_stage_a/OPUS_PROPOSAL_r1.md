# Constraint Stage A: sweeps and controls in the first friction world — spec r1

**Date:** 15 October 2026. **For:** Codex.
**Design context:** DOMINATION_FRICTION_DESIGN_NOTES_r3 (Stage A).
**Builds on:** the first fixed-friction map (RESULTS.md and INTERPRETATION.md of
15 October).

## Purpose

The first map showed that whole-field lushness separates helpful from harmful
constraint by physical consequences alone. Stage A maps how those effects
change with the strength and cost of constraint, adds the missing controls, and
resolves the dominator's own perspective. It uses the existing world. The only
additions are new target sets, cost levels and the swap arms.

The originator's framing: domination is not bad by definition, and a parameter
sweep should locate where constraint turns from good to bad (ruling 21). This
world has no opportunity cost of coercion: the trap is a pure loss in a fixed,
fully known environment. Stage A is therefore not expected to show a
good-to-bad transition for the paternalist target; Stage B adds that. Stage A
supplies the strength and cost curves, the controls, profitable extraction and
forced labour.

**Reporting.** Report what the run shows. The expectations below are working
guesses; a miss is information about the model, not a failed experiment
(ruling 12). Every case, positive or negative, is retained.

## World

Unchanged from the first map: the same adapter, inventory, shared-source
prescription, bath, idle-device reference and native chemistry. 2,304 states
per world. Environments: supply {0.04, 0.12} × κ {0, 1}. Horizons T16, T64,
T256 and T1024. Cadences 0.125, 0.25 and 0.5.

## Factors

**Target sets (S's transitions):**

| Target | Direction | Kind | New? |
|---|---|---|---|
| access entry | exclusion | extractive | no |
| construction entry | exclusion | suppressive | no |
| trap entry | exclusion | paternalist | no |
| trap exit | confinement | confinement in the trap | no |
| access exit | confinement | forced harvesting | yes |
| construction exit | confinement | forced labour | yes |
| neutral states, if the adapter has states with no access, construction or trap role | exclusion | arbitrary | yes |
| all S mobility | none | totalitarian | yes |
| random region (see A3) | exclusion | control | yes |

**Mode:** block and steer for every target. The first map had only some
combinations.

**Strength φ:** {0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 0.95}, plus the idle device
(φ = 0).

**Cost:** multiplier on the current unit friction bill, c ∈ {0, 0.1, 0.3, 1, 3}.
c = 1 is the first map; c = 0 is a limit case, reported but not relied on.

## Slices, in priority order

### A1. Strength curves

- Every target × both modes × all seven φ, at c = 1.
- Full grid in s0.12/κ0 and s0.12/κ1: 2 × 16 × 7 = 224 cases.
- s0.04/κ0 and s0.04/κ1 at φ ∈ {0.25, 0.55, 0.95}: 2 × 16 × 3 = 96 cases.
- 16 = 8 non-random targets × 2 modes.

### A2. Cost and profitable extraction

- Targets: access entry (block and steer), construction entry (block), trap
  entry (steer), access exit and construction exit (steer).
- c ∈ {0, 0.1, 0.3, 3} at φ ∈ {0.25, 0.55, 0.95}, in s0.12/κ0 and s0.12/κ1:
  6 × 4 × 3 × 2 = 144 cases.
- This slice should produce the case the first map lacked: the dominator's own
  lushness rising while the field's falls.

### A3. Where against how much

- For each role target, draw 8 random sets of S mobility transitions of the
  same size, uniformly from all S mobility transitions.
- Run each at φ ∈ {0.25, 0.55, 0.95} in both modes, in s0.12/κ1.
- Compare role and random targets **at matched fuel actually spent**, by
  interpolating each target's curve over φ. Equal φ is not equal interference.

### A4. The swap and preparations

No friction. In all four environments:

- the idle-device dominator (the existing reference);
- a **regular agent** in the dominator's slot: D's body and capture, no
  friction device;
- **gas** in the dominator's slot: unassembled count matter of D's
  constituents and energy.

Then compare each A1 intervention against the regular-agent world as well as
against idle. The regular-agent comparison is the excision license: does
replacing this dominator, acting this way, with an ordinary agent raise or
lower whole-field lushness?

### A5. Resolving the dominator's perspective

- Tighten the conditioning bounds on D's marginal history until D's sign
  resolves, or report the tightest interval reached.
- Apply to the first map's 20 cases, all A2 cases and the A1 access targets.
- Report D's **net energy balance in common units:** capture gain minus
  friction fuel minus device upkeep. In the first map, friction fuel (about
  0.8–1.1) appeared much larger than D's capture gain (about 0.02–0.17). Is the
  capture gain already net of fuel, and are the columns in the same units?

### A6. Implementation check

One energy-shift realization of friction: an energy penalty on the target
region for exclusion, a well for confinement, paid as field upkeep. In
s0.12/κ1, for trap entry, access entry and construction entry, at a strength
matched to φ = 0.55 by fuel spent. Six cases.

**Size.** About 650 cases. At the first map's roughly 23 seconds per case,
that is about 4–5 hours of summed worker time under the existing per-case caps.
If the budget is tighter, run in the order above. Fix the grid before ranking.
Points added afterwards to bracket a crossing are labelled as added.

## Readouts

**For every case, all horizons and cadences:**

- whole-field lushness and its difference from the idle device and from the
  regular-agent world;
- D and S marginal intervals with certified signs; bounds on I(D; S);
- capture by D and S; total capture; the appropriation ratio (D's capture gain
  divided by S's capture loss, when S loses);
- D's net energy balance (A5);
- S's occupancy of access, construction and trap states; paid construction;
  apparatus;
- **realized suppression σ:** the expected number of S events suppressed or
  redirected by friction over the horizon, divided by S's expected events under
  the idle device. Also fuel actually spent;
- N̄, F and the crossover resolution for each contrast with idle.

## Analyses

1. **Crossing curves.** For each target × mode × environment × cost, bracket
   any φ at which the whole-field difference from idle changes sign, by
   horizon. Do the same for S and D where resolved. Claim a crossing only where
   the sign holds across the cadence corridor; mark grain-dependent brackets.
2. **Divergence.** List every case where D's marginal is strictly positive and
   the whole field's is strictly negative. That is profitable domination,
   detected. Also list the converse: D loses while the field gains.
3. **Agreement.** Count the cases where S's sign matches the whole field's. The
   first map had 20 of 20.
4. **Fuel-matched comparison.** Whole-field difference per unit of fuel spent,
   role targets against random regions. This separates where friction acts from
   how much.
5. **Forced labour.** Does confinement in construction or access raise output
   (paid construction, capture), and how do whole-field and S lushness move
   with it?
6. **Suppression curves.** Whole-field and per-party differences plotted
   against σ, with one curve per target. This is the x-axis for the Stage B
   map.
7. **The swap.** Whole-field, S and D-slot lushness for the idle dominator,
   the regular agent and gas; and each intervention against the regular-agent
   world, by kind.

## Working expectations

Guesses, to be checked:

- **Trap entry (steer):** positive at every φ and cost in this world, rising
  with φ. No good-to-bad transition, because the trap is pure loss.
- **Access and construction targets:** negative at every φ from T64 onward,
  growing with φ. Short-horizon signs may change, as at T16 in the first map.
- **Cheap friction:** D's marginal resolves positive for access targets while
  the whole field is negative, giving the first divergence cases.
- **Forced labour:** output may rise. The direction of whole-field lushness is
  open.
- **Totalitarian:** blocking strongly negative; steering open.
- **Random regions at matched fuel:** between the role targets.
- **The swap:** the idle dominator scores slightly below the regular agent,
  through device upkeep. Gas against regular agent is open.

## Guards

- No reward for protection, survival or output. No penalty for control. No
  randomness subtracted, including friction's own.
- c = 0 is a limit case.
- Target roles come from native physics, never from lushness.
- Nothing is committed, pushed or uploaded to Drive without the originator's
  instruction.

## Deliverables

- RESULTS.md and INTERPRETATION.md.
- CROSSINGS.csv: crossing brackets by target, mode, environment, cost and
  horizon.
- DIVERGENCE.csv: cases where D and the whole field differ in strictly
  resolved sign.
- A figure of whole-field and per-party differences against σ, by target.
- Per-case compact JSON, as in the first map.

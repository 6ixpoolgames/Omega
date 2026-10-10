# Operational continuation comparison protocol v0

Status: specification fixed before implementation; known finite acceptance cases
Date: 2026-09-28
Base: 506ef363a3f27ec4713617089f4f7f3caf8a7d9c

## Question and scope

Can an exact finite implementation preserve local information, joint feasibility,
origin-based time/resources, and history while comparing task achievement with
uniform response emulation? This is a semantics audit, not a new experiment
validating lushness, value, identity, or a theory of consciousness.

The motivating cases and expected distinctions were already derived in review.
Passing them shows implementation correctness, not independent empirical discovery.
No prescribed ethical winner, policy prior, or capability bonus is introduced.

## Fixed implementation contract

Reuse omega_v2.finite.model.FiniteDistribution, ControlledMarkovSystem,
FinitePath, and the observation/memory semantics of FiniteStateController.
Use Fraction arithmetic throughout probabilities and comparisons.

A context supplies conditional input preparations, a finite controller catalogue,
a horizon measured from the common initial origin, and a scalar token budget.
Each team member acts only on its own current observation and internal memory.
Controller programs are chosen before the external input is drawn. Physical
communication changes later observations; it never discloses a simultaneous
action retroactively. Explicit random transitions are the only randomization
in the finite catalogue. No arbitrary convex mixtures of policies are added.

Record complete state/action paths, each participant's observation and memory
history, time, cost, and unfinished status. Keep every positive-probability
outcome. Reject a policy if any supported path exceeds the registered budget;
do not renormalize its successful or inexpensive branches. Empty catalogues
are reported as unavailable, not as demonstrated zero capability.

Models are small operational machines, not thermodynamically validated devices.
Finite controller ROMs and sensors are preinstalled as declared apparatus.
Token/time charges describe the operations included in each case; no claim
of equal apparatus manufacturing cost is made.

## Two comparisons

Achievement: maximize each declared task's success probability over the same
admissible catalogue, using an explicitly supplied physical input preparation.

Uniform emulation: for every target controller, find one source controller whose
projected response law agrees for every input in the common declared interface.
The source witness must be selected before the hidden input, and retained for
audit. This is finite catalogue emulation, not a theorem of universal online
simulation or unrestricted compositional substitution.

Compare both under explicit output projections and common time/budget bounds.
Full histories and cost laws remain in the evidence even when a response
projection omits them. A restricted output comparison does not preserve an
omitted quantity by implication.

## Acceptance cases

1. Hidden/revealed bit: a sender sees a fair bit; the actuator only sees it after
   a physical transmission. Hidden best guessing is 1/2; transmitted best is 1.
   Revealed can emulate hidden response laws; hidden cannot emulate copying.
   Conditional optimization is retained as a deliberately unsound control.
2. Selectable/random output: installed selection with an explicit coin can
   emulate a fixed coin; the reverse fails. Removing the coin from the selector
   leaves taskwise maxima high but prevents exact emulation of the random law.
3. Shared consumable: two local repair commands contend for one token; individual
   success maxima are one but simultaneous success is impossible. Two tokens
   permit both. Compare marginal and joint task families.
4. Build/wait: preparation and use share one origin, deadline, and token account.
   At two ticks/two tokens, build-then-use succeeds and wait cannot. A savings
   requirement produces a mixed comparison. Tight bounds expose censoring and
   unavailable prefixes. Include a probabilistic failed setup without dropping it.
5. Same endpoint/different history: equal terminal response, time and cost can
   coexist with different earlier signal histories. Endpoint emulation can tie
   while history emulation fails.

## Additional controls and decision gates

- Passive binary distributions: enumerate k/20 for k=0..20. Complement-complete
  event dominance is equality; do not generalize this to all controlled models.
- Verify lawful local observation/memory use, failure mass, exact normalization,
  unavailable-policy reporting, and explicit randomization.
- Verify emulation's quantifier order, witness correctness, reflexivity and
  transitivity within matched finite interfaces.
- Relabel states/actions consistently and duplicate controller descriptions:
  attainable projected laws and verdicts must not change.
- Refining the selected test family may remove taskwise dominance. Record a
  concrete case; do not manufacture universal comparability.
- Retain definitions, expected/observed gates, complete laws and witnesses,
  source hashes and base revision. Failed gates must yield a nonzero CLI exit.
- Run focused tests, relevant predecessor tests, repository witness smoke,
  lint and diff checks. No Lean changes or proof-assistant result are planned.

## Deliverables and provenance

New finite module, five-case experiment, command-line evidence runner, tests,
a mathematical note, and a retained report under docs/research_notes/omega_v2.
Reuse the dynamic-continuation, controlled-Markov, controller, and
process-interface work explicitly.

Motivation: Omega Cosmology v3.1 Parts 02-04, 08, 11-12, 14 and the
28 September 2026 lushness-deformation addendum, especially its distributed-access
and branch-selection cautions. The new code operationalizes these cautions.
The interpretation remains conditional on the declared model and test frame.

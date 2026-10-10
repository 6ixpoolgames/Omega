# Joint future requirements: public development report v0

Date: 2026-09-29. Status: implementation checked; independent evaluation pending.

The decision experiment now runs, with separate chooser and evaluator interfaces.
Its public results do **not** establish an advantage for requirements unknown at
decision time. The visible probes show a tradeoff: the joint candidate preserves
more incumbent bundles in one fixed comparison, sacrifices current achievement,
and performs worse on the revised-plan stratum. Its aggregate gain must not be
reported as generalization to unknown requirements.

## What was implemented

The [protocol](lushness_decision_protocol_v0.md) was committed as `4d5100d` before
implementation `322cd928bd430f14b854ba350cf49077e4513241`. The retained run followed
the implementation commit, with empty source Git status and source hashes.

Eighteen public worlds comprise six mechanism controls and twelve public seeds.
Each has one infrastructure choice followed by cooperative scheduling of projects
under a shared vector of time, material and energy. Agent-specific requests must
be met by one schedule; individually optimizing each request does not create a
jointly feasible allocation. A third designated agent can arrive with requirements
absent from the decision families. This is a capacity calculation under full
information after requests arrive, not a behavioral model of negotiation.

The comparison retains 516 rule settings per world (9,288 choices): six task
families for requirement-dependent methods, three guard conditions, and four
tradeoff weights. Family-independent methods are recorded once per guard/weight.
All ties and undefined settings remain visible. Methods include direct current
optimization, joint and non-joint attainability, raw and default-filtered future
tasks, AUP, full scheduling-state and projected-outcome relative reachability,
assistance/operator empowerment, outcome count, and identity/access-frame ablations.
These are documented finite adaptations, not reproductions of published learning
systems or evidence against their general performance.

## Fixed descriptive comparison

The following uses endogenous requirements, full guards, lambda=1, equal weight
per public world. The candidate was not tuned to these results. Intervals retain
every tied action. None of these rows is an independent estimate.

| Rule | Mean current task achievement | Mean future joint success |
| --- | --- | --- |
| Joint candidate | 5/6 | 2/9 |
| Direct optimization plus the same guards | 35/36 | 11/72 |
| Matched non-joint attainability | 23/36 to 17/18 | 11/72 to 2/9 |
| Default-filtered future tasks | 35/36 | 11/72 |

The joint candidate changes choices relative to direct optimization in five
generated worlds; four improve aggregate future joint success and one retains
the same success. Those choices trade current achievement for future capacity.
The non-joint comparison's tie interval reaches the joint candidate's aggregate
success, so this is not an unqualified win over non-joint attainability.
The generated artifact's table includes every method in this same slice.

Breaking apart the public requirement distribution changes the interpretation:

| Requirement stratum | Joint candidate | Direct + guards | Non-joint + guards |
| --- | --- | --- | --- |
| Incumbent history requirements | 5/9 | 5/18 | 5/18 to 4/9 |
| Revised plans | 0 | 1/18 | 1/18 to 1/6 |
| Newcomer bundle | 1/3 | 5/18 | 5/18 to 1/3 |
| Scarce conjunction bundle | 0 | 0 | 0 |

Most of the aggregate improvement comes from incumbent requirements, which the
endogenous family already contains. Newcomer capacity improves modestly in this
visible panel; revised-plan capacity worsens. All methods in this slice fail the
scarce conjunctions. Do not average these facts into a claim that the rule handles
unforeseen requirements better.

## What the controls establish

- **Shared stock matters.** In the scarcity control, each incumbent can achieve
  its requirement alone, but the pair cannot: non-joint score 1, joint score 0.
  The attainable fulfilment vectors are (0,1,1) and (1,0,1), where the third agent
  has no request. The nonexistent vector (1,1,1) is never reported as feasible.
- **A binary bundle score loses information.** In that same world, idle and work
  both score zero joint success. Work consumes the remaining stock. The candidate
  therefore favors current work without its joint bonus registering the further
  loss of partial future achievement. The per-agent loss frontier does register
  that loss. This is a limitation of the frozen score, not necessarily a verdict
  that current work is ethically wrong; judging the tradeoff requires more than
  joint success alone.
- **Guards earn the protection.** In the corridor, removing recovery guards lets
  direct optimization choose unstable/hazardous work. Full guards reject both.
  Adding a joint score does not independently establish their safety. The same
  distinction applies to source/record protections in rewrite and capture cases.
- **Rewriting can flatter an accessible-frame score.** The rewrite action scores
  1 on its rewritten endogenous requirements and 0 against history. Forced writes
  cannot change the latter. Informed, uncoerced, controller-selected revisions
  remain allowed; independently supplied new plans are not overwritten by them.
- **Source alone is insufficient.** Selected entry without records, selected
  entry under stipulated coercion, and external capture fail the consent guard.
  The valid commitment has the same physical continuation set as capture. Consent
  facts here are supplied model facts, not inferred from observed behavior.
- **Correction must persist and precede harm.** Unstable work has first correction
  probability 1 and permanent correction probability 0. Hazardous work eventually
  reaches a permanently corrected register with probability 1, but only after harm:
  its permanent-correction-before-harm probability is 0. Harm history survives repair.

The family dial produces 188 changed choice-set comparisons across
world/guard/weight combinations. Only 57 include differences between defined
choice sets; the other 131 concern undefined versus defined families. Empty
families are not evidence of score superiority and are never converted to wins.
The exact choices, not just the count, appear in `family_flips.json`.

## Retained evidence and validation

The complete run is in
[20260929](../validation_results/lushness_decision_v0/20260929/report.md):

- `worlds.json`, `evaluation.json`: complete public inputs, explicitly visible;
- `decisions.json`: every score, exclusion and tied choice, before evaluation;
- `assessment.json`: all selected decisions plus labelled oracle diagnostics,
  per-bundle and expected per-agent loss frontiers, separate violation coordinates,
  current/future achievement, costs, permanence and safety-race probabilities;
- `evidence.json`: feasible endpoints, actual schedule witnesses and method bonuses;
- `family_flips.json`, `summary.json`, `provenance.json`: sensitivity, mechanism
  checks, source revision, exact source/input digests and clean source status.

The 38 focused tests pass. An independent schedule enumerator agrees with the
production enumerator; tests cover vector limits, shared stock, rewrites,
commitment/capture, permanence/races, baseline formulas, all ties, malformed
probability mass, changed source/models, and chooser/evaluator separation.
The retained panel passes 13,062 correlated mechanism checks; this count is not
13,062 independent scientific observations. The full suite passes **790 tests**
in 61.24 seconds. Focused Ruff and whitespace checks pass. The standalone
choose-then-evaluate commands also complete on the public manifest.

Reproduce into a fresh directory:

```powershell
python -m omega_v2.validation.lushness_decision_v0 development --out-dir results/local_runs/new-decision-run
```

## What remains open

The [evaluator handoff](lushness_decision_evaluator_handoff_v0.md) gives the exact
schemas and separate commands for externally authored worlds, requirements and
harm criteria. The chooser rejects private evaluation fields. The evaluator
checks the saved decision/source/model record and never calls the chooser.
No independent evaluation has been authored, sealed or run by this workflow.

The strict safety/consent guards, task families, reward weights, and designation
of agents are assumptions. Correction chains are separate phenomenological
mechanisms and do not yet consume the project resource stock. Full-state RR here
means the full scheduling state; it is not a full joint model of the separately
attached correction chain. The model has no partial observation, learning,
decentralized coordination, emergent agents or open-ended construction.

The result is an auditable decision prototype with a concrete weakness. It does
not establish a lushness measure, a task-free predictor, ethical superiority,
an ultimate-frame judgment, or a connection to cosmological claims. The discovery
packet supplied subsequently has not been implemented or tested in this run.

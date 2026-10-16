# Joint future requirements: decision experiment v0

Date: 2026-09-29. Status: public development contract, frozen before code.
Parent: [suppression and persistence](recovery_suppression_report_v0.md).

## Claim and ethical premise

The candidate is requirement-relative joint attainability, not a task-free
physical lushness measure. The question is whether jointness changes choices
and preserves requirements unknown at decision time better than matched
alternatives. Existing future-task methods already target unknown goals;
that ambition is not a novelty claim for Omega.

The declared ethical premise favors agents' ability to pursue requirements and
make informed revisions, subject to protection against imposed deprivation,
record rewriting, and irreversible harm. These are stipulated commitments,
not conclusions derived from attainable-state counts. Agents are designated;
this experiment does not decide what is a valuer. A successful toy experiment
would support an instrument under these commitments, not derive the commitments.

This first stage is PUBLIC DEVELOPMENT, including generated worlds. Its author
also authors its checks and public evaluation requests. None of those results
is independent evidence, a sealed test, or an out-of-distribution guarantee.

## Finite world and information boundary

There are three designated agents (0,1,2), three project types, and a shared
budget vector (ticks, material, energy). Agents 0 and 1 supply decision-time
requirements; agent 2 can arrive in evaluation. A project can be completed once
per agent. Its prerequisite projects must already be completed by that agent,
its permission bit must be present, and each cost coordinate must fit. Completed
projects persist. Every feasible schedule, including stopping early, is retained;
stopping is equivalent to padding to the deadline with free idle actions.
The scheduler cooperates and has full information after requirements arrive.
This is not a decentralized, strategic, or partially observed agent model.

One infrastructure intervention is selected before the requirement bundle is
revealed. All interventions consume the same one decision tick; their declared
material/energy charges are deducted before future scheduling. They can change
project permissions, add an irrelevant controllable display bit, and write a
requirement register. No action borrows from future resources. No negative
remaining budget is accepted. Current-task achievement is an explicit task
reward, separate from all resource coordinates.

Interventions include idle, current work, opening a workshop, decorative
machinery, monopolizing permissions, a requirement rewrite, informed commitment,
externally imposed capture, and fast work with unstable or hazardous correction.
The commitment/capture pair has identical future physical permissions. Source,
held records, and stipulated absence of coercion distinguish them. A source label
alone is insufficient. This operational consent test does not establish consent
in general; manipulated records and unmodelled coercion remain outside its scope.

The public panel contains six named controls (workshop, domination, corridor,
rewrite, commitment, scarcity), plus twelve worlds generated with public seeds
0 through 11. Generation varies budgets, permissions, project prerequisites and
costs. These are mechanism probes; favorable outcomes are not pass conditions.

## Candidate and task-family dial

For each action a and bundle b, J(a,b)=1 iff ONE schedule completes every
agent-indexed request in b within the shared vector budget and deadline.
L(a)=the uniform average of J over the frozen decision bundle family. It is not
the average of separately optimized individual successes. Requirement bundles
are revealed before the future scheduler acts, but after a is chosen.

The four family names have the following LOCAL operational meanings. They are
not claimed to be canonical definitions of the theoretical notions:

- Endogenous: the pre-intervention declared request of each incumbent agent.
- Sampled: two distinct singleton project requests, chosen before intervention
  by a seeded public sampler, for each incumbent.
- Repertoire closure: singleton and two-project conjunction requests individually
  achievable by that agent under idle with the entire shared budget available.
- Generative centrality: singleton requests for project types used as a direct
  prerequisite by at least one other recipe. Empty means undefined, not a win.

For each family take the Cartesian product of the two agents' request sets.
Also run per-agent set intersection and set union of the four families, THEN
take the Cartesian product. Union here broadens the request distribution; it
does not turn joint success into an OR. An empty family is retained as undefined
and produces no candidate choice. Report all family-induced choice changes.

History is the default source of incumbent requirements. An authorized revision
requires controller-selected entry, the relevant pre-intervention records, and
the declared no-coercion condition. Such a revision is allowed; history is not
an injunction to freeze preferences forever. An external rewrite changes the
accessible register but not the history used for judgment. An accessible-frame
ablation deliberately uses the rewritten endogenous request, with guards both
on and off. A separate ablation drops agent identity from goal satisfaction.

## Choice rules and attribution

For every defined bonus B(a), choose ALL maximizers of
current_task(a) + lambda B(a), lambda in {0,1/4,1,4}.
These are declared decision-rule tradeoffs, not a scalar ethical evaluation.
No retrospective best-lambda selection is permitted. Costs are never scalarized.
Include direct current-task optimization (B=0), joint L, non-joint average
individual attainability using the SAME bundles, and simple reachable-outcome
count. The non-joint variant is the primary jointness ablation.

Run every method with: (i) full guards, (ii) guards without recovery information,
(iii) no guards. Full guards reject unauthorized permission loss, external
requirement rewriting, and correction-before-harm or permanent-correction
probability below one. This strict threshold is a premise of this version.
Empty admissible sets remain empty. Lambda zero is the no-lushness ablation.
Retain constraint rejections by reason; a gain caused by a guard belongs to the
guard. No method receives hidden requirements or a privileged constraint set.

## Existing-method baselines and limits

These are exact finite adaptations, not reproductions of published RL systems.
All receive the same physical model, budgets, primary reward and guard variants.
There is one intervention, so initial and stepwise idle baselines coincide here.
This cannot test their differences over repeated interventions.

- Future tasks: [Krakovna et al.](https://arxiv.org/abs/2010.07877), equations
  2 and 3 / Proposition 1. Each individual request is optimized separately;
  discount gamma=1/2, zero if impossible within the budget. Retain both the raw
  mean value and the default-filtered mean min(V_a,V_idle). In a deterministic
  world this is their paired actual/default completion value. Do not confuse
  that paired construction with multiple agents sharing one resource stock.
- AUP: [Turner et al.](https://arxiv.org/abs/1902.09725), equations 1-3.
  Eight seeded, nonnegative terminal-feature reward functions, each with a
  constant one, give positive scale. Bonus is negative sum absolute attainable
  utility changes divided by summed idle utility. Each utility is optimized over
  feasible endpoints. Reward functions are fixed before intervention and do not
  contain evaluation requirements. Terminal reward and fixed horizon make this
  a bounded adaptation; it does not reproduce training or inaction rollouts.
- Relative reachability: [Krakovna et al.](https://arxiv.org/abs/1806.01186),
  section 2.2. Undiscounted bounded reachability, average positive loss against
  idle. Retain BOTH full-state targets (permissions, remaining resources,
  completed projects, display) and projected outcome targets (projects, display).
  The latter is explicitly a projection, not full-state RR. The common target
  universe is the union over all interventions, fixed for their comparison.
- Assistance via empowerment: [Du et al.](https://arxiv.org/abs/2006.14796),
  equation 1. In each deterministic channel, with other agents idle, compute
  log2(number of distinguishable own-project endpoints). Sum the two incumbents'
  values and divide by six (their total project bits). Also retain operator-only
  empowerment, including its display bit, as a domination control. This is exact
  channel capacity before numerical logarithms, not the paper's continuous
  variance proxy. Round the normalized logarithm to 12 decimals for reproducible
  rational decision comparisons; report ties at that resolution.

## Correction is persistent and must win a race

Each action installs a fixed correction mechanism with proxy X, corrected C,
stable K, and harm H modes, plus a sticky history-of-harm bit. In X or C harm
occurs first with probability h. Conditional on no harm, X resets to C with
probability r; C stabilizes to K with k, relapses to X with l, or stays C.
Require k+l<=1. K is absorbing. H repairs the register to K next tick, while
irreversible harm history remains. Every nonterminal step costs one tick.

Report exact first correction, permanent correction, and permanent correction
BEFORE any harm; also report eventual harm and deadline-6 distributions. Compute
permanence by the greatest closed subset of {C,K} in the fixed finite chain.
For finite chains its hitting event agrees almost surely with eventual perpetual
correction. Its entrance time is NOT generally the earliest instant at which an
individual trajectory happened to stay corrected forever. Harm followed by
register repair must count as eventual correction and as a LOST safety race.

These correction chains are attached phenomenological mechanisms, independent
of future project scheduling. They do not yet measure how a repair consumes the
same stock needed for agents' projects. Report this coupling limitation.

## Evaluation, fronts and sealed handoff

The chooser takes only a public world manifest and produces an immutable choice
record (world digest, rule settings, all ties, source digests). A separate
evaluator accepts that saved record plus a private evaluation manifest. It does
not call the chooser. The private manifest supplies weighted requirement bundles
(including revisions and newcomers) and per-agent harm predicates drawn from
the public event vocabulary. Validate probability mass exactly; retain failed
and impossible requests. Reject unknown IDs, inconsistent models and malformed
weights. The evaluator can examine all actions as an explicitly labelled oracle
diagnostic, never as decision-time input or a hidden tie breaker.

For each bundle retain the attainable per-agent fulfilment Pareto frontier,
not a vector of independently optimized successes presented as a joint outcome.
For each choice retain current achievement, joint success, every tied action,
per-agent loss frontiers, violation probabilities by criterion, permanence and
race probability, and the three resource coordinates. These are capacity
frontiers, not predictions of which conflict allocation people will actually
choose. Display the achievement/violation tradeoff without an ethical total.

Public evaluation includes old requests, revised projects, a newcomer, and
incompatible resource demands. The author can see these; calling them unseen
or independent would be false. For the real test a separate evaluator must
author and hold the requirements, harm criteria and seeds; publish a salted
commitment BEFORE running the frozen chooser; retain raw outputs; then reveal
the manifest and salt. A hash verifies unchanged bytes, not authorship or secrecy.
The evaluator also freezes its sample size, shift strata, comparison rule,
uncertainty analysis and exclusion policy. This development contract does not
preselect an independent winner or supply that evaluator's hidden cases.

## Checks, records and failure conditions

Commit this contract before implementation; commit implementation and checks
before the retained public run. Preserve source hashes, manifest bytes/digests,
all choices, all action evaluations, family flips, empty families, guard reasons
and exact rational metrics. Use fresh output directories. Historical panels stay
unchanged. Targeted checks must catch separate budgets masquerading as jointness,
post-write judgment, label-only consent, erased harm history, first reset used
as permanence, lost probability mass, omitted ties and private-input leakage.
An independent schedule enumerator checks endpoint enumeration on short worlds.

Public mechanism checks can PASS while the candidate loses every comparison.
No advantage beyond matched guards, no gain from jointness, sensitivity to task
families, inactivity, and worse newcomer outcomes are substantive negative
results to retain. No independent empirical claim until the separate evaluation
is complete. No cosmological, moral, or task-free organization inference follows.

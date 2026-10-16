# Continuation prediction pilot: draft protocol v0

Date: 2026-09-28.

Status: proposed experiment contract; no candidate implementation, sealed test
manifest, or experimental results are claimed. This document fixes a concrete
starting proposal for review. A later freeze record must identify the actual
code, generator, task manifest, thresholds, hardware, and evaluator before a
held-out run can count as the registered experiment.

Parent: [operational comparison](operational_continuation_comparison_v0.md) and
its [termination controls](operational_continuation_termination_report_v0.md).

## 1. The question

Can a task-independent, shared representation of bounded continuations preserve
exact task predictions while reducing the total cost of construction and use,
relative to conventional predictive representations?

Separate three possible results:

1. **Correctness:** the representation preserves the registered response laws
   and task probabilities under the actual local controllers.
2. **Engineering utility:** it saves measured computation or storage after
   charging for extraction, updates, and queries.
3. **Distinct contribution:** its semantics or useful computation differ from
   the strongest matched conventional construction.

Correctness does not imply efficiency. Either can hold without mathematical
novelty. A standard construction implemented inside Omega remains a standard
construction. No result here establishes value, an ethical ranking, or a
universal measure of lushness.

## 2. Deliberately bounded first experiment

Use finite rational workshop models: at most two local controllers, 64 world
states, four joint actions, and 16 installed controller teams. Horizons are
2, 4, and 6 ticks. Physical token costs, observations, memory, terminal states,
and preparations follow the existing evaluator's semantics.

Primitive operations may move materials, consume energy, transmit records,
construct or maintain a tool, and perform a job. All construction and use share
one physical origin and budget. Generator strata must include scarce-resource
conflicts, restricted information, useful and wasteful construction, and
specialized equipment. Include both compressible and poorly compressible cases.
The generator must not select worlds according to which method wins.

In this first experiment, every method receives the **same complete finite
kernel and declared observation/cost interface**. The model-building method
knows those laws; the embedded controllers still see only their own permitted
observations. These two information levels must not be confused.

The candidate does not receive the evaluation jobs while building its
representation. The registered vocabulary of measurable atomic events is
public; test formulas composed from that vocabulary are withheld. Jobs can
refer to intermediate events, terminal outcomes, joint completion, elapsed time,
and expenditure. A formula requiring an undeclared observable is out of scope.

This tests compression and prediction given a model. Learning a model from a
limited intervention sample is a separate experiment with additional
identifiability assumptions; it must not be claimed from this one.

## 3. Concrete candidate C1: shared bounded continuation graph

C1 is a proposed implementation candidate, not an assertion that this is the
unique or novel mathematical meaning of Omega generativity.

For each horizon h, recursively represent a world state using:

```text
base(s) = (terminal flag, each local observation, registered observable atoms)

signature_0(s) = base(s)

signature_h(s) = (base(s), STOP)                         if s is terminal
signature_h(s) = (base(s), {
    joint action a -> distribution of (transition cost, signature_(h-1)(s'))
})                                                    otherwise
```

Probabilities are exact rationals. Aggregate mass only when both the cost and
successor signature agree. Intern identical signatures into shared graph nodes;
do not sample successors or discard failure/censored outcomes. Store edge
labels and probabilities, preparations, observation maps, atoms, and the full
decoding information needed by queries. A zero-horizon nonterminal node is
censored, not completed.

Use this graph to execute each installed controller team with its own local
memory updates. An action edge is an available world command, not a license
for a controller to observe hidden state or choose its program after the input.
Retain path readouts while traversing the graph; terminal projection alone
cannot answer a history query.

The primary query is the success probability of a registered job under each
admissible team, followed by the maximum over whole teams where requested.
Comparisons use the existing declared frame and quantifier order. Every claimed
achievement must have a controller witness that the full model can check.

This recurrence is a standard bounded probabilistic behavioral construction:
states have equal signatures exactly when they have equal base labels and,
recursively, equal action-conditioned mass on each cost/successor class. The
expected equivalence with bounded partition refinement follows by induction
on h. The first audit must make that correspondence and its controller/readout
assumptions explicit. C1 therefore starts with **no mathematical novelty claim**.
Any additional Omega-specific extraction claim requires a specified addition
and a demonstrated consequence. An engineering comparison of C1 may still be
useful, but it must be described at that level.

## 4. Reference and baselines

| Method | Purpose and conditions |
| --- | --- |
| Full exact path evaluator | Answer key, respecting the same installed teams, local information, costs, failures, and horizons; reference computation is not counted as candidate work |
| Ordinary memoized finite-state prediction | Strong practical baseline; cache by world state, remaining horizon and physical budget, controller memory, and necessary task-monitor state |
| Conventional bounded probabilistic quotient | Strong representation baseline with the same observation, atom, terminal, and cost distinctions as C1; compare induced classes and laws, not just ranking agreement |
| Truncated simulation | Budget-limited baseline; expose uncertainty and simulation error, rather than calling estimates exact |
| Resource counts and reachable-set summaries | Diagnostic weak baselines; beating these alone cannot establish the main claim |

Use the same supplied model, task language, controller catalogue, and compute
accounting for each method. No candidate gets a causal graph, dependency labels,
or hidden query results unavailable to its competitors. If a baseline supports
fewer query types, report that limitation rather than changing its objective.

An epsilon-transducer comparison is relevant only after matching the input/output
process and memory assumptions. Its literature already supplies a predictive
structural framework; it must not be approximated by a weak unrelated model and
then advertised as defeated. See [Barnett and Crutchfield](https://arxiv.org/abs/1412.2690).
AUP and relative reachability are deferred to an actual decision-objective test.

## 5. Adversarial and identifiability controls

These controls have known answers and check the instrument. Keep their scores
separate from the generated-world results.

- A passive replay matches an observed trace but fails a registered intervention
  to which the original system responds.
- A lookup mimic matches the development queries but differs on a specified
  held-out intervention. Require a separation only when the supplied evidence
  or model actually supports it.
- An operationally equivalent mimic matches all admissible responses, costs,
  and timing. It must remain equivalent within that interface.
- A dormant seed has an explicit activation and construction path with charged
  time/resources. A control lacks that path. Use deadlines both sufficient and
  insufficient for activation; the word `seed` cannot determine the prediction.
- Two models agree on baseline and single-knockout observations but disagree
  after a double knockout. A diagnostic restricted-evidence query must report
  the range permitted by the compatible models, not unsupported certainty.

The last control demonstrates a learning limit. It does not convert C1, which
receives a full model, into a validated causal learner.

## 6. Development, blinding, and freeze

Proposed scale: 24 development worlds, followed by 96 test worlds balanced
across the four generator strata above. Evaluate registered short, medium,
and long horizons. Hold out combinations of mechanisms and task formulas,
not merely new names or seeds. Report results by stratum and horizon as well
as pooled summaries.

The public generator must have a documented sampling distribution and no
method-dependent acceptance filter. A separate evaluator must hold the test
seeds and query manifest until extraction implementations and settings are
frozen. Commit hashes of those manifests, the generator, all methods, and
the grading code. Hashing alone does not create independence or remove a biased
sampling design. Development examples remain available to all implementers.

Current role status: the generator author, candidate implementer, and evaluator
have **not** been assigned independent roles. No sealed seeds have been created.
Runs performed without this separation must be labeled development runs.

The freeze record must also specify the physical budgets, exact task-formula
grammar and sampling rule, software versions, hardware, memory/time caps,
query-batch size, timing repeats, and how timeouts are charged. Check grader
feasibility on development worlds before freezing; do not drop hard test worlds
after seeing outcomes. Reference failures are reported and invalidate the
affected evaluation rather than being silently resampled.

## 7. Proposed decision criteria

These are proposed pilot targets, not constants implied by the theory. Freeze
them with a rationale before exposing test results; any later revision starts
a separately labeled experiment.

| Claim | Proposed criterion | What a failure means |
| --- | --- | --- |
| Exact preservation | Zero probability discrepancies or invalid controller/comparison certificates on completed in-scope queries | The implementation or preservation claim is wrong |
| Useful coverage | At least 90% of registered queries answered within the frozen compute limits, with every timeout and abstention counted | The method is not useful enough for this declared workload |
| Computational advantage | At least 20% lower total CPU time than the strong primary baseline chosen on development data; require a one-sided 95% paired interval supporting that reduction | No registered computational advantage demonstrated |
| Storage advantage | Report total serialized bytes and peak memory, including auxiliary tables, decoding maps, and caches | A separate result; it cannot retroactively substitute for a failed primary time target |
| Distinct semantics | A proved difference or a verified separating example under a common interpretation; otherwise record equivalence or unresolved status | No distinct semantic contribution established |

Choose and freeze the primary strong baseline using development results only.
Report all registered baselines; a stronger competing result must be visible.
Use worlds, not correlated queries within a world, as the statistical sampling
unit. The exact interval procedure and handling of capped runs belong in the
freeze record. No efficiency claim is issued after a correctness failure, or
by deleting queries that timed out. For a computational-advantage claim, the
candidate must answer every query answered by the primary baseline; otherwise
report a coverage/cost trade-off, even if both exceed 90% coverage. Charge both
methods for all attempted queries. Publish setup cost, first-query cost, total
batch cost, and the break-even number of queries separately.

Measure decision coverage separately from query completion. A correct answer
of `incomparable` is different from `unknown` due to insufficient evidence and
from `unavailable` due to an empty admissible catalogue. Do not force a scalar
ranking to improve coverage. No 95%-agreement novelty cutoff is used.

## 8. Invariance and scope changes

Require exact preservation under consistent state/action relabeling and a
proved irrelevant-variable extension. Splitting an operation is an invariance
test only with a validated correspondence preserving duration, costs,
observations, and opportunities to act. Changes to the task family, comparison
frame, or physical deadline change the question; report sensitivity without
automatically labeling changed answers errors.

Any benchmark success applies to the specified model class, task vocabulary,
installed controller family, and workload. It is not evidence that maximizing
the representation is ethically safe. A later adversarial decision test must
first specify the complete choice rule, including constraints and arbitration.

## 9. Implementation order and required outputs

1. Audit C1 against the conventional bounded quotient; record equivalence,
   differences, or a corrected claim before any novelty benchmark.
2. Build the small control panel and an independent exact grader. Add mutations
   for hidden-input policy selection, lost joint resource constraints,
   probability renormalization, and omitted extraction costs.
3. Implement C1 and strong baselines against one input/output contract. Check
   all development cases and measure the proposed workload's feasibility.
4. Complete the freeze record and independent test manifest, then run the
   generated-world evaluation once under that registration.
5. Retain per-world predictions, reference answers, witnesses, error/coverage
   distributions, full cost records, source hashes, and every failure.

The first concrete deliverable is the C1/conventional-quotient equivalence audit
and control panel. The existing 40 acceptance gates remain regression checks;
they are not counted as new experimental evidence.

The separation of development and unfamiliar evaluation settings follows the
generalization concern studied by [Packer et al.](https://arxiv.org/abs/1810.12282).
This protocol is an engineering proposal for Omega's next bounded test; it does
not attribute its candidate or numerical thresholds to that literature.

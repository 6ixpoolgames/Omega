# Operational Continuation Comparison v0

Status: finite definitions, elementary propositions, and executable acceptance cases.

Date: 2026-09-28.

This note makes two continuation comparisons executable under declared local
information, installed controllers, operational costs, and a shared deadline.
The [protocol](operational_continuation_comparison_protocol_v0.md) was committed
as `354be7e` before implementation. These are known finite examples chosen to
check an instrument; passing them is not independent evidence for Omega's
physical or normative claims.

## 1. The finite operational object

An experiment declares:

- A finite world state set and a rational transition kernel for joint actions.
- A finite external input set Q and an initial world-state distribution for
  each input q. The input labels belong to the experimenter, not automatically
  to any controller's observations.
- A finite catalogue of installed controller teams. Each controller has its
  own observation map, initial memory, memory-update table, and action table.
- Terminal states, nonnegative integer transition costs, a common horizon H,
  and a common operational budget B.

At tick t, controller i observes only o_i(s_t), chooses its action from its
current memory and that observation, and updates its own memory from those
same data. The joint action determines the next stochastic world state.
A newly transmitted signal can therefore affect a receiver at the next tick,
not retroactively at the sending tick. There is no separate selector that
can inspect q and choose a different team after seeing it.

The controller tables are deterministic. Random outcomes occur through the
declared world kernel, including a physical coin when one is installed.
The catalogue is not silently closed under randomized mixtures of programs.
Preinstalled controller tables and apparatus are part of the declared context;
their manufacture, discovery, and installation are not priced by this model.
Those costs would need an additional preparation model.

For every team pi and every q, exact enumeration constructs a probability law
L_X(pi,q) on runs. A run records the full world/action history, each local
observation and memory history, elapsed ticks, total cost, and whether the
horizon censored a nonterminal continuation. Terminal runs stop. No operation
is composed after censoring. Failure and unfinished paths retain their original
probability mass.

A team is admissible only if every positive-probability run under every declared
input costs at most B. This is a worst-case bound, not an expected-cost bound.
An over-budget branch rejects the whole team; it is never deleted followed by
renormalization. An empty admissible catalogue is reported as unavailable.

The executable definitions are in
[`operational_continuation.py`](../../../omega_v2/finite/operational_continuation.py).
They reuse the existing exact finite distributions, controlled Markov systems,
finite paths, and finite-state controllers.

## 2. Taskwise achievement

Declare a full-support rational input law w and a nonempty task family T.
Each task is a Boolean predicate on (q, run). Define

```text
A_X(t; w, H, B)
  = max over admissible pi of
      sum over q of w(q) * Pr_{L_X(pi,q)}[t(q, run)].
```

One complete team is chosen for a task before the input is sampled. The
maximum is outside the sum over hidden inputs. A different task may have a
different maximizing team. The comparison X >=_T Y means that X's achievement
is at least Y's for every task in the declared family.

This answers a useful question: how well can each context achieve each target
separately? It does not assert that the taskwise optima can coexist in one run,
nor that a single source controller can reproduce a target's response law.
There is no prior over teams and no aggregate scalar over tasks.

The hidden-bit control makes the quantifier error explicit:

```text
max_pi sum_q w(q) Pr[guess = q | pi, q] = 1/2;
sum_q w(q) max_pi Pr[guess = q | pi, q] = 1.
```

The second expression gives the selector hidden input access that the actual
actuator lacks. It is retained as a deliberately invalid comparison.

## 3. Uniform response emulation

Declare a common response frame F, with a readout rho_X(q, run) into its output
space for each context. The frame includes the meaning of its inputs and
outputs; matching a frame name in software is an assertion by the model author,
not a proof of semantic alignment. Horizons, budgets, and input keys must match.
The projected response is the pushforward law

```text
R_X(pi,q) = (rho_X(q,-))_* L_X(pi,q).
```

Write X >=_F Y when

```text
for every admissible target team tau in Y,
  there exists one admissible source team pi in X,
    such that for every declared input q,
      R_X(pi,q) = R_Y(tau,q).
```

The source witness can depend on the target program, but cannot depend on the
subsequently selected input. Each witness is an actual table-based team from
the source catalogue. The implementation retains the target-to-source mapping.
For a failed target, it retains a differing input for every proposed source
team, together with both projected response catalogues.

This is exact, catalogue-relative response emulation. It does not construct a
single online adapter that transforms arbitrary target programs, price that
adapter, or prove substitution inside an arbitrary surrounding system.
The finite lookup used by the verifier is not a free physical compiler.
No emulation verdict is issued for an empty catalogue on either side.

### Elementary propositions

On nonempty catalogues with one matched frame, uniform emulation is a preorder.
Reflexivity uses each controller as its own witness. For transitivity, compose
the two witness selections; equality of response laws holds for each input
through the intermediate controller. These are direct finite arguments, not
new claims of a general resource-conversion theorem.

Uniform emulation implies taskwise dominance when both contexts use the same
input law and every task factors through the common readout:

```text
t_X(q,run) = tbar(q,rho_X(q,run));
t_Y(q,run) = tbar(q,rho_Y(q,run)).
```

Proof: take a maximizing target team for each task. Its source witness has the
same conditional output law for every input, so the same success probability.
The source maximum is at least that witness's success. The argument also works
for bounded real payoffs of the common response.

The converse fails without additional assumptions. A deterministic selector
can force either binary output, so its maxima for output-zero and output-one
are both 1. A fixed fair coin achieves 1/2 for each. But neither deterministic
selection reproduces the coin's law. Adding a physical coin to the selector
repairs this emulation failure. Free random program mixing would change the
catalogue and can remove this particular separation.

Projection matters. If costs or histories are omitted from rho, output emulation
does not promise their preservation. Full underlying histories remain available
in the audit, but that retention does not strengthen the chosen comparison.

## 4. Five cases and their exact scope

The experiment is
[`operational_continuation_comparison_v0.py`](../../../omega_v2/experiments/operational_continuation_comparison_v0.py).

| Case (left / right) | Operational declaration | Expected distinction |
| --- | --- | --- |
| Revealed / hidden bit | Two ticks, budget 2; sending costs 1 and guessing costs 1; a fair external bit is initially visible only to the sender | Guessing 1 versus 1/2; revealed emulates hidden output, but hidden cannot copy the bit |
| Selector / fixed coin | One tick, budget 1; select 0, select 1, or use an explicitly installed coin | Selector with coin emulates coin; removing the coin retains task maxima but destroys that emulation |
| Two / one repair tokens | Two local repair commands, one tick, common operational budget 2; contested single token is consumed and both repairs fail | Individual maxima tie at (1,1); simultaneous success is 1 versus 0 |
| Build / wait | Both begin before preparation, with two tokens and two ticks; building costs 1, using costs 1 | Service 1 versus 0; adding zero-expenditure as a target makes the achievement profiles incomparable |
| Alarm / clear history | Two ticks and cost 2; each transient signal ends at the same final state | Endpoint/time/cost response ties; full signal-history responses do not emulate one another |

The repair collision rule is a declared miniature physical law. Other arbitration
rules require other kernels. The witness demonstrates why one must model shared
stock and joint execution; it does not infer that rule from real repair systems.

Build and wait are compared from the same initial origin, not from a completed
machine versus its earlier construction state. At horizon 1, the setup remains
censored and service success is 0 when preparation fits the budget. At horizon
2, budget 1 permits building then waiting but no successful use. Budget 0 makes
the build-prefix catalogue unavailable. A separate half-successful setup has
service probability 1/2, with the failed setup retained. These comparisons do
not claim that a larger stock or future capability is always preferable.

The helper exhausts declared reactive controller tables. For these fixtures,
each nontrivial choice occurs once, or the world state physically retains the
relevant received record. Adding private deterministic memory cannot recover
the unobserved hidden bit. In the build fixture, setup success is not observed;
past local observations cannot reveal it. General finite-memory controllers
are supported by the evaluator and tested separately, but their unbounded
search space is not exhausted. The catalogue boundary remains explicit.

## 5. Why a broad comparison can collapse

For two *fixed passive probability laws* P and Q, requiring

```text
P(E) >= Q(E) and P(not E) >= Q(not E)
```

forces equality on E, since both complement probabilities are 1 minus their
event probabilities. Requiring this for every event forces P = Q. The finite
control checks 21 binary laws k/20 and all 441 ordered pairs: 21 ties and 420
incomparable pairs, with no strict dominance.

This argument is specific to passive laws. For controlled envelopes, the policy
maximizing E may differ from the policy maximizing its complement; their maxima
need not sum to 1. The selector example exhibits that distinction. The intended
lesson is to state the object and quantifiers before claiming a general order
collapse.

Refining a task family can remove a tie or a one-sided ordering. Adding joint
repair breaks a marginal tie. Adding savings removes build's service-only
dominance. Incomparability is an allowed and informative outcome.

## 6. Relationship to the retained repository and theory

This work operationalizes cautions already present in Omega Cosmology v3.1 and
the 28 September lushness-deformation addendum, especially distributed access,
whole-policy selection, and a shared time/cost origin. It does not present those
cautions as newly discovered flaws or the elementary mathematics as novel.

The direct predecessors are:

- [Dynamic Continuation Profiles](dynamic_continuation_profiles_report_v0.md):
  controller alternatives and environmental outcomes must remain distinct.
- [Controlled Markov Abstraction](finite_controlled_markov_abstraction_report_v0.md):
  exact kernels and path laws provide the reused executable substrate.
- [Stochastic Blackwell forward bridge](../omega_theory/omega_decision_stochastic_blackwell_v0.md):
  explicit randomized policy compilation is a different, stronger supplied
  mechanism than assuming a randomization source in this catalogue.
- [Process Interface Transport](process_interface_transport_report_v0.md):
  declarations and their transport require checks. Here a consistently renamed
  state/action presentation preserves attainable response laws; arbitrary
  changes of interface are not thereby justified.

The implementation is a new audit layer over `omega_v2` primitives. Historical
adapters supply conceptual provenance; they are not imported or rewritten.
No Lean theorem or existing claim boundary is changed.

## 7. What remains open

The immediate next mathematical problem is to specify an admissible online
adapter and prove a resource-accounted substitution rule. That requires an
explicit connecting interface, local information available to the adapter,
its memory and installation costs, synchronization, and the treatment of
shared resources. Response-law inclusion alone does not discharge those duties.

The larger theory still needs a justified choice of tasks and readouts,
measurement procedures and error bounds for real systems, an account of
capability extraction and preparation costs, and a normative bridge from
attainable continuations to what should be preserved. None follows from these
finite witnesses. A universal lushness ranking is not produced here.

Reproduction details and retained results are in the
[report](operational_continuation_comparison_report_v0.md).

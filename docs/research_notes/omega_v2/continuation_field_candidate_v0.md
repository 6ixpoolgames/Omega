# Continuation field candidate v0

Date: 2026-09-29.

Status: conceptual specification and migration checkpoint. The construction
and physical realization relation below remain proposals. This note adds no
implementation, experiment, proof-assistant result, or cosmology release.

Follow-up: the [finite concurrent continuation contract](finite_concurrent_continuation_contract_v0.md)
attempts the bounded milestone below with one-shot stochastic token dynamics,
three analytic examples, and a direct autonomous-subsystem realization
preorder with explicit resource overhead. Its restricted result does not
close the general physical-realization question stated in this candidate.

Provenance: the field-first discussion following the September 29 discovery
and field packets, including the review of the concurrent-geometry proposal.
Existing executable work is identified separately below.

## 1. Decision and version scope

This is an advance in the proposed representation of the futures field:
joint compatibility, causal dependence, and independent developments belong
inside the object being compared. They are not merely corrections to a count
of sequential paths. Composed physical processes can change which further
developments are accessible, without a fixed catalogue of valuers or values.

Record this as a new candidate specification on the active
`codex/operational-continuation-comparison` branch. Do not promote it to a
numbered edition of the entire cosmology or migrate the active research yet.
The candidate's notation, stochastic interpretation, and physical realization
relation need one coherent, bounded definition before they anchor a successor.

The intended successor is the user-created
[`6ixpoolgames/OmegaCosmology`](https://github.com/6ixpoolgames/OmegaCosmology).
Earlier migration notes naming `alpha` remain historical plans. This note
records the present destination without rewriting those plans or transferring
their proposed contents automatically.

## 2. Target and physical starting point

The target is the structured field of continuation. Organisms, memories,
gates, instruments, and valuers should be configurations or processes within
that field. Their names are not primitive admission criteria.

Start with a specified physical dynamics, including relational configurations,
legal transformations, relevant records, physical time, resource accounting,
and any stochastic law. Access has the same meaning throughout: a continuation
is physically realizable from the relevant history under those conditions.
Its geometry and available combinations can change as processes interact.

This requires more than the current
[`AlphaCore.Frame`](../../../formal/lean/AlphaCore/Primitive.lean). That minimal
record supplies relation, distinction, and an asymmetry predicate, with
limited implications between them. It does not supply transition rates,
composition, costs, or an independence relation. A fully specified Alpha
dynamics could supply these; deriving them from the minimal axioms is open.

Gating is a proposed consequence of differential access: some configuration
makes the consequences of another distinction selective. It must be exhibited
in the dynamics rather than installed as an unexplained gate label. The
[directional-asymmetry report](directional_asymmetry_capability_report_v0.md)
already distinguishes passive statistical asymmetry from operational
selection. An asymmetry statistic alone does not derive a gate or an agent.

## 3. Proposed continuation object

For a physical history h, write schematically:

```text
F_A(h) = (K_A(h), physical time and resource accounting, admissible laws).
```

K is a directed continuation complex, provisionally represented using
concurrent execution semantics:

- Vertices retain partial developments and their physical configurations.
- Directed edges represent legal further transformations.
- Higher cells represent families of transformations whose independence and
  joint execution are physically justified.
- Directed paths represent sequential presentations of developments.
- Residual continuation structure records what remains possible afterward.

[Higher-dimensional automata](https://arxiv.org/abs/2106.11703) provide an
existing geometric language for concurrent execution. Choosing that language
does not yet give a unique construction from an arbitrary physical dynamics.
An equal endpoint after two different orders is insufficient to establish
independence. Pairwise feasibility is also insufficient for a higher joint
cell when several transformations share a limited resource.

Interleavings of genuinely independent events should not inflate the number
of complete developments. For five fixed, independently executable, one-shot
events there are 120 complete sequential orders, one complete concurrent
configuration, and 32 partial configurations. The proposed representation
retains those partial configurations and independent directions.

Composition can create configurations with new subsequent access. A new
composite operation is not automatically a new independent direction. The
object must distinguish concurrent independence from ordered enabling and
from changes in later continuation geometry.

The first formal scope should be explicitly classical. Ordinary positive
probabilities on histories do not by themselves represent quantum interference.
A future cosmological interpretation needs a justified extension or a stated
boundary; this candidate does not settle that issue.

## 4. Probability, description, and records

If a physical model already supplies a stochastic execution law, a measurable
projection to concurrent histories can transport that law. For finite
histories this means summing the masses of presentations identified by the
projection. The projection still has to be justified: it must not identify
orders with different physical consequences.

Local probabilities cannot generally be assigned independently when choices
interact with concurrent events. The
[confusion literature](https://arxiv.org/abs/1710.04570) supplies relevant
constructions under specific assumptions. A confusion-free first definition
is a possible scope restriction, not a claim about all physical worlds.
Scheduler choices and correlations must remain explicit. If several physical
controllers are admissible, retain their conditional laws without inventing
a probability distribution over controllers.

Use exact preservation requirements for harmless changes of description:
physical time, cumulative resource use, causal access, interaction
opportunities, records, and outcome laws must correspond. Splitting an edge
into two steps is harmless only if the inserted stage supplies no new physical
opportunity, observation, cost, delay, or stochastic effect.

History-preserving equivalences are relevant, but a canonical noise quotient
has not been selected. Published
[event-structure reductions](https://arxiv.org/abs/1403.7181) illustrate why
preserving histories does not automatically provide one canonical minimal
presentation. Identical isolated residuals can still have different external
correlations. An unread record can also have later consequences. Neither can
be erased merely by calling it noise.

Quasi-isometry is not the default notion of harmless description here: even
finite metric spaces are all quasi-isometric to a point. Coarse asymptotic
comparisons may be useful, but cannot replace the physical preservation
requirements. Renaming interchangeable copies likewise does not erase their
multiplicity when it changes jointly available resources.

## 5. Proposed comparison and its main debt

The proposed direction is:

```text
F_A >= F_B when B's continuation structure has a coherent physical
realization within A under matched physical conditions and budgets.
```

This is a specification target, not yet a defined general preorder. A
realization must preserve causal information access, shared-resource
compatibility, stochastic outcomes including failures, and later interaction
opportunities. Preparation, adapters, decoding, and control must be physical
and accounted for. A software description of an object is not automatically
a physical realization of that object.

The existing
[uniform response comparison](operational_continuation_comparison_v0.md)
is a proved finite preorder in a declared common response frame. It does not
provide a costed online compiler, arbitrary contextual substitution, or a
realization of the full continuation complex. Those conclusions cannot be
inherited from its finite witness-selection proof.

Separate finite realizations of every bounded pattern also do not by
themselves give one coherent realization of all patterns together. The
definition must state the coherence required across histories and budgets.

Incomparability is an acceptable result. It does not itself justify a scalar
tie-breaker, nor does it establish an ethical verdict.

## 6. What the geometry can currently tell us

Concurrency dimension, composition depth, and physically grounded volume
profiles are candidate descriptors. No one of them has been identified with
lushness. A volume requires a justified metric and measure; counting cells
alone makes subdivision change the answer.

For a regular bracket-generating smooth model, the weighted dimension is
Q = sum_k k n_k, where n_k counts directions first obtained at bracket level
k. [Barilari and Rizzi](https://arxiv.org/html/1211.2325) describe this setting
and its canonical Popp volume. These constructions require the specified
smooth distribution and metric; they do not apply automatically to the
general continuation object.

An elementary analytic example blocks the proposed rule that a larger Q
always means greater access. On coordinates (x,y,z), let:

```text
X = partial_x
Y = partial_y + x partial_z
[X,Y] = Z = partial_z.
```

With velocity uX + vY and u^2 + v^2 <= 1, the growth vector is (2,3),
and Q = 2 + 2 = 4. Add direct velocity wZ with
u^2 + v^2 + w^2 <= 1. Setting w = 0 preserves every old motion at the same
time cost. The distribution now has rank 3 immediately, and Q = 3.

Thus added access can lower this exponent. This is an analytic comparison of
two declared control models, not an experiment or a derivation of physical
controls from Alpha. It rules out that simple monotone interpretation of Q;
it does not rule out useful geometric comparisons.

Do not identify smooth small-scale scaling with large-scale group growth
without the hypotheses of both constructions. Exponential growth alone also
says nothing about whether a law is stochastic or whether its consequences
are valuable. Recursive eigenvector scores from the earlier packets remain
unjustified by changing the underlying representation.

## 7. Relation to ethics

The candidate could make comparisons of jointly available continuation more
faithful. Whether those comparisons track the possibility of value, and when
they should govern action, remain separate questions. Adding an opportunity
to harm is also adding an opportunity; structural inclusion alone has not
resolved that problem.

The
[public decision prototype](lushness_decision_report_v0.md) remains evidence
about its declared requirement families, controls, and ethical premises. It
does not validate this field object or establish an independently evaluated
advantage for requirements unknown at decision time.

New values need not be enumerated to represent new physical developments.
Showing that some such developments constitute valuation, and establishing
their ethical significance, still requires an argument. The proposed field
representation does not supply that argument by definition.

## 8. Next milestone and migration threshold

The next task is one bounded mathematical specification, with hand-worked
examples. No new experimental panel is requested by this checkpoint.

1. Specify a tractable class of physical dynamics and construct its concurrent
   continuation object, including the exact interpretation of probability,
   cost, observations, and residual histories.
2. Define harmless redescription and physical realization in that same class.
   Establish the claimed identity/composition properties, or retain an
   explicit counterexample and revise the claim.
3. Work through independent events, shared-resource exclusion, and a composed
   enabling process. Show which data survive and why these examples are
   distinct without adding organism, value, or gate labels.

A successor first commit becomes worthwhile when this contract is coherent
enough for another reader to follow without reconstructing the conversation.
It can still contain open hypotheses. Solving lushness, proving an ethical
theory, or completing a cosmology is not a prerequisite for opening a repo.

That first commit should contain a short reading guide, the bounded formal
contract, a claim-status ledger, the worked examples, and provenance links to
selected existing results. It should preserve the current repository as the
research record rather than transplant its full history into a new apparent
foundation. Existing local successor drafts need reconciliation before reuse.

This checkpoint advances the candidate specification only. There is no new
test result, empirical claim, cosmology version, or migration in this change.

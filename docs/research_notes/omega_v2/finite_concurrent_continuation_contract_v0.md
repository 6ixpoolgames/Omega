# Finite concurrent continuation contract v0

Date: 2026-09-29.

Status: proposed bounded contract, with ordinary mathematical arguments and
hand-worked examples. No implementation, simulation, test run, independent
empirical result, or proof-assistant verification accompanies this note.

Parent: [continuation field candidate v0](continuation_field_candidate_v0.md).

## 1. What this attempt establishes

For the finite physical models specified below, there is a definite construction
of a continuation complex from transition rules. Independence cells are
derived from resource incidence. Probability comes from a specified stochastic
law, not from assigning weights to the resulting drawing. A narrow realization
relation, direct embedding as an autonomous physical subsystem, preserves that
structure and composes with explicit cost accounting.

One fixed model contains independent, exclusive, and enabling processes. They
have different residual structures and different completion probabilities under
the same firing convention. No organism, valuer, or ethical labels are used.

This is a specialization of established concurrency and stochastic-process
mathematics, not a new foundational theory. Relevant starting points are
[van Glabbeek and Plotkin's configuration structures](https://homepages.inf.ed.ac.uk/gdp/publications/config_Mogens.pdf),
[Petri nets and higher-dimensional automata](https://www.lre.epita.fr/dload/papers/amrane.25.pn.pdf),
and [Ajmone Marsan's stochastic Petri nets](https://doi.org/10.1007/3-540-52494-0_23).
The definitions and arguments below specify this note's narrower conventions;
they do not assert equivalence with every construction in those sources.

## 2. Supplied dynamics and scope

A model N consists of the following finite data:

- A set P of physical places, each with capacity one and a declared physical
  type. A marking m is a subset of P: its members contain a token.
- An initial marking m0.
- A finite set E of transition mechanisms. For e in E, specify input places
  pre(e), output places post(e), a constant firing rate lambda_e > 0, and a
  nonnegative cost vector c_e in common declared units.
- Nonnegative preparation charge vectors k_p in those same units for the
  places and their installed apparatus, counted from the declared comparison
  origin. These charges may
  be zero for apparatus already installed at that origin; that convention
  does not assert that its manufacture was free.
- For each e, a distinct private fuel place d_e in pre(e) minus post(e).
  No transition produces a token at d_e, and no other transition touches it.

The private fuel restriction makes every transition fire at most once. It is
a physical consumable restriction, not an event counter silently added to the
observer's memory. Some fuel places may be empty initially. The model has at
most |E| firings on any run. It excludes replenishment and recurrent processes.

The enabling and update rules are fixed for every example:

```text
enabled(e,m) iff pre(e) is a subset of m
                 and (post(e) minus pre(e)) is disjoint from m.

fire(e,m) = (m minus pre(e)) union post(e).

foot(e) = pre(e) union post(e).
```

An input is consumed even if the transition returns a token to that same
place. There are no nondestructive read arcs, hidden couplings, or implicit
shared reservoirs. Any such coupling would require a different supplied model.
Capacity, incidence, and physical types are modeling inputs; they have not
been derived from the minimal AlphaCore axioms or made invariant under
arbitrary changes of physical factorization.

Firings are atomic. The stochastic waiting time defined below is not a model
of a mechanism occupying resources throughout an extended execution interval.
This matters when interpreting cells: they encode independent firings, not a
derived theory of overlapping manufacturing durations.

There is no external policy selector in this class. Installed control or
record mechanisms can be represented by additional places and transitions
when they satisfy the restrictions. The analyst's knowledge of a marking
does not become information available to a physical controller. Access here
means possible physical continuation under the supplied dynamics, not a power
to choose or reliably achieve every supported outcome.

## 3. A complete probability law

At marking m, let R(m) be the enabled transitions and
Lambda(m) = sum_{e in R(m)} lambda_e.

If Lambda(m) = 0 the run is absorbed. Otherwise the next waiting time has an
exponential distribution with rate Lambda(m), and the next transition is e
with probability lambda_e / Lambda(m). After firing, repeat from the new
marking. Equivalently, use independent Poisson clocks of rates lambda_e and
accept a clock event only while its transition is enabled.

This stipulates a finite continuous-time Markov process and a law on its
labeled histories. It is an actual assumption about the model's dynamics,
not an inference from the unweighted net. There is no unspecified scheduler
or uniform prior over possible programs.

At time t, cumulative cost is C_N(t) = sum_{p in P} k_p plus the sum of
c_e for every transition that has actually fired by t. Time is retained
separately; event rates use the same physical time unit across comparisons.

For a finite deadline H >= 0, a legal word e1...en, and firing times
0 < t1 < ... < tn <= H, the density
of exactly these firings by deadline H is

```text
product_{i=1..n} [lambda_ei exp(-Lambda(m_{i-1})(ti-t_{i-1}))]
    times exp(-Lambda(m_n)(H-tn)),

t0 = 0; m_i = fire(e_i,m_{i-1}).
```

For n = 0 this is the no-firing probability exp(-Lambda(m0)H). Integrating
over firing times and summing over legal words includes every run, including
absorbed and unfinished runs. All budgets are audited on these original
laws. Exceeding a budget is retained as a failure or makes the whole model
inadmissible for a worst-case requirement; it never removes and renormalizes
branches. Physical stock limitations already operate through enabling.

The general
[probability/concurrency confusion problem](https://www.cl.cam.ac.uk/~gw104/VVW-TCS05.pdf)
is not solved by declaring local choices independent. Here a complete race
law is specified first, and it determines competition and its probabilities.
Using this convention does not establish it as the correct physics elsewhere.

## 4. Deriving the continuation complex

Define e I f iff e and f are distinct and their footprints are disjoint.
I is computed from the supplied transition mechanisms; there is no separate
table of desired independence cells.

**Diamond lemma.** If e and f are enabled at m and e I f, then each remains
enabled after the other, and fire(f,fire(e,m)) = fire(e,fire(f,m)). Each
transition also retains its own rate and cost.

**Argument.** A firing changes only its footprint. The other transition's
input and output-capacity conditions depend only on a disjoint footprint.
Updates therefore commute. Rates and costs are fixed transition data. The
same argument applies to any finite pairwise-disjoint family, by induction.

Let legal words be the finite firing sequences from m0, including the empty
word. Identify two legal words only through repeated swaps of adjacent
I-independent transitions. Write [w] for a resulting trace. The diamond
lemma proves that marking and accumulated cost are well defined on [w].
Do not identify all words with equal final markings.

Construct K_N as follows:

- A vertex is a legal trace [w].
- An n-cell is ([w],U), where U is a set of n transitions enabled after w,
  with pairwise-disjoint footprints. A zero-cell has U empty.
- For e in U, its lower face is ([w],U minus {e}); its upper face is
  ([we],U minus {e}).

An arbitrary ordering of E can order the cell coordinates; changing it only
renames axes. Faces exist by the diamond lemma. Taking two upper faces in
opposite orders agrees because [wef] = [wfe]. The other face identities
follow directly. Thus this defines a finite cubical execution object.

This construction's joint cells follow from a special sufficient mechanism:
disjoint physical footprints. It does not infer general joint feasibility
from pairwise achievements. Pooled capacities, alternative allocations and
nondestructive shared reads require an extension or a justified translation.

After a history w, the residual contains legal extensions [wv], keeping w's
provenance. The physical future law depends on its current marking by the
Markov assumption; that does not give permission to erase history from the
field or to turn audit histories into physically readable records.

The decorated field is K_N together with its markings, incidence data,
physical types, rates, cost accounting, and the transported timed-history
law. These decorations matter: K_N alone is not the full object.

The untimed law on traces is the pushforward of the history law. In the
full decorated object, each occurred event also retains its firing time.
Independent events may occur at physically different times and in different
chronological orders; those timing differences are not erased. One concurrent
development can contain many timing realizations. This removes an artificial
count of linear presentations without declaring real delays irrelevant.

## 5. One model, three mechanisms

Take thirteen places and six transitions. Initially

```text
m0 = {p, q, r, c0, d0, u, w}.

Other places a_out, b_out, c_out, d_out, v, f_out are empty.
```

Every transition has rate 1 and work charge 1. Preparation charges are zero
at the already-installed comparison origin. Token stocks and capacities
remain explicit; work charges are not being identified with physical energy.

| Transition | Consumed inputs | Produced outputs | Private fuel |
| --- | --- | --- | --- |
| a | p | a_out | p |
| b | q | b_out | q |
| c | r, c0 | c_out | c0 |
| d | r, d0 | d_out | d0 |
| e | u | v | u |
| f | v, w | f_out | w |

These are three disjoint physical components of one model. The following are
their marginal descriptions under the full law, not three separately tuned
schedulers or a procedure that freezes the other components for free.

| Derived feature | a and b | c and d | e and f |
| --- | --- | --- | --- |
| Initially enabled | a, b | c, d | e |
| Effect of first on second's hazard | 1 remains 1 | 1 becomes 0 | 0 becomes 1 |
| Can both occur? | Yes, either order | No | Yes, only e then f |
| Joint independence cell | One square | None | None |
| Untimed partial traces | empty, a, b, ab=ba | empty, c, d | empty, e, ef |
| Maximal untimed developments | One | Two | One |
| Work after two firings | 2 | Impossible | 2 |

In the enabling component, the enabling predicate for f changes from false
to true when e produces v. This is the promised minimal gating example:
differential subsequent access follows from the update rule. No primitive
gate label was supplied. It shows enabling of an already specified mechanism,
not unbounded invention of new mechanisms or a derivation of valuation.

The full complex has 4 x 3 x 3 = 36 vertices: its components combine by
independent interleaving. This count is an audit of this presentation, not a
volume or lushness score.

For H >= 0, the exact marginal probabilities are:

| State by deadline H | Independent component | Exclusive component | Enabling component |
| --- | --- | --- | --- |
| Neither event occurred | exp(-2H) | exp(-2H) | exp(-H) |
| First only | exp(-H)(1-exp(-H)) | (1-exp(-2H))/2 | H exp(-H) |
| Second only | exp(-H)(1-exp(-H)) | (1-exp(-2H))/2 | 0 |
| Both occurred | (1-exp(-H))^2 | 0 | 1-(1+H)exp(-H) |

For the independent component, two independent exponential completion times
give the first column. For the exclusive component, the first arrival has
rate 2 and each competitor wins with probability 1/2; the consumed r then
blocks the other. For enabling, completion requires two successive independent
rate-1 waiting times. In particular,

```text
Pr[e only by H] = integral_0^H exp(-s) exp(-(H-s)) ds = H exp(-H).
```

Every column sums to one. Waiting and incomplete development retain their
mass. The full law factors across these disjoint components. Its work cost
is the sum across all three, at most 5; the table does not waive background
spending. An equal scalar comparison is unnecessary: the structural and
probabilistic distinctions have been derived under one convention.

These examples have analytically expected answers. They establish what this
contract expresses, not independent evidence for a lushness hypothesis.

## 6. Two checks against false identification

**Equal endpoints do not create a cell.** Modify only the two exclusive
transitions to return r: c consumes {r,c0} and produces {r,c_out}; d consumes
{r,d0} and produces {r,d_out}. Both cd and dc now exist and end at the same
marking. Their footprints still share r. There is no square under this
contract, and the two traces remain distinct. Each transition consumes and
replaces the common token; a two-transition step would require it twice.
Endpoint commutation alone would miss this resource history.

**Subdivision can change the physical law.** Replacing a rate-1 firing by
two successive rate-1 firings changes its completion probability at H from
1-exp(-H) to 1-(1+H)exp(-H). Calling the added place an intermediate drawing
vertex does not restore equivalence. Genuine graphical subdivision must keep
the original physical clock and introduce no new enabled stage, record,
interaction, or charge. It is then an annotation of the original model, not
another two-transition model in this class.

## 7. Exact changes of presentation

A harmless redescription within this class is a bijection of places and
transitions preserving physical types, private fuel, input/output incidence,
initial marking, rates, preparation charges, and cost vectors. Units must
remain common, or be converted explicitly before comparison.

Such a bijection maps legal words and independence swaps in both directions.
It therefore induces an isomorphism of K, preserves its decorations, and
transports the complete timed law term by term in the density formula.
This gives exact invariance under naming and coordinate order, not under
arbitrary coarse-graining, physical refactorization, or deletion of records.
There is no noise quotient or quasi-isometry reduction in this contract.

## 8. Direct physical realization

Define a direct autonomous realization B -> A by injections

```text
i: P_B -> P_A,
j: E_B -> E_A,
```

satisfying all of the following:

1. Place types, capacities, preparation charges and initial token occupancy
   agree under i. The mapped places are actual components of A with those
   physical types, not arbitrary encodings into strings or trajectories.
2. For every e in E_B, pre_A(j(e)) = i(pre_B(e)) and
   post_A(j(e)) = i(post_B(e)). Its rate, cost vector, and designated private
   fuel agree as well.
3. Every transition of A outside j(E_B) has its entire footprint outside
   i(P_B). There are no interactions crossing the image boundary.

This is deliberately stronger than simulation. B must literally occur as
an autonomous subsystem, up to physical renaming. There is no interpreter,
adapter, preparatory search, or hypothetical controller whose cost was omitted.
Initial apparatus charges are explicitly included. Whether declared component
types faithfully describe actual hardware remains a modeling obligation.

**Preservation proposition.** Such an embedding supplies one coherent mapping
of all B histories and residuals into A, preserving and reflecting their
independence cells. Projecting A's complete timed law onto its image gives
exactly B's timed law.

**Argument.** Induction on a word proves equality of image markings and
enabling. Footprint intersections are preserved and reflected by injection,
so trace equivalence and cube faces correspond. Extra transitions neither
change nor inspect image places and commute with every image transition.
Use the same independent clocks for corresponding transitions in A and B.
The projected process then agrees pathwise; the additional clocks drive only
the complementary subsystem. Consequently the equality holds for every
deadline and residual history, not just for separately selected finite tests.

The image can have additional independent surroundings in A. Their execution
is not discarded as a failure, and their charges do not become free. Define
the conservative overhead certificate

```text
kappa(B -> A)
  = sum_{p outside i(P_B)} k_p
      + sum_{e outside j(E_B)} c_e.
```

Each extra transition fires at most once, so for the coupled histories at
every time t,

```text
C_B(t) <= C_A(t) <= C_B(t) + kappa(B -> A),
```

where C includes preparation and all occurred-event charges. The certificate
can overestimate spending when extra transitions conflict. It is a sufficient
bound, not a claim of optimal resource conversion.

**Composition proposition.** Direct autonomous embeddings have identities
and compose. If C -> B and B -> A have certificates kappa_1 and kappa_2,
their composite has certificate kappa_1 + kappa_2.

**Argument.** Compose the injections. The image incidence, types, rates and
charges still agree. An extra transition of A is either outside B's image,
or the image of a B transition outside C's image; in both cases it avoids
C's image. Extra places and transitions partition into those same two
groups, and their charges are preserved. Identity has empty complements
and certificate zero.

For a fixed horizon H and common resource units, define the following
budget-indexed relation on model/budget pairs:

```text
(A,H,b_A) >=direct (B,H,b_B)

iff a direct autonomous embedding B -> A exists
    with b_A >= b_B + kappa(B -> A), coordinate by coordinate.
```

It is a preorder by the identity and composition propositions and addition
of the budget inequalities. If B stays within b_B on every run, A stays
within b_A on every run under that witness. Otherwise no worst-case
admissibility is implied; original over-budget mass remains in the law.

This is not a free same-budget extension theorem. With b_A = b_B, this
sufficient relation requires a zero-overhead witness. Extra costly activity
cannot be called greater same-budget access merely by hiding it in projection.
If all charges are zero, only that declared charge convention is being used;
no assertion of physically free construction follows.

For a concrete nonidentity witness, embed the independent component from
section 5 into the full model. The extra exclusive and enabling transitions
give kappa = 4 work units by the sum bound, although their actual maximum
work is 3. The projected completion law for a and b is exactly unchanged.
The rest of the work remains charged. A sharper certificate is possible,
but is not silently substituted into the proved compositional convention.

## 9. What is still missing

This closes a bounded version of the parent note's three-example milestone.
It also exposes the price of obtaining a clean realization theorem: the
realized subsystem is autonomous and no mechanism is translated into a
different physical mechanism. This relation mainly compares a system with
an independently extended system. It does not establish the broader
realization order proposed for lushness.

Open obligations include interacting embeddings, genuine physical adapters,
faithful changes of component boundaries, recurrent and replenished systems,
shared reads and pooled capacities, a justified structural quotient,
quantum interference, and any defensible invariant or ethical comparison.
The finite transition vocabulary exhibits new access through configuration;
it does not establish open-ended emergence of new mechanisms or values.

The next useful mathematical question is whether a small, explicitly costed
interaction or adapter can extend this realization relation while retaining
the composition and information-access guarantees. A failure would identify
a missing assumption. Another panel of named moral worlds would not answer it.

## 10. Claim status and provenance

| Claim | Status in this note |
| --- | --- |
| A finite cubical object follows from these rules | Definition plus ordinary diamond/face argument |
| The three mechanisms have different residuals and deadline laws | Hand-worked analytic examples in one fixed model |
| Direct autonomous realization preserves structure and timed laws | Ordinary proof for the stated restrictive embeddings |
| Its certified budget relation is a preorder | Ordinary identity/composition proof |
| Arbitrary physical realization is now defined | Not established |
| Gates or rates follow from AlphaCore alone | Not established |
| A lushness invariant or ethical ordering follows | Not established |

The earlier [finite operational comparison](operational_continuation_comparison_v0.md)
remains a separate response-frame result. Its catalogue witnesses were not
used as a substitute for the embedding proof here. The
[suppression and persistence report](recovery_suppression_report_v0.md)
retains the distinction between first correction and permanent correction;
those recurrent mechanisms are outside this one-shot scope. The
[public decision report](lushness_decision_report_v0.md) retains revised-plan
success zero in its fixed comparison and independent evaluation pending.
This new representation supplies no revision of those findings.

Any successor repository should carry these scope statements and provenance
links with the contract. The present attempt remains on the active branch;
it changes no manuscript edition and does not migrate or publish a successor.

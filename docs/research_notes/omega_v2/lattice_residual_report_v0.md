# Exact residual alternatives v0

2026-10-05. Follow-up to the naive realized-history count, authorized by the
user. The unchanged chemical generator is now enumerated completely in a
small positional class, so untaken alternatives and their native probabilities
are represented as well as events that happened.

**Main result:** forming a bond can create a catalytic route for the next
reaction even when the opening event law was identical. Simple reachable-state
counts miss this. The weighted timed continuation law retains it. A matched
pair also shows that equal energy, fuel, bond count and support counts do not
determine this downstream access.

## Exact system and scope

Four particles fill a 2x2 square, using `LatticeChemistry.events/apply` without
changing a reaction. No translation is legal in this fully occupied class;
binding/unbinding, conformation changes, shared fuel, reverse reactions and
catalysis remain active. This is an invariant positional class of the existing
law, **not a gas/mobility comparison**. It is also not a moving patch extracted
from a larger lattice with its boundary dynamics silently removed.

All 16 conformation patterns, 16 bond subsets and capacity+1 fuel stocks are
enumerated. Eight generators cover capacity 1/4, bond energy 0/2 and catalytic
barrier 0/2: 512 or 1,280 states per generator. There are seven preparations:
exact equilibrium in this positional class, refueled equilibrium, and exposed
four-particle configurations with zero, one, adjacent two, opposite two or four
bonds. The latter have initial fuel `min(2,capacity)`.

We retain complete rate-weighted state/channel graphs, ordered state and
channel-sequence counts through eight jumps, distinct-state balls at those
depths, native laws at cuts 0/1/5/20, and residual laws at lags .25/1/4.
Initial zero-jump mass remains. The probability of more than eight jumps goes
to a separate overflow entry without rescaling. Its maximum is 10.10% at lag
4 in the zero-binding, catalytic, adjacent-bond case. Full endpoint laws and
mean event counts are separately computed without that jump truncation.

The atlas took **2.41 seconds**, with eight jobs in a pool capped at ten
workers. There are 224 cut/preparation rows and 672 residual rows. These are
finite-state matrix-exponential calculations, not Monte Carlo estimates.

## 1. Construction changes later access, not the opening catalogue

Consider capacity 4, binding energy 2, initially no bonds, all four particles
exposed and fuel stock 2. Compare catalytic barrier 0 versus 2. Initially
neither preparation has a catalytic template. Consequently the entire
first-event channel/rate law is identical, with total event rate 2.245508.

Once a bond forms it can supply the template for its opposite bond. The exact
native continuation law gives:

| Readout from the unbound preparation | Barrier 0 | Barrier 2 |
|---|---:|---:|
| Distinct successor states | 12 | 12 |
| States within four jumps | 467 | 467 |
| States within eight jumps | 1,178 | 1,178 |
| Mean number of events by time 1 | 1.7653 | 2.0178 |
| Probability next two events are distinct fuel-consuming bindings, both by time 1 | 6.226% | 15.508% |

In the catalytic case, **10.553 percentage points** of the 15.508% consist
of a first fuel-consuming binding whose product catalyzes the second binding.
These are route probabilities derived from the physical event records, not a
generativity bonus. The first binding may also occur thermally: including
those routes, the probability that the first event makes a template and the
second uses it to bind is 21.771% by time 1.

This is a finite mechanism witness for composition changing residual access.
The catalytic rule was already in the model; it is not a discovery of a new
chemical law or a requirement that emergence invent new primitive transitions.
What changes is which native channels are enabled, and their resulting timing
and weight, when physical relations are constructed.

## 2. Same resources and count profile, different continuation

The two-bond preparations have either a corner of two adjacent bonds or two
opposite bonds. With capacity 4, binding 2 and barrier 2, both have:

- four exposed particles, two bonds and fuel stock 2;
- stored energy 7 in model kBT units;
- the same state free energy including fuel multiplicity, `7 - log(6)`;
- 12 distinct successor states and 14 enabled reaction channels;
- the same distinct-state ball sizes at every tested depth 0..8;
- 406,888,960 ordered state sequences of length eight.

Their dynamics differs strongly:

| Native readout | Adjacent bonds | Opposite bonds |
|---|---:|---:|
| Total initial event rate | 4.4421 | 1.2582 |
| Mean events by time 1 | 1.9048 | 1.2834 |
| Next two events both fuel-consuming bindings by time 1 | **34.683%** | **9.842%** |
| Contribution using a newly made template on the second binding | 0% | 8.510% |
| Contribution using an already present template on the second binding | 29.989% | 0% |

In the adjacent arrangement, the existing bonds face the two missing bonds,
so they already catalyze both additions. In the opposite arrangement, each
existing bond faces an already bonded pair. A missing bond must first form;
that new bond can then catalyze the other missing bond. Geometry explains the
difference under one law. Register names provide no additional reward.

Without catalysis the corresponding two-binding probabilities are 1.7086%
and 1.7111%, nearly equal. Thus the large contrast is a geometry/kinetics
interaction, not just assigning two different names to a count.

These point preparations match the stated resource coordinates. This does
not claim every preparation in the atlas has equal ensemble free energy.
The two-binding event is one explicit structural coordinate of the native
law, not an adopted goal or a complete ordering of the arrangements.

## 3. Joint fuel constraints survive the branching count

At capacity 1, the next two events cannot both consume fuel to bind: after
the first such event the stock is zero. The calculated probability is exactly
zero for every state and lag. The two individual bindings may each be enabled
at the starting state; their apparent individual availability is not enough
to establish that ordered joint continuation.

This does not rule out later construction with intervening thermal reactions
or replenishment. For example, in the capacity-1 unbound catalytic case,
the probability that a first **thermal** binding supplies the catalyst for
a second fuel-consuming binding is 11.132% by time 1. No failed or blocked
branch was discarded, and no permanent exclusion is inferred from a two-event
constraint.

## 4. Early activity and later residual access can reverse

For the matched capacity-4 pair above, compare a fresh lag-1 window at later
cuts, averaging over the complete native state law at that cut:

| Cut | Adjacent: next two events bind with fuel | Opposite: next two events bind with fuel |
|---:|---:|---:|
| 0 | 34.683% | 9.842% |
| 1 | 0.644% | 3.731% |
| 5 | 0.0121% | 0.1017% |
| 20 | 0.0046% | 0.0069% |

By cut 1, mean fuel is .668 in the adjacent preparation and 1.409 in the
opposite preparation. The adjacent arrangement has already used more of its
fuel and filled more of its binding opportunities. That is not automatically
a harm: the earlier development remains in its history. Nor does the later
reversal erase the initial access advantage. Accumulated development and
remaining opportunities are genuinely different readouts of the same law.

## 5. What this says about a naive extent

There are three concrete limitations, alongside the successful mechanism
resolution:

**Support alone loses kinetics.** Each generator has one communicating class.
For every positive physical horizon, every state in that finite class has
positive probability from every starting state. Thus unrestricted state-support
size is simply 512 or 1,280. Even finite-jump state balls fail to distinguish
the matched two-bond preparations at the tested depths.

**Ordered channel counts are sensitive to route representation.** Catalytic
and uncatalyzed channels can reach the same state. They are physically
recorded separately here, so marked sequence counts retain that distinction.
At capacity 4/barrier 2, the four-bond preparation has more length-eight
channel sequences (1,126,532,272) than the adjacent two-bond preparation
(1,001,393,948), yet at binding 2 its mean number of events by time 1 is only
.3806 versus 1.9048. Raw sequences include reverse routes, repeated visits and
sequential interleavings. They are not independent physical dimensions.

**Summing native weights over individual prefixes collapses to activity.**
For length n, the probability masses of all first-n-jump prefixes completed
by T sum to P(N_T >= n). Therefore, including the empty prefix,

`sum_n sum_prefixes P(prefix completed by T) = 1 + E[N_T]`.

This identity holds even though the complete carrier contains richer
relations. The atlas records the finite-depth sum and its untruncated value;
it does not relabel that activity identity as possibility volume.

None of these observations requires gas to lose or justifies filtering noise.
They tell us which structural information each compression discards.

## Recommendation

Keep the exact residual atlas. It makes the next candidate inspectable:
native weights, legal combinations, timing and composition-enabled channels
are now present together in a computable object. The new-template witness and
the matched adjacent/opposite pair are useful controls for any proposed extent.

Next, take this **same short-continuation calculation back to sampled cuts of
the mobile lattice**, where the thermal comparison includes motion. A two-step
residual law only needs the native current events and their successor laws;
it does not require enumerating the full large state space. Compare it with
the existing ancestry count, retaining the full mix of forward, reverse,
switching and movement alternatives. No new physical mechanisms or preferred
winner are needed. A scalar lushness comparison is still not selected.

## Evidence and checks

- [Protocol](lattice_residual_protocol_v0.md).
The runner generates a local `lattice_residual_v0/` directory with the manifest,
all 224 cut and 672 residual profiles, the next-two-event decomposition, and
`g00` through `g07` containing every physical state, reaction channel and rate,
sparse generators, distributions, support counts and residual probability
arrays. Generated outputs are kept out of Git; the code, protocol and this
report provide the published reproduction path.

Four focused tests passed: native detailed balance and matched energies,
Poisson jump law with its full tail, channel multiplicity versus state support,
and shared-fuel exclusion. Probability mass errors were below 5.4e-14;
detailed-balance errors below 4.4e-19. An independent next-two-jump exponential
waiting-time calculation agrees with the augmented native generator within
5.4e-14, including the decomposition totals. Focused lint passed. Raw evidence
occupies about 22.7 MB locally.

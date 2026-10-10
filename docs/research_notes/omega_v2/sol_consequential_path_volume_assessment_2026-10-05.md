# Sol's Consequential Path Volume proposal: assessment

2026-10-05. User-supplied proposal, not an adopted lushness measure. No new
simulation or parameter sweep was requested or run for this assessment.

## Proposal retained

The proposed carrier consists of physically resolved histories with relations
and residual continuation attached. Each class has actual frame-conditioned
probability w_i. The extent is the Hill family:

    V_q = (sum_i w_i^q)^(1/(1-q));
    V_1 = exp(-sum_i w_i log w_i);
    V_infinity = 1/max_i w_i.

Retain profiles over physical frames, temporal/spatial resolution, horizons
and q, and compare log volumes with a specified thermal preparation. Noise,
failed histories and finite contributions remain represented. These are useful
features. Native dynamics first and existing physical models are sensible scope.

## Main obstruction: decorating a history is not measuring its geometry

For fixed physical dynamics, let Gamma be a complete resolved state history
and let R(Gamma) attach its residual kernels at the cuts. Whenever those kernels
are determined by that history, D=(Gamma,R(Gamma)) is an injective deterministic
recoding of Gamma. Each atom retains exactly its old weight, so

    V_q(D) = V_q(Gamma) for every q.

This follows immediately from the proposed sum, not a conjecture or a claim
that all entropy-based constructions must fail. Appending a large future
process to a class does not give that class any additional extent in this
formula. Two entirely different collections of residual processes with the
same list of class weights have identical Hill spectra.

For example, weights (.6,.3,.1) always give V_0=3, V_1=2.454555596,
V_2=2.173913043 and V_infinity=1.666666667, regardless of residual labels.
Replacing one class by a structurally richer class with the same weight is
invisible until the class partition or weights change. A probability-one
history has V_q=1 regardless of its internal deterministic development.

At a coarse resolution, a residual signature can split formerly lumped classes.
That can change the spectrum and be useful. But the partition must actually be
defined. If R is the future law conditioned on the same observed history, it
is already a function of that history and cannot split it. If R uses additional
hidden full-state information, state that it is supplied by the encompassing
description; it is not automatically information physically held by the frame.

This does not prove every full family of local Hill profiles must tie across
different wirings. Local distributions may differ. Nor must a legitimate
volume distinguish every pair of different structures. The specific claim
that attaching residual processes automatically makes the extent sensitive to
their geometry is what fails. The full-history case remains ordinary path
diversity, despite the richer annotation.

## Additional implementation and interpretation obligations

- Exact continuous jump times are nonatomic: an exact timed path typically has
  probability zero. Declare finite measurable timing/history cylinders before
  applying a discrete sum. Finite state count does not make continuous-time
  path space finite; replenishing cycles can make arbitrarily many jumps by a
  finite horizon. A density-based replacement needs a reference measure and
  units. Physical time resolution is therefore an actual specification.
- For an irreducible finite continuous-time chain, every entry of exp(Q*t) is
  positive at t>0. For a fixed initial state and m subsequent sampled cuts,
  full-state support can simply be |X|^m. That q=0 value is insensitive to
  catalytic speed. Floating-point zero thresholds must not invent forbidden
  paths. Projected frames change support counts but do not remove this issue.
- Higher q emphasizes high-probability atoms, not shock resistance, physical
  repair or long lifetime. Retaining q is a legitimate sensitivity profile;
  it does not derive the programme's probability weighting or settle arbitration.
- Selected one-time future marginals at a few lags do not necessarily determine
  joint future histories for a coarse frame. A coarse observation process need
  not be Markov. A finite signature should be described as such.
- A positive log-volume difference establishes greater effective path diversity
  in the declared partition. Calling it increased lushness is still the
  candidate hypothesis, not something established by the sign alone.
- Restoration of access need not increase path entropy. Making the next step
  more reliable can concentrate probability. Recovery should be represented in
  the same object, without stipulating that this entropy must rise.
- Full histories retain early events, but their scalar differences can still
  cross later. No additive common-tail result follows automatically.
- The thermal preparation must be physically specified and its preparation
  resource differences retained. Current 2D equilibrium includes assemblies.

## Recommended disposition

Keep the proposal as a path-diversity baseline and retain its full-history
carrier. Do not implement a large atlas expecting residual annotations alone
to supply a structural extent; the algebra already shows their limitation.

The next candidate must explicitly involve internal continuation geometry or
relations in its extent calculation. It should demonstrate, in a small common
apparatus, how a physically specified change in residual coupling can affect
the readout while a path-weight histogram stays fixed. This is a test of the
claimed measurement mechanism, not a demand that every rewiring changes volume
or a requirement that structure always beat thermal.

Existing similarity-sensitive effective-number mathematics is relevant as a
possible borrowing, not an adopted repair. Leinster–Cobbold explicitly combines
weights with a similarity matrix; ordinary Hill numbers are a special case.
The project would still have to derive any such relational input from physical
continuation, retain all histories, and justify its handling of jointness and
internal structure. Arbitrary similarity values or assigned catalyst rewards
would only relocate the problem.

Sources checked: [Leinster and Cobbold, author manuscript](https://webhomes.maths.ed.ac.uk/~tl/mdiss.pdf),
[Shannon, original paper](https://marco-dalai.unibs.it/teach/IT/shannon_1948.pdf).
Local precedents: [timing-volume collision](timing_volume_counterexample_report_v0.md),
[historical-volume application](active_thermal_volume_report_v0.md), and
[bounded frame aggregation](frame_aggregation_report_v0.md).

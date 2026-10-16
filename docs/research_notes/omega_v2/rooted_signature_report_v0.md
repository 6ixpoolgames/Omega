# Present-rooted continuation profile: results v0

## Result

There is now a working present-only measurement prototype. It starts from one
specified native configuration and computes a profile of the physical
developments generated from it. It uses no average over time cuts, no stationary
prior and no invented uncertainty about the present.

The profile distinguishes deterministic internal developments and stochastic
alternatives, preserves tested prefixes after reconvergence, and does not dilute
completed development when terminal waiting is extended. It responds to the
existing kinetic-gating and driven-ring examples. Pure encoding controls pass.

This establishes a workable measurement architecture under the present-only
requirement. It does not establish a canonical possibility volume or a lushness
ordering. The construction is a truncated signature-moment profile of resolved
physical paths; important omissions are recorded below.

## Construction

The [specification](rooted_signature_protocol_v0.md) gives the full choices.
Use a time-augmented physical path Y=(t,X), retaining ordered-integral signature
coordinates through degree three that end in a physical-change coordinate.
For example,

\[
S_i=\int dX_i,\qquad S_{ij}=\int_{u<v}dX_i(u)dX_j(v),\qquad
S_{ti}=\int t\,dX_i(t).
\]

These record net change, order/composition, and timing. They are not event
counts. The full tensor entries retain physical coordinate roles and signed
orientation. Word degree is order of combination, not physical dimension.

Condition on the exact present x and compute

\[
m=\mathbb E_x[S],\qquad M=\mathbb E_x[SS^T],\qquad
C=M-mm^T.
\]

M remains nontrivial for a deterministic development with a nonzero signature.
C describes variation among the selected signatures of possible developments.
Neither covariance alone nor a normalized rank is used as the extent.

Native probabilities enter the expectations once. The clock supplies timing,
not a distribution over past cuts. No result is divided by elapsed horizon.
Different clock grades have different units and are kept separate.

The mathematics is borrowed from [Chevyrev and Kormilitzin's signature primer](https://arxiv.org/abs/1603.03788).
Chen concatenation permits exact propagation of the truncated moments by native
state, without materializing the exponentially growing history tree. Sharing a
residual computation does not erase the contributions of different prefixes.

## Exact present, nontrivial future

The known-root fair bit starts certainly at 0. At horizon six, its first physical
coordinate has mean 0.5, second moment 0.5, and variance 0.25. Thus its stochastic
future is visible even though the initial law is a point mass. Old present-only
B returned one for this case regardless of the branching.

Deterministic parallel, chain and fork/join devices each change three registers
and end at 111. Their first-order net-change vectors agree. Their second-order
ordered tensors differ. For compact illustration, the following table gives
the trace of the purely physical degree-two block of M, at horizon six:

| Development | Second-moment trace | Covariance trace |
|---|---:|---:|
| Static | 0 | 0 |
| Three parallel changes | 2.25 | 0 |
| Dependency chain | 3.75 | 0 |
| Two changes jointly enabling a third | 3.25 | 0 |

All three active cases have exactly one history. Their zero covariance is
appropriate; their nonzero, differing ordered-development tensors remain.
The displayed traces depend on the declared coordinate geometry and are not
lushness scores. In particular, the chain's larger trace is not a finding that
chains are better than parallel activity.

## Waiting, delay and reconvergence

Extending the horizon from six to twelve after the parallel, chain, fork/join,
reconvergent and single-corridor systems have terminated leaves all their
retained m, M and C entries unchanged, with zero computed discrepancy.

There is also an algebraic reason: a pure-time suffix can only append time
letters under Chen concatenation. It cannot change a coordinate whose final
letter is a physical change. This is a property of the chosen change-ending
profile, not a claim that every physical form of waiting is inconsequential.
If aging, reactions, resource losses or downstream responses occur, those are
physical changes and belong in the resolved dynamics.

A delay before a change remains visible. For otherwise identical output bits
that switch at tick one versus tick two, S_i=1 in both cases while S_ti=1 versus
2. The clock/timer is retained in the native model; this comparison explicitly
uses the common output-bit view rather than pretending that view is Markov.

Two branches that reconverge and one deterministic corridor both have a
degree-two second-moment trace of 2.5. Their covariance traces are 0.5 and 0.
The full profiles therefore distinguish them, even though this one scalar
summary ties. At the absorbing endpoint the differing prefixes remain in the
profile rooted at the original cut. Evaluating anew from that endpoint would
ask a different, residual question.

## Joint structure, kinetics and circulation

Independent fair bits and two bits driven by a shared native coin have the same
single-bit means and variances. At horizon six both means are (0.5,0.5) and both
individual variances are 0.25. Their cross covariance is 0 versus 0.25. The
joint physical law enters the calculation; separate marginal profiles would
miss that difference.

The gated and ungated devices retain the same uniform equilibrium, while the
gate accelerates both directions of one conditional flip. At horizon six:

| Case | Physical degree-two M trace | Physical degree-two C trace |
|---|---:|---:|
| Gate off | 0.314506 | 0.247373 |
| Gate on | 0.521864 | 0.413813 |
| Reversible ring | 1.578240 | 1.300498 |
| Driven ring | 3.436893 | 0.975149 |

The ring pair has equal expected move count. Its differing signature moments
therefore do more than return that count. Driving raises the displayed M trace
while lowering C: systematic ordered development and variation among futures
are different aspects. No coefficient combines these into a preferred verdict.

Shared/local resource cases were also computed in full and common chemistry
views. Unlike the previous run's left/right mixture, the local cases now have
one exact left-location root. These results must not be presented as a numerical
continuation of that earlier initial distribution or as an established
fast-transport theorem.

Binary noise remains in all calculations. These logical devices are not a
matched thermodynamic gas/chemistry comparison, and the table does not establish
a defeat of gas.

## An explicit finite-resolution failure

Consider one output bit that changes from zero to one at time J. Compare:

| Law | Possible times | Probabilities |
|---|---|---|
| Even-index support | 1,3,5 | 1/16,10/16,5/16 |
| Odd-index support | 2,4,6 | 5/16,10/16,1/16 |

Their time moments through order four agree despite disjoint hitting-time
supports. With degree-three signatures, m and M in the output-bit view agree
to 7.11e-15. This is a genuine blind spot of the truncation, not equivalent
continuation or redundant description.

The same defined construction at degree four separates them: the maximum M
and C entry difference is 4.375. No metric, probability or coefficient changed.
Increasing tensor order is a systematic refinement available for this readout;
it does not imply that any finite order captures the complete law.

## Representation and numerical checks

- Splitting each gate outcome into two half-weight encodings of the same
  physical outcome changes moments by at most 1.12e-16.
- Consistent register relabeling agrees after the corresponding tensor
  permutation to 1.12e-16.
- Redundant alias encoding, with the physical feature map preserved: exact tie.
- Collinear subdivision of the same lifted path obeys Chen concatenation in
  analytic tests. Reordering genuine physical changes is not such a subdivision.
- Native endpoint laws from the moment propagation agree with direct matrix
  propagation within 3.34e-16; maximum total mass error is 1.12e-15.
- Nineteen focused tests pass, including explicit small-history enumeration
  against the dynamic program. Focused lint checks pass.

The run took approximately 0.45 seconds for 108 degree-three profiles across 24
device variants / 27 views and four horizons, plus two degree-four refinement
checks. No trajectory sampling or probability cutoff was used. Tiny negative
covariance eigenvalues from roundoff, down to -7.22e-13, are retained rather than
clipped or interpreted as negative variation.

Run from the repository:

```text
python -m omega_v2.validation.rooted_signature_v0
```

Numerical tensors, kernels and source snapshots occupy approximately 1.9 MB in
the ignored local `rooted_signature_v0/` output directory. Code, specification
and this written report are separate from those raw outputs. Nothing was pushed.

## What is and is not fixed

The present-only boundary now works operationally: a known present generates a
nontrivial profile of future organization and alternatives. There is no return
to time-averaged occupancy.

Remaining limitations are substantive:

- The physical feature map and jump lift are choices. A straight jump lift
  does not assert that fractional register values are physically accessible.
- Finite order and moments are lossy, as the timing collision demonstrates.
- The signature describes resolved changes. Translation-equivalent paths and
  static configurations can tie; the full root remains in the carrier but is
  not fully measured by this change profile.
- State-path signatures can miss different physical channels with the same
  state path. Retaining reaction marks in the carrier does not automatically
  put them into this readout.
- Traces/spectra depend on coordinate units and do not select a canonical
  volume or ethical order. Higher signature order is not a new physical
  dimension. This remains a classical prototype, with no interference model.

The useful next question is whether physically equivalent descriptions and
different physically resolved channel structures can be handled consistently
by the observable/lift construction. Keep the full profile and its refinement
hierarchy while examining that question. Do not promote a favorable trace into
lushness or hide the declared blind spots.

# Present-rooted development signature: exploratory specification v0

**Representation update:** the native joint-continuation reference is now
specified in [native_joint_continuation_protocol_v0.md](native_joint_continuation_protocol_v0.md).
It reads actual local configurations directly from the exact present and native
law. This signature construction remains an optional compression benchmark;
its coordinate embedding and jump lift are not the primary physical carrier.

The user requires present-only to work and rejects time averaging as a solution.
This candidate conditions on one exact physical root in each native logical
model. The sole probabilistic weighting is the law of subsequent developments.
No stationary distribution, unknown-input prior, or average over cuts is used.
This is an exploratory version, not a mandatory freeze or an adopted lushness.

## What changes

B treated a whole known present as one point and only compared possible present
states. This construction calculates ordered physical development *from* that
point. Its representation is a path signature: iterated integrals of the clock
and declared physical coordinates. Deterministic development can have a nonzero
signature; alternatives induce a native distribution of signatures.

For a physical coordinate path X, append the elapsed-time coordinate Y=(t,X).
For a word w=(i_1,...,i_k),

    S_w = integral_(u_1<...<u_k) dY_i1(u_1)...dY_ik(u_k).

Examples: S_i is net change; S_(i,j) records ordered composition; S_(time,i)
weights a change by when it occurs. Signed entries are orientations, not signs
of value or harm. Retain all nonempty words through degree three ending in a
physical-change coordinate. Words ending in time remain available internally
for composition but are excluded from the reported change-ending profile.

This is an explicit choice of a development profile. It omits the bare duration
of unchanging configurations; it is not proven to be all physical extent.

## Probability and internal organization

From the native root-conditioned law P_x compute

    m = E_x[S],    M = E_x[S S^T],    C = M - m m^T.

M combines deterministic development and random alternatives without a fitted
coefficient. C identifies variation of the selected signature coordinates among
alternatives. Neither C alone nor normalized effective rank is proposed as
extent: both would reintroduce the deterministic singleton failure.

The full typed tensors are retained. For compact inspection, report diagonal
blocks grouped by word length and number of clock letters, with their traces
and spectra. Different clock counts have different physical units; do not add
them into a scalar. Even within a block, a Euclidean trace assumes the declared
coordinate units; this does not derive a canonical physical metric or volume.

## Physical adapter and jump lift

Use the existing eighteen discrete-clock logical devices, not new chemistry.
Binary coordinates are actual resolved register values. A single categorical
position uses one-hot coordinates, so numeric names are not treated as physical
distances. Injective alias encodings reuse the original physical coordinates.
For resource views, retain native token location in the dynamics even when the
readout observes only free/bound-A/bound-B.

Every case has one exact initial root. In particular, local-resource models
start with the token on the left, rather than using the earlier left/right
mixture. Comparisons with the preceding B run must acknowledge this change.

Each tick advances time at the old configuration, then applies the complete
physical update at that time. The signature uses a straight jump lift for this
instantaneous change. This is established geometric-signature machinery, but
the interpolation is an additional representation choice: fractional register
values along that lift are not newly possible physical configurations. Native
event marks/read-write data remain in the model; this state-path readout does
not automatically consume every distinction between parallel reaction channels.

## Computation

Chen concatenation makes the new truncated signature a linear function of the
old signature (including its constant coordinate), conditional on a native
transition. Propagate unnormalized first and second moments by exact dynamic
programming over reachable native states. Histories that share a residual node
share computation, not identity. No history probabilities are pruned or
renormalized; no independent mean-field factorization is introduced.

Compute horizons 2,4,6,12 at degree three. These are exact finite-model moment
calculations in floating-point arithmetic. Retain native kernels and source
snapshots locally; no large raw outputs are to be committed.

## Checks and failure probes

- Known-root fair switch: future branching must enter C despite root mass one.
- Deterministic parallel/chain/fork-join: internal order enters the tensor,
  while C should be zero. No desired lushness ranking.
- Terminal waiting: for a fixed completed physical path, extending it with
  pure time leaves every retained word unchanged by Chen's identity. Delays
  inserted before changes should still affect mixed time/change words.
- Reconvergence versus a deterministic corridor: common endpoints do not
  identify the different signature laws of their prefixes.
- Shared versus independent native coins: same local marginals, different
  joint continuation. No invented prior over coin inputs.
- Pure encoding: relabeling permutes tensor coordinates; a redundant alias or
  splitting a physical outcome into two half-weight copies changes no readout.
- Collinear subdivision: dividing the same lifted segment into pieces leaves
  the signature unchanged. Splitting a simultaneous update into ordered
  different-coordinate changes is a different path and need not be invariant.
- Reversible gating, resources and circulation: retain all profile effects,
  including signs and reversals; the candidate need not award a winner.
- Finite-resolution collision: a single output jump at times (1,3,5) with
  probabilities (1,10,5)/16 versus times (2,4,6) with probabilities (5,10,1)/16.
  Their time moments through order four agree. Degree-three m,M therefore tie
  in the declared output-bit view despite disjoint hitting-time supports.
  Degree four is expected to separate them. This is a registered limitation
  of the truncation, not permission to declare the lower-degree tie harmless.

## Borrowed mathematics and limits

[Chevyrev and Kormilitzin, A Primer on the Signature Method](https://arxiv.org/abs/1603.03788)
supplies iterated-integral signatures, Chen concatenation, and time augmentation.
The terminal-wait claim follows by restricting to words ending in physical
change: the appended pure-time segment cannot supply a nonempty such suffix.

Finite degree and first/second moments are lossy projections. Even if those
limits are progressively refined, adequacy as lushness is not established.
The original physical coordinates, relative clock unit, frame and jump lift
remain assumptions to inspect. Translation invariance also means that paths
with the same coordinate increments can tie despite different initial states;
the root remains in the carrier and is not claimed to be encoded by S alone.
Static structure without resolved change can be invisible. This is a test of
present-rooted measurement architecture, not a theorem selecting possibility
volume, a quantum port, or a thermodynamic defeat of gas.

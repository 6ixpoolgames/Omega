# Bounded continuation attempt v0: result

2026-10-08. Exact small finite-adapter audit; no new physics, gas comparison,
universal quantum extent, commit, or push. Protocol was written before execution.
Raw results remain ignored in results/local_runs/bounded_continuation_v0/results.json.

## Verdict

The proposed lower/classical-upper bounds can be realized by established quantum
information mathematics, without adjustable interpolation coefficients. The
candidate works as an ensemble- and region-relative distinguishability readout.
It still fails as intrinsic complete-future extent because it needs a physically
justified alternative family and retained algebra/region. The bounds constrain
the answer but do not select its physical bearer.

The actual new constructive result is a checked classical history-record
certificate and extension rule on the existing native recording circuits. The
candidate equals 2,4,8 for successive fair recorded developments; no fixed initial
Hilbert-dimension/reference-mass ceiling is imposed. This validates a restricted
classical anchor, not a full automatic native-algebra construction.

## Formula and what it means

For weights p_h and normalized conditional record/continuation states rho_h,

    rho_bar = sum_h p_h rho_h,
    chi = S(rho_bar) - sum_h p_h S(rho_h),
    B_chi = exp(chi).

The standard Holevo bounds give

    0 <= chi <= H(p),     1 <= B_chi <= exp H(p).

This distinguishes information about the alternative h from uncertainty within
each conditional state. Identical conditional states yield one even if mixed;
orthogonal supports yield the classical bound even if internally mixed. Pure
conditional states reduce to the previous spectral mixture/Gram construction,
so this is not a newly discovered escape from that construction's failures.

The Holevo quantity bounds accessible classical information. B_chi is an
exponential information scale, not an exact one-shot distinguishable-outcome
count. It is not claimed a theorem-derived lower bound on an unknown Omega
extent. See [Roga, Fannes, Zyczkowski](https://arxiv.org/abs/1004.4782).

For equal binary weights and pure conditional-state overlap c, the eigenvalues
are (1+|c|)/2 and (1-|c|)/2. Results:

| Overlap | B_chi |
|---|---:|
| 1 | 1 |
| 1/sqrt(2) | 1.516637223 |
| 1/2 | 1.754765351 |
| 0 | 2 |

Unequal priors .1,.5,.9 were checked against the analytic eigenvalues
(1 +/- sqrt(1-4p(1-p)(1-c^2)))/2.

## Native physical record extension

The existing adapter is one particle qubit and one fresh initially blank memory
per balanced hop, coupled by actual CNOT recording interactions. For n=1,2,3:

| Recorded hops | Classical complete-history breadth | B_chi in all memories | exp S(actual joint memory state) |
|---|---:|---:|---:|
| 1 | 2 | 2 | 2 |
| 2 | 4 | 4 | 2 |
| 3 | 8 | 8 | 2 |

The distinction is important: rho_bar is a history-conditioned ensemble average,
not necessarily the actual coherent reduced memory state. At n=2,3 they differ
by .25 and .125 in maximum entry, respectively. Agreement of those two matrices
is not the admission criterion for a physical classical history family.

Instead, for each actual joint memory record cell R_h, the exact certificate

    R_h psi_final = C_h psi_root

passes with zero residual. Descendant record projectors sum to the dynamically
transported parent projector, with maximum error 2.22e-16. These are actual
register records from the supplied coupling schedule, not newly inserted readers.

The general-purpose certificate only checks orthogonal exhaustive projectors
and their correlation with histories. It does not infer native physicality:
arbitrary abstract branch projectors could also pass. The native register
interactions supply the additional evidence in this specific adapter.

## Eraser: local record information versus the whole conditional system

24 mode/leakage profiles reuse the six existing eraser treatments and leakage
angles 0,pi/6,pi/4,pi/2. We ask specifically about the two source-path alternatives
with weights .5,.5. Their conditional states are propagated through the actual
marking, leakage, and reversal operations. The subsequent common signal operation
does not change whole-system distinguishability or marker/environment marginals.

| Treatment | B_chi in marker+environment |
|---|---:|
| No mark | 1 |
| Retain mark | 2 |
| Conditional eraser, early or delayed | 2 |
| Undo marker, no leakage | 1 |
| Undo marker, leakage pi/6 | 1.278612322 |
| Undo marker, leakage pi/4 | 1.516637223 |
| Undo marker, complete leakage | 2 |
| Undo both marker and leakage | 1 |

Conditional erasure rotates the marker encoding; it does not eliminate optimal
path distinguishability. Erasing the marker alone leaves leaked information in
the environment. In contrast, joint reversal removes it from the record region.

On the whole conditional system, B_chi remains two in every treatment, because
the two conditional source inputs are orthogonal and undergo a common unitary.
Thus the successful local 1-to-2-to-1 behavior does not imply universal extent
does the same. The full unconditioned state remains pure throughout; the two
conditional inputs are a derived ensemble, not two incoherent universes substituted
for that state.

## The decisive unchanged-physics failure

The existing delayed-record echo makes a balanced hop, reverses it coherently,
and only then records the endpoint. No midpoint measurement occurs.

| History description | B_chi in memory | Classical diagonal bound | Record certificate |
|---|---:|---:|---|
| Endpoint only | 1 | 1 | Pass |
| Mathematical midpoint site cut plus endpoint | 2 | 4 | Fail |
| Refined amplitudes coherently grouped by actual record | 1 | 1 | Pass |

All descriptions obey the proposed numerical bounds. The bad family still
manufactures a different ensemble and hence changes the bounded readout. Its
proposed memory projectors repeat for distinct fine histories and are not an
exclusive exhaustive history-record family; maximum certificate residual is one.
The ensemble average differs from the actual memory state by .5.

Coherent regrouping by the already present physical record recovers the correct
record readout. That is an explicit narrower projection, not a proof that all
unrecorded intervening development has zero or one unit of full quantum extent.

## Other checks and numerical status

- Identical mixed states diag(.7,.3) give B=1 despite positive output entropy.
- Orthogonal mixed supports at priors .3,.7 give B=1.842022775=exp H(.3,.7).
- A common independent mixed ancilla leaves the fixed-label readout unchanged.
- Independent product ensembles multiply B.
- Common coordinate changes, relabeling, and splitting one conditional state
  into duplicate labels preserve B.
- Eight focused tests and Ruff pass. Maximum listed representation/product
  control error is 5.78e-15. Bounds were checked without clipping outputs into
  range; deviations of order 1e-15 are floating-point residuals.

No post-run change to the candidate, physics, or decision rule was made.

## Consequence for the programme

The limits are mutually compatible and support a useful physical diagnostic.
They do not uniquely identify lushness. For fixed h, B_chi only measures the
distinction between those alternatives visible in the retained states. Additional
future innovations common to all h are not counted unless the development family
is extended to include them. In a classical noisy record channel B_chi can also
be below complete-history perplexity. This confirms its narrower meaning.

Do not turn it into a universal definition by maximizing over invented readers,
by imposing the source/record partition on every system, or by treating a failed
record certificate as extent one. Preserve the native coherent process; use this
readout only where its alternative family and physical region are declared.

The next missing construction remains a native development algebra/equivalence
rule retaining unrecorded coherent development and physical chronology. The
record-correlation and prefix-refinement checks now provide concrete classical
constraints on that construction. A larger entropy sweep is not warranted.

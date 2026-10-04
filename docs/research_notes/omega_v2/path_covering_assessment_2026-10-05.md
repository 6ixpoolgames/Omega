# What the trajectory-covering run establishes

2026-10-05. User authorized the run and continuation. The definition was kept
unchanged: native probabilities, physically located frames, integrated state
mismatch, probability-depth and distance-resolution profiles. No chemistry
parameters or noise weights were changed.

## Evidence

- [Main protocol](path_covering_protocol_v0.md).
- [Main results](path_covering_report_v0.md):756 finite observed-law coordinates,
  97 complete finite-support coordinates,12 empirical continuous-time fits.
- [Matched-preparation coupling check](path_covering_coupling_check_v0.md):216
  additional finite observed-law coordinates.
- [Admissible-center check](path_covering_center_check_v0.md):analytical and fresh
  Monte Carlo calibration of the continuous-time fitting method.

All1,069 finite coordinates have certified minimum codebook sizes (exhaustive
enumeration, disjoint-ball sorting, or MILP). This concerns the declared finite
law, not all continuous paths. The continuous work generated24,960 native
binary CTMC histories containing92,086 jumps, retaining every sampled path.
The initial run took2.84seconds with6workers; the matched-preparation follow-up
took.70seconds. Five focused tests and lint passed. Evidence occupies about9MB.

## Findings

1. **Temporal structure reaches the arithmetic.** At T1, fractional tolerance.25
   and alpha.90, stationary switching rates .05/1/10 require2/3/4 representatives
   in the four-observation law, despite identical one-time marginals. The
   occupancy-collapse objection no longer applies to this quantity.

2. **Independent noise increases the same coordinate.** Adding a fast, decoupled
   binary fluctuation to a static fair source raises whole-frame cover2->4.
   This is a real consequence of the native law. It is neither grounds for
   deleting noise nor a demonstrated thermal defeat of a lushness candidate.

3. **Reliability and diversity separate.** A finite scheduled construction with
   success probability.5 needs2 representatives at tolerance.25/alpha.90;
   success probabilities.9,.99,1 need1. Deterministic idle also needs1. Failure
   branches remain in the law; at alpha1 a positive failure branch is retained.
   This is a concentration effect, not an inference that successful construction
   harms the field or that failure improves it.

4. **Whole-state equality misses a consequential coupling.** The stronger
   follow-up uses identical independent-fair initial S,D in both apparatuses.
   One D relaxes toward S, the other toward0, with matched error-clock rates and
   event-count law. Whole-frame cover ties at all36 coordinates. Yet I(S;D)
   grows from0 to.227107bits byT1 in the coupled process and stays0 in the other.
   The destination-frame covers differ at11of36 coordinates; source covers tie.
   A full-state bijection preserves mismatch geometry but not the physical
   subsystem relations. The full frame profile has not failed this contrast.

5. **Finite prefixes survive absolute tolerance.** Two histories differing for
   .5 time units still need2 representatives at absolute tolerance.4 as T grows
   1->2->4. At fractional tolerance.25 they go2->1->1. The common suffix has
   not erased the past; the tolerance increased in absolute units.

6. **Randomly sampled centers can badly misestimate covers.** For stationary
   rate10, tolerance.25, the37-center fitted cover contains90.6% of its64-path
   training sample but31.5% of2048 fresh histories (95% interval29.6–33.6%).
   This is not a population covering-number estimate. At tolerance.5 a direct
   physical center construction resolves part of the issue: constant0 and1
   cover every binary history. For rate.05, a single center switching atT/2
   covers97.5615% of the true stationary law, while the original restricted
   sample fit needed2 centers. Fresh sampling agrees. The approximation, not
   the candidate, caused that extra representative. Fast-process covering at
   tolerance.25 remains unresolved beyond the reported empirical results.

## Disposition

Keep the covering machinery: it is executable, physically weighted and sensitive
to temporal distributions. Do not promote whole-state covering count to lushness.
Its verified role is trajectory distinguishability at a declared resolution.
The reliable-construction and coupling cases locate the next issue in what the
distance regards as significant, not in missing probability normalization.

The physically located frame family already recovers a distinction lost by the
whole-frame number. Pursue that structural information before adding a fitted
distance coefficient or declaring that bigger covers must mean better access.
Neither summing frame counts nor voting across profile cells was adopted.
The work supports a bounded extent prototype; it does not establish a geometric
measure, a gas comparison in the chemistry, or an ethical ordering.

All results remain local. No commit or push was requested for this run.

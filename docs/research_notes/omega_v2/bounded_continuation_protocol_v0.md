# Bounded continuation attempt v0: protocol

2026-10-08. Written before execution. Reuse the existing finite quantum adapters;
no new physical dynamics, rewards, gas comparison, or claim of universal extent.

## Candidate and status

For a declared weighted ensemble of conditional continuation/record states
{p_h, rho_h}, test

    chi = S(sum_h p_h rho_h) - sum_h p_h S(rho_h),
    B_chi = exp(chi).

The Holevo quantity is established mathematics, with 0 <= chi <= H(p).
Identical conditional states give B=1; mutually orthogonal supports give exp H(p).
It is additive for independent product ensembles, hence B is multiplicative;
a common quantum channel cannot increase chi. No measurement optimization or
new observer action is inserted. The ensemble and retained physical region are
inputs, not claimed canonical. For pure conditional states this reduces to the
previous spectral mixture construction; its earlier failures must remain visible.

Reference: Roga, Fannes, Zyczkowski, https://arxiv.org/abs/1004.4782.
The exponent is an effective distinguishability scale, not a claim of exactly
exp(chi) outcomes distinguishable in one measurement.

## Fixed checks

1. Identical mixed conditional states: one despite nonzero output entropy.
2. Orthogonal mixed supports: classical perplexity despite internal mixedness.
3. Pure binary record overlap: analytic interpolation between one and two.
4. Independent common mixed ancilla: unchanged B; product ensembles multiply;
   coordinate covariance, relabeling, and splitting an identical conditional
   state into duplicate labels leave B unchanged.
5. Existing eraser, six modes and four leakage angles, fixed equal source-path
   weights supplied by its initial Hadamard. Compare information about that
   source alternative in M, E, ME, and the whole conditional system. This is a
   specific native channel query, not complete-future extent. Expect marker-only
   undo to leave leakage in E, conditional erasure to preserve ME information,
   and full reversal to remove path information from ME while full-system
   conditional inputs remain orthogonal.
6. One through three fresh physical records: complete-history ensembles,
   expected B=2^n in the joint memories. Check actual record correlation
   R_h psi_final = C_h psi_root and stable parent-to-descendant refinement.
7. Delayed-record echo: endpoint history family versus inserted mathematical
   middle site cut. Expected representation failure remains possible; no rule
   is allowed to remove it by hindsight. Compare coherent actual marginal with
   ensemble average, and coherently regroup histories to actual record labels.

An algebraic record-correlation/refinement certificate does not establish that
an arbitrary projector family is physically selected. In retained-record toys
the register couplings provide explicit provenance. No universal extraction
algorithm is claimed. Neither marginal agreement nor the Holevo bounds suffice
to establish a physical classical history ensemble.

## Decision rule

Reject as an intrinsic full extent if changing only a history description changes
B, or if the chosen retained region is indispensable but unspecified. Retain a
bounded physical record-distinguishability readout if its proper narrower claims
pass. Save raw data only to ignored results/local_runs/bounded_continuation_v0.

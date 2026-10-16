# Coherent reference extent v0: protocol

2026-10-08. Written before numerical execution. Analytical limitations below are known in advance. Purpose: test one full-matrix reference construction, not rescan bare spectral entropy or select a winner.

Use the existing two-site particle/detector physics, exact initial L,0 and the same 24 profiles from spatial_futuresfield_v0. No physical modification or fitted coefficient.

Actual history kernel D is built from rho. Define one explicit reference R=I_position tensor |0><0|_detector: one unit per initial physical position, conditional on the same blank detector resource. Propagate it through the same history maps:

M_ab=Tr(C_a R C_b-dagger).

This is independent of which actual particle state is chosen within that reference sector, but depends on the native law and history query. It is a proposed pushforward of initial volume, not an independently justified measure of newly generated developments. The pure detector restriction is declared, not automatically derived. Compare the unrestricted I_position tensor I_detector reference as a separate ambient-reference diagnostic; do not silently substitute it.

Candidate:

V_M(D)=exp[-Tr D(log D-log M)], Tr D=1, supp D subset supp M.

For diagonal D=p and M=m, this is exp[-sum p log(p/m)]. With M=I_history it is the already-tested spectral entropy, retained only as a control. The new candidate is the law-generated M. Its algebra is quantum relative entropy against a positive unnormalized reference, not an assumption that logD-logM equals log(D M-inverse).

Anticipated properties: positive finite output on common support; product multiplicativity for independent D,M; passive unitary covariance; coherent grouping of both kernels exact; blank ancilla unchanged when its reference remains the same blank. Scaling M by c scales V by c. No arbitrary trace normalization or signed-weight repair.

Anticipated obstruction: exhaustive projective histories preserve Tr M=Tr R=2. Set sigma=M/2; V=2 exp[-S(D||sigma)]<=2. Since rho<=R, also D<=M, giving V>=1 here. The construction is potentially a reference distinguishability readout, not an expanding complete-future volume. Test explicit classical calibration before promotion.

Extra fixed benchmark: 1,2,3,4 balanced hops, each recorded into a distinct initially blank local detector at R. Histories are genuinely decoherent: ordinary complete-history perplexity should be 2^n, while this reference construction cannot exceed2. More blank detectors are physical resources, but receive no extra occupied initial reference volume under the declared resource-conditioned ruler. No assertion of energy-free recording or universal growth follows.

Representation controls: transform state/reference/law/projectors together; propagate an inert blank; identity checkpoint; subdivide unitary without resolving another site cut; refine a site cut then coherently regroup both D and M. Also report fine-query versus coarse-query values without asserting these are identical questions. Independent product test includes the complex phase fixture that broke the prior real-allocation candidate.

Additional scalar probes: endpoint-only and completely unresolved history queries for the same evolution; unrestricted detector reference; synthetic diagonal p,m calibration and singular-support rejection. Publish small protocol/report/source; raw output ignored locally. No push requested.

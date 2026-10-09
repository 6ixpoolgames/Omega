# Coherent reference extent v0: result

2026-10-08. Exact exploratory run; 24 unchanged spatial profiles, four recorded-growth cases, and representation/composition controls. No gas comparison, parameter fitting, scalar adoption or push.

## Main finding

Using the full complex history matrix fixes the negative-probability and independent-composition failures of the previous real allocation. However, the particular reference proposed here is a propagated initial-volume measure. Its conserved total volume prevents it from reproducing growing classical complete-future breadth. Reject this reference as the general continuation extent ruler; keep the relative-entropy calculation as an explicitly reference-dependent diagnostic.

This is not a failure of Born normalization. Classical branching probabilities stay normalized while their effective number grows. The artificial cap comes from the chosen reference volume, not the physical law.

## Construction

The physical substrate and query are unchanged from spatial_futuresfield_report_v0.md: one particle on two adjacent sites, an explicitly included detector initially blank, two hopping windows with an intervening local detector/phase pulse, and site histories at two specified cuts. These are ideal scheduled unitaries, not an autonomous energy-accounted detector model. They retain the full particle/detector state while resolving only particle site history.

Use the actual root rho=|L,0><L,0|. A common reference across particle preparations is

\[
R=I_{\mathrm{site}}\otimes |0\rangle\langle0|_{\mathrm{detector}},\qquad \operatorname{Tr}R=2.
\]

It assigns one initial volume unit to each site while holding the prepared detector resource fixed. This is a declared reference choice, not a theorem selecting the physically universal ruler.

For the same class operators, propagate both source operators:

\[
D_{ab}=\operatorname{Tr}(C_a\rho C_b^\dagger),\qquad
M_{ab}=\operatorname{Tr}(C_aR C_b^\dagger).
\]

Then evaluate

\[
V_M(D)=\exp\{-\operatorname{Tr}[D(\log D-\log M)]\}.
\]

The actual D has trace one in the exhaustive projective families used here; M is deliberately not normalized. Support must satisfy supp D subset supp M. No entrywise log, inverse-product log, dropped imaginary part, signed clipping or trace repair is used. The scalar is based on standard quantum relative entropy; see [Wilde, From Classical to Quantum Shannon Theory](https://arxiv.org/abs/1106.1445). Our interpretation as candidate volume and reference R are additional hypotheses.

For diagonal D=p and M=m this recovers exp[-sum p log(p/m)]. For M=I_history it becomes the old spectral-history entropy; that special case is printed as a control, not promoted again. Independent products give multiplicative V when both D and M are tensor products. Multiplying M by c multiplies V by c, exposing the reference units.

## Exact cap: the reference transports initial volume

Exhaustiveness yields sum_a C_a-dagger C_a=I and therefore

\[
\operatorname{Tr}M=\operatorname{Tr}R=2
\]

at every tested horizon, even if the number of histories grows. Set sigma=M/2. Then

\[
V_M(D)=2\exp[-S(D\Vert\sigma)]\le2.
\]

Also rho<=R implies D<=M. Operator monotonicity of the logarithm on the supported subspace gives V>=1 for this setup. These bounds were derived before execution; the numerical run checks their relevance to the concrete physical cases.

The meaning is now explicit: the candidate is the fixed reference mass multiplied by a factor measuring closeness to a reference history state. It does not give every newly resolved classical development one additional extent unit.

## Recorded-growth benchmark

After each balanced hop, a fresh detector at R records the particle site. All detector qubits start blank and are retained in the full quantum state. The resulting site histories are genuinely decoherent, and all 2^n histories have weight 2^-n. The reference keeps initial source volume two and conditions on those same blank detector resources.

| Recorded hops | Classical complete-history perplexity | Candidate V_M | Reference mass |
|---:|---:|---:|---:|
| 1 | 2 | 2 | 2 |
| 2 | 4 | 2 | 2 |
| 3 | 8 | 2 | 2 |
| 4 | 16 | 2 | 2 |

Here M=2D, so the cap is saturated exactly. Additional memories are explicit physical resources, not free environmental magic. This is a classical-limit calibration, not a claim about unbounded physical generativity or a thermodynamic advantage. Since the programme's classical candidate counts complete weighted developments, the failure is material even though the reference-relative entropy itself is mathematically correct.

## Spatial profiles

All 24 profiles yield valid nonnegative finite extents, including the cases that previously produced negative real allocations.

| Native development | Detector pulse | V_M | Spectral D control |
|---|---:|---:|---:|
| Idle | 0 | 1 | 1 |
| Balanced spread and hold | 0 | 2 | 2 |
| Balanced echo | 0 | 1 | 2 |
| Balanced echo | pi/4 | 1.516637 | 3.033274 |
| Balanced echo | pi/2 | 2 | 4 |
| Unequal pi/4,pi/6 hopping | 0 | 1.139754 | 2 |
| Unequal hopping | pi/2 | 2 | 3.509531 |

Adding a pi/2 site phase to the unequal-hopping case leaves these two matrix summaries unchanged in this panel. That is a reported tie, not evidence that the coherent processes or all their readouts are equivalent.

## Composition and reference controls

Use the complex phase fixture that broke the prior real-allocation product rule. Individual V_M=1.1397535285; independent pair=1.2990381057, equal to its square within 6.7e-16. The full D and M product laws also hold. The imaginary structure is retained throughout.

Passive transformations rotate state, source reference, law and projectors together. Maximum covariance error is 2.34e-15; blank ancilla, identity checkpoint, numerical subdivision, and coherent regrouping of refined histories preserve the appropriate original D and M within 1.2e-16. No uncontrolled normalization was applied.

The same physical evolution under different questions gives:

| History question | V_M |
|---|---:|
| Original two-cut site query | 1.139754 |
| Additional resolved site cut | 1.032815 |
| Endpoint only | 2 |
| Completely unresolved development | 2 |

Coherently regrouping both refined kernels recovers the original pair exactly. The scalar on the finer query is not equal to the original; it has not become an intrinsic description-independent volume merely because a reference matrix was included. A completely unresolved query yields D=[1], M=[2], hence V=2 for every root in this reference family. Loss of resolving power can maximize the readout. This further identifies its reference-distinguishability character.

An inert pure ancilla changes nothing when its reference is the same pure blank. Giving the existing detector unrestricted reference identity instead of its prepared blank doubles reference mass to4 and, for the chosen no-marker control, doubles V to2.279507. Excluding unused reference directions is a declared physical-resource condition; it is not automatic selection of a canonical measure.

## Mathematical interpretation and next requirement

The two latest failures are different:

1. Allocating quantum interference to additive real history weights loses positivity and independent composition.
2. Keeping the full positive matrix and propagating fixed initial reference volume fixes those algebraic failures, but caps the extent before any new branching occurs.

Neither failure implies that the coherent futuresfield lacks an extent. They show that an acceptable reference needs an explicit extension rule for development through time. It cannot merely be the pushforward of a fixed finite initial mass if it must recover unit-cell classical history breadth as new developments accrue.

This also does not justify multiplying the answer by a fitted horizon-dependent factor. A new reference must explain which physical distinctions receive new units, which changes are only numerical subdivision, how coherent composition works, and how it reduces to counting volume at the declared classical resolution. Full D and M covariance alone is insufficient.

The next mathematical task is therefore the reference extension law, before another physics sweep. The present code supplies a reusable support-aware full-matrix calculation against which such a law can be evaluated. No new optimality, gas-defeat, value or block-Everett claim follows.

## Reproduction and checks

Source: omega_v2/finite/coherent_reference.py. Runner: python -m omega_v2.validation.coherent_reference_v0 from Omega using its .venv. Seven targeted tests passed; Ruff passed. Checks cover diagonal reference recovery, singular-support refusal, trace refusal, complex product/covariance, recorded growth and the signed-failure fixture. Small eigenvalues below1e-12 are treated as numerical null directions; no statistical estimation is involved.

Raw JSON is retained only under ignored results/local_runs/coherent_reference_v0/results.json. Protocol was written before the run; no panel changes were needed. Nothing was committed or pushed.

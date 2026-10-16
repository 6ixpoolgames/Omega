# Spatial futuresfield reference probe v0: results

2026-10-08. Completed exploratory exact calculation. This tests one explicit extension of classical weighted volume, not quantum lushness in general.

## Result

A physical spatial reference removes the arbitrary-axis choice for this query, but the attempted interference-adjusted cell weights are not probabilities. Three of 24 predeclared profiles have significant negative weights. A stronger independent-composition test finds nonnegative single-system weights can become negative for the independent pair. Reject ordinary perplexity of this allocation as a general coherent extent. Retain the native coherent field and its history kernel.

No physical criterion required organized states, records, spreading or coherence to win. No gas comparison or value claim was made.

## Physics and ruler

One particle on neighboring sites L,R, with H=J X in its one-particle sector. Two fixed-duration hopping windows have integrated actions theta1 and theta2. A detector initially in 0 at site R undergoes a conditional Y rotation of action phi between windows; its two conditional states have overlap cos(phi). An optional phase pulse acts at R. These are exactly specified externally scheduled local unitaries. The ideal detector pulse is not a thermodynamic model of measurement, and an autonomous clock/controller has not been included.

The full pure state of particle and detector evolves unitarily in dimension four. A site-history query resolves particle position after each window and retains the detector in all branch vectors; it does not resolve the detector's whole trajectory. Thus the candidate is a two-time spatial frame profile, not a claim to full-universe extent. Its failure already in this frame is sufficient to reject the general allocation rule. One unit of reference volume is assigned to each resolved site history. An inert ancillary control extends the Hilbert space without altering this query.

## Derivation of the attempted weight

Let v_alpha be a branch amplitude vector and D_ab=<v_b|v_a>. Set

\[
z_\alpha=\sum_\beta D_{\alpha\beta},\qquad
q_\alpha=\operatorname{Re}z_\alpha.
\]

This shares the total pair interference 2 Re D_ab equally between its two histories. Exhaustiveness gives sum z=sum q=1. Coherent grouping commutes with summing z or q. For a medium-decoherent family q is the ordinary diagonal history probability. When q>=0 the attempted extent is exp[-sum q log q]; significant negative q makes it invalid. No signed value is clipped or repaired by renormalization. Sub-1e-12 numerical negative residues have zero entropy contribution, with original q retained in output.

For class operators with common final unitary U, z_alpha=Tr(U-dagger C_alpha rho). Thus it is an ordered-projector quasiprobability, and q its real part. This connects the calculation to established Kirkwood-Dirac/Margenau-Hill mathematics rather than supplying a new Born probability law. See [Lostaglio et al., statistics of incompatible observables](https://arxiv.org/abs/2206.11783) and [Arvidsson-Shukur et al., properties and applications of the KD distribution](https://arxiv.org/abs/2403.18899). The negativity below is derived directly for our model.

Crucially, for a set A,

\[
\sum_{\alpha\in A}q_\alpha
=\mu(A)+\operatorname{Re}D(A,A^c).
\]

It is not generally the physical quantum weight mu(A). A real additive allocation cannot simply inherit the nonadditive event arithmetic of quantum measure.

## Numerical profiles

There are six predeclared hopping/phase cases and four detector strengths. Representative values:

| Native development | Detector action | Allocated history extent | Final site breadth | Final site+detector breadth |
|---|---:|---:|---:|---:|
| Idle | 0 | 1 | 1 | 1 |
| Balanced spread, then hold | 0 | 2 | 2 | 2 |
| Balanced spread, then reversed hopping | 0 | 2 | 1 | 1 |
| Same reversed-hopping sequence | pi/4 | 3.033274 | 1.516637 | 2.300188 |
| Same reversed-hopping sequence | pi/2 | 4 | 2 | 4 |
| Unequal hopping pi/4 then pi/6 | 0 | invalid | 1.278612 | 1.278612 |
| Unequal hopping pi/4 then pi/6 | pi/2 | 3.509531 | 2 | 3.509531 |

The echo's 2 versus endpoint 1 does not establish history extent 2; it describes this candidate before its general failure. Endpoint breadth is explicitly a control. The fully recorded case is a valid classical calibration of this history family, not a universal preference for decoherence.

For unequal hopping without a phase pulse, in history order (L,L),(L,R),(R,L),(R,R):

\[
q=\frac18(3-\sqrt3\eta,\;1+\sqrt3\eta,\;1-\sqrt3\eta,\;3+\sqrt3\eta),
\qquad \eta=\cos\phi.
\]

With no detector interaction:

\[
q=(0.158494,\;0.341506,\;-0.091506,\;0.591506).
\]

The negative entry persists whenever eta>1/sqrt(3). It is -0.0625 at phi=pi/6 and -0.028093 at phi=pi/4. At phi=pi/2 the histories decohere and q=(.375,.125,.125,.375), giving classical breadth 3.509531. Nonnegative q can occur before full decoherence, so positivity alone is not evidence of durable classical records.

## Independent composition is a stronger failure

For independent systems the full kernel and complex weights compose exactly:

\[
D_{AB}=D_A\otimes D_B,\qquad z_{AB}=z_A\otimes z_B.
\]

But

\[
\operatorname{Re}(z_Az_B)
=\operatorname{Re}z_A\operatorname{Re}z_B
-\operatorname{Im}z_A\operatorname{Im}z_B.
\]

Consequently q_A and q_B discard information needed even for independent composition.

Take theta1=pi/4, theta2=pi/6, phi=0 and an intervening site phase pi/2. Each separate system has nonnegative q=(.375,.125,.125,.375), apparent extent 3.509531. Two independent copies have minimum q=-1/32 and total negative mass 1/8. The candidate is undefined for the pair, instead of giving the product 12.316806. The maximum discrepancy from q_A tensor q_B is 3/64=0.046875. This follows from the imaginary terms, not numerical error or a physical interaction between the copies.

The initial diagnostic run used a generic complex fixture whose individual q was already negative. After that run, the representative composition/covariance fixture was changed to the already-predeclared pi/2 phase case to demonstrate the stronger positive-individual/negative-product result. No physics panel or verdict threshold changed. This focused diagnostic selection is recorded here as post-run clarification.

## Checks and artifacts

All 24 profiles reproduce analytic Born probabilities. Largest normalization/amplitude/marginal error is 4.45e-16. Passive coordinate transformations, blank ancilla, identity checkpoint, splitting a propagator without resolving a new cut, and coherent recovery after adding a resolved cut all preserve the appropriate original D to less than 3e-16. Exact independent product D and complex z also agree to this precision.

The resolved-cut control compares the coherently coarse-grained kernel, not an assertion that all fine-resolution extent readouts must be identical. An actual extra measurement would change the physics.

Source: omega_v2/finite/spatial_futuresfield.py. Runner: omega_v2/validation/spatial_futuresfield_v0.py. Five new tests cover analytic sign threshold, classical record limit, covariance and product failure, refusal to repair probabilities, and Born/restriction identities. Ten focused tests including the existing quantum-history tests passed. Raw JSON remains ignored at results/local_runs/spatial_futuresfield_v0/results.json. No push.

## What this changes

The spatial ruler is now explicit at this finite resolution. It does not make coherent history weight behave like a positive density over those cells. We have narrowed the problem beyond arbitrary basis selection: even physically located alternatives at different times have interference that cannot be allocated this way and then processed with classical entropy.

Retain the full complex kernel and physical site/history reference. Do not take absolute values, fit a cell volume to cancel a negative sign, or reward records to ensure a preferred result. A positive cell volume cannot change the sign of q/m. The next candidate must use coherent composition directly, or explicitly restrict itself to physically justified classical frames. Bare spectral D entropy remains disqualified as a general intrinsic answer by earlier checkpoint tests; this result does not rehabilitate it.

This is a rejection of the particular additive allocation plus perplexity. It is not an impossibility theorem for quantum extent, nor a rejection of the universal-wavefunction/block-Everett object or the user's intended definition of lushness.

# Spatial futuresfield reference probe v0

2026-10-08. Exploratory protocol written before numerical execution. The signed-weight failure is analytically anticipated, not a blind prediction.

## Physics and reference

One particle on two neighboring physical sites L,R. In the one-particle sector the hopping Hamiltonian is H=J X, U(theta)=cos(theta)I-i sin(theta)X, theta=J Delta-t/hbar. Two hopping windows each last one declared time unit. Changing theta changes hopping action, not the number of numerical solver steps. Negative theta represents reversed hopping coupling. Initial particle L; one explicit detector qubit starts in 0 at R.

Between windows a local controlled detector rotation exp(-i phi Y) occurs only if the particle is at R. phi=0 has no coupling; phi=pi/2 leaves orthogonal detector records. It is an ideal local pulse with integrated action phi, not a modeled finite-duration, autonomous energy-conserving detector. Both windows and the pulse constitute the declared law. No gas or efficiency comparison is attempted. An optional local phase at R provides a complex-amplitude control.

The spatial observable is actual particle occupation, not an arbitrarily selected qubit axis. A coarse configuration cell has unit counting volume in this finite lattice adapter. The two-time reference uses one unit per site sequence (x1,x2). This supplies a clear, resolution-dependent reference, not a canonical quantum history volume. Timing, quantum coherence and the environment are retained in the native evolution; history projectors are mathematical resolutions, not inserted measurements.

## One explicit candidate

Let v_alpha=C_alpha psi, D_ab=<v_b|v_a>, and Omega be all histories. Try

q_alpha=Re D(alpha,Omega)=D_aa+sum_(b != a) Re D_ab.

This splits each total cross contribution 2 Re D_ab equally between a and b. It is additive, normalized, and coarse-grains by summing q. It reduces to the diagonal probability in a medium-decoherent family. It is the real part of an ordered-projector quasiprobability, not assumed to be positive.

Attempt V=exp[-sum q_alpha log(q_alpha/m_alpha)] with m_alpha=1 ONLY if all q are nonnegative (within stated floating-point tolerance). Negative values yield an explicit invalid result; no clipping, absolute values, or renormalization repair. Preserve the complex row sums and full D so this candidate does not replace the coherent carrier.

For a set A, q(A)=Re D(A,Omega)=mu(A)+Re D(A,A-complement), generally not mu(A). A signed allocation over cells is not a positive quantum event measure. This distinction is part of the test, not an omission to repair after a preferred ranking.

## Cases and controls

Fixed cases: idle; spread then hold; balanced spread and reversed hopping; balanced spread and further hopping; unequal hopping windows; optional pi/2 local phase. Marker phi=0,pi/6,pi/4,pi/2. All 24 profiles predeclared. Pure universal state throughout.

Analytical witness theta1=pi/4,theta2=pi/6, no local phase: q(R,L)=1/8-(sqrt(3)/8)cos(phi), negative when cos(phi)>1/sqrt(3). Do not require nonnegativity to imply decoherence.

Readouts: q and its imaginary counterpart, negative mass, candidate extent or invalid flag, original diagonal-history breadth as a control, one-time spatial breadth at both cuts, final joint site/detector breadth, interference size and exact amplitude reconstruction. Endpoints are controls, not substitutes for complete-future extent.

Checks: analytic Born law and witness; coherent coarse-graining to either cut; passive coordinate covariance transforming site projectors as well; inert blank ancilla; identity checkpoint; splitting a hopping propagator without adding a new resolved cut; independent-product D and q in real and complex cases. The candidate can fail independent multiplication because Re(z1 z2) need not equal Re(z1)Re(z2); retain and report that failure. A genuine additional resolved site cut is a changed resolution: coarsen back coherently before comparing.

No rank order is prescribed for idle, spreading, echo, records or loop activity. No simulation or parameter fitting can promote q to an extent if positivity fails. Results remain local under results/local_runs/spatial_futuresfield_v0; publish source and compact notes only.

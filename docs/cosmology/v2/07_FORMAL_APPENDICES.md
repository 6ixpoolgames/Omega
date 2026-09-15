# 07 — Formal Appendices

## A. Purpose and scope

Two models currently provide useful precision: a quantum construction for histories and perspectives, and a controlled transition model for continuation and recovery. Both borrow established mathematics. Their connection to valuerhood and phenomenality remains an additional task.

The formulas below do not derive quantum mechanics from awareness, derive morality from selection, or solve global optimization. They make a restricted realization of the framework explicit and identify where its open concepts would enter.

## B. A minimal quantum block

Take a finite-dimensional closed quantum model, including the relevant apparatus and environment:

$$
\mathcal Q=(\mathcal H,|\Psi_0\rangle,U),\qquad
\langle\Psi_0|\Psi_0\rangle=1,
$$

$$
U(t,s)U(s,r)=U(t,r),\qquad
i\hbar\partial_tU(t,s)=\widehat H(t)U(t,s).
$$

Here $\widehat H$ is the specified Hamiltonian. A mixed initial state can be used with traces. The model supplies a temporal/background structure; it is not a quantum-gravity construction.

The block interpretation treats the entire model as specified. Its time parameter locates internal relations. Nothing in these equations requires a universal present moving through them, and nothing in them proves that the block interpretation is uniquely correct.

### B.1 Multiway amplitudes

Insert orthonormal resolutions of identity between propagators $U_k=U(t_k,t_{k-1})$:

$$
\langle f|U_N\cdots U_1|i\rangle
=\sum_{z_1,\ldots,z_{N-1}}
\prod_{k=1}^{N}\langle z_k|U_k|z_{k-1}\rangle,
\quad z_0=i,\ z_N=f.
$$

This is a finite multiway representation with complex edge weights. Regrouping terms or inserting a genuine resolution of identity leaves the propagator unchanged. Thus valid refinement does not manufacture physical weight. Creating another actual physical channel changes the model and is a different operation.

### B.2 Histories and decoherence

Choose exhaustive orthogonal alternatives $P^{(k)}_a$ at selected times. In the Heisenberg picture, define

$$
P^{(k)}_a(t_k)=U(t_k,t_0)^\dagger P^{(k)}_aU(t_k,t_0),
\qquad
C_\alpha=P^{(n)}_{\alpha_n}(t_n)\cdots P^{(1)}_{\alpha_1}(t_1).
$$

For a set $B$ of histories,

$$
C_B=\sum_{\alpha\in B}C_\alpha,
\qquad |\Psi_B\rangle=C_B|\Psi_0\rangle,
\qquad w(B)=\|\Psi_B\|^2.
$$

The decoherence functional is

$$
D(\alpha,\beta)=\langle\Psi_\beta|\Psi_\alpha\rangle.
$$

For disjoint sets $B,C$,

$$
w(B\cup C)=w(B)+w(C)
+2\operatorname{Re}\langle\Psi_B|\Psi_C\rangle.
$$

Off-diagonal decoherence makes these weights additive on the chosen history family. Approximate decoherence requires an error assessment for the coarse events actually used; many individually small interference terms can accumulate. These class-operator constructions are borrowed from decoherent-histories quantum mechanics. [Hartle, *Decoherent Histories Quantum Mechanics Starting with Records of What Happens*](https://arxiv.org/abs/1608.04145)

### B.3 Records and situated conditioning

An ideal physical record at time $t$ is represented by a projector $R_p$. If $w_p=\|R_p|\Psi(t)\rangle\|^2>0$, define

$$
|\Psi_{p,t}\rangle=\frac{R_p|\Psi(t)\rangle}{\sqrt{w_p}}.
$$

For an ideal sequential record measurement, or the corresponding suitably recorded histories,

$$
p(q,t'\mid p,t)=\|R_qU(t',t)|\Psi_{p,t}\rangle\|^2.
$$

The conditional state retains the environment and correlations; the label $p$ alone need not specify them. Conditioning describes the situation relative to a record and does not delete the global state.

Record projectors are physical modeling choices. An identification with Page-style awareness operators is not assumed.

## C. Exact future-relevant coarse graining

Let $\mathcal T$ be a specified class of accessible future protocols. Each protocol $\tau$ and its complete outcome record $r$ determine an effect $E_{\tau r}$ on a sufficiently complete initial state. Define

$$
\rho\sim_{\mathcal T}\sigma
\iff
\operatorname{Tr}(\rho E_{\tau r})
=\operatorname{Tr}(\sigma E_{\tau r})
\quad\text{for every }\tau,r.
$$

This is an equivalence relation. It formalizes compression that preserves all distinctions relevant to the declared protocols. With all global measurements available, it reduces to equality of density operators. Nontrivial compression therefore requires an actual restriction on the accessible questions.

Equal present local records do not guarantee this equivalence. Later interactions can reveal correlations that the present record omits. For environments with memory, a reduced state may need to be replaced by an adequate description of the multi-time process; process-tensor approaches are an appropriate technical neighbor. [Pollock and colleagues, *Operational Markov Condition for Quantum Processes*](https://arxiv.org/abs/1801.09811)

An approximate version can bound statistical distinguishability over a horizon, but a pairwise tolerance relation need not be transitive. It cannot be silently treated as an exact quotient.

The awareness-centered conjecture asks whether an independently grounded awareness correspondence selects such a relevant protocol class or invariant. The operational equivalence does not establish that conjecture.

## D. The delayed-choice eraser

Use the ideal signal–idler state

$$
|\Psi\rangle=\frac{|0\rangle_s|0\rangle_i+e^{i\phi}|1\rangle_s|1\rangle_i}{\sqrt2},
\qquad \psi_j(x)=\langle x|U_s|j\rangle.
$$

The propagated modes are orthonormal globally but can overlap at a screen position. Tracing out the idler gives

$$
p(x)=\tfrac12(|\psi_0(x)|^2+|\psi_1(x)|^2).
$$

Measuring the idler in $|\pm\rangle=(|0\rangle\pm|1\rangle)/\sqrt2$ yields

$$
p(x,\pm)=\tfrac14|\psi_0(x)\pm e^{i\phi}\psi_1(x)|^2,
\qquad p(\pm)=\tfrac12.
$$

These are joint densities. The conditional densities are twice as large. The opposing interference terms cancel when outcomes are combined:

$$
p(x,+)+p(x,-)=p(x).
$$

For separated local measurement operators,

$$
(M_x\otimes I)(I\otimes N_b)=(I\otimes N_b)(M_x\otimes I).
$$

Completeness of the idler instrument gives

$$
\sum_b p(x,b)=\langle\Psi|(M_x^\dagger M_x\otimes I)|\Psi\rangle.
$$

Thus the local idler choice does not change the unsorted signal record. Delaying it changes no requirement for a consistent joint description. This ideal calculation captures the conditional-correlation feature of the quantum eraser, without reproducing every optical component of the experiment. [Kim and colleagues, *A Delayed Choice Quantum Eraser*](https://arxiv.org/abs/quant-ph/9903047); [Fankhauser, *Taming the Delayed Choice Quantum Eraser*](https://arxiv.org/abs/1707.07884)

If another environment retains path records $|e_0\rangle,|e_1\rangle$, let $g=\langle e_0|e_1\rangle$. The joint density becomes

$$
p(x,\pm)=\tfrac14\left[|\psi_0|^2+|\psi_1|^2
\pm2\operatorname{Re}(e^{i\phi}\psi_0^*\psi_1g)\right].
$$

At $g=0$, even these conditional fringes vanish. Removing a distinction from someone's description does not remove a physical record retained elsewhere.

For a finite diagnostic, set $\phi=0$ and measure both qubits in the $+,-$ basis. With row and column order $+,-$,

$$
P_{g=1}=\begin{pmatrix}1/2&0\\0&1/2\end{pmatrix},
\qquad
P_{g=0}=\begin{pmatrix}1/4&1/4\\1/4&1/4\end{pmatrix}.
$$

The local marginals agree while the joint continuation differs. This is a direct illustration of why marginal summaries can conceal consequential coupling.

## E. What Planck's constant contributes

Where an action path integral is available, its schematic form is

$$
A(B)=\int_B e^{iS[\gamma]/\hbar}\,\mathcal D\gamma,
\qquad \Delta\phi=\Delta S/\hbar.
$$

The propagator and its regularization supply the measure and normalization. Planck's constant relates action to phase. It does not independently supply a measure of awareness or future value. [Feynman, *The Principle of Least Action*](https://www.feynmanlectures.caltech.edu/II_19.html)

Near a stationary path, one nondegenerate fluctuation coordinate may satisfy

$$
S(\xi)\simeq S_0+\tfrac12 k\xi^2,
\qquad |\Delta\phi|\lesssim1
\ \Rightarrow\ |\xi|\lesssim\sqrt{2\hbar/|k|}.
$$

This is a local phase-variation estimate in a quadratic approximation. It is not a hard cutoff: other regions contribute, higher-order terms can matter, and distinguishability depends on the full experiment.

Coarse graining can yield discrete effective alternatives without deriving physical quantization. Representation consistency here follows from completeness and linearity. No separate anti-manufacturing axiom, universal minimum length, or quantized-awareness law is needed for the calculation.

## F. A finite continuation and recovery model

For a fully observed model, let $X$ be a finite state space, $A(x)$ its allowed actions, and $\mathrm{Succ}(x,a)$ a nonempty set of successors for each enabled action. Let $S\subseteq X$ encode declared continuation requirements. Partial observation requires an adequate information-state construction or a separate restriction on policies; the statewise formula below cannot silently provide unavailable information to the controller.

Define

$$
\mathcal F(K)=\{x\in S:\exists a\in A(x),\ \mathrm{Succ}(x,a)\subseteq K\}.
$$

Starting with $K_0=S$, iterate $K_{n+1}=\mathcal F(K_n)$. The sequence decreases and stabilizes in the finite model at the greatest fixed point $K_*$. From each state in $K_*$, selecting a witnessing action keeps every modeled successor in $K_*$. This is the standard controlled-invariance structure behind a robust corridor.

The quantifiers matter. Existence of some favorable path is weaker than existence of a policy succeeding against every allowed disturbance. Individually feasible requirements may also fail jointly.

For a declared fact $F\subseteq X$, bounded robust recovery can be written

$$
\operatorname{Rec}^{\mathrm{rob}}_T(x,F)
\iff \exists\pi\ \forall\omega\ \exists t\le T:
x_t^{\pi,\omega}\in F,
$$

where $\pi$ uses only the permitted observations and actions, and $\omega$ ranges over allowed disturbances. Replacing the robust quantification with a favorable-path condition produces a different recovery notion. Resource and repair restrictions belong in the model.

Increasing a repair horizon can restore a previously missing route. Increasing an assessment horizon can expose delayed foreclosure. No horizon-free moral verdict follows from a bounded recovery calculation.

## G. Abstraction, joint structure, and retained project results

A claimed preservation result in an abstraction must transfer to the concrete system. An abstraction that erases a relevant distinction can manufacture apparent recovery or compatibility. Exact aggregation of a stochastic process also preserves only the observations and targets covered by its assumptions.

The earlier packet reports finite witnesses distinguishing pairwise from joint compatibility, local from joint recovery, and locally successful policies from a single robust policy. It also records conditional licensing and corridor results. This edition retains those bounded lessons; it does not report a fresh execution or proof audit of the repository.

Two source locations, pinned to the revision recorded in the earlier addendum, are the [coarse/fine nonreflection note](https://github.com/6ixpoolgames/Omega/blob/cc4c89ca6552ce52cc5f7392e3b95f0c24dfdf88/docs/research_notes/omega_theory/coarse_fine_nonreflection_v0.md) and the [marginal-coupling nonfactorization note](https://github.com/6ixpoolgames/Omega/blob/cc4c89ca6552ce52cc5f7392e3b95f0c24dfdf88/docs/research_notes/omega_theory/marginal_coupling_nonfactorization_v0.md). Their relevance is abstraction integrity and the information lost by separate summaries. The quantum diagnostic above is analogous in structure, not a proved translation of those repository results.

## H. The missing lushness functional

For an exhaustive decoherent family, $\sum_\alpha w_\alpha=1$. A candidate assessment such as

$$
L_{P,T}(\pi)=\sum_\alpha w_\alpha^{\pi}\,G_{P,T}(\alpha)
$$

therefore needs an additional function $G$ encoding the relevant continuation richness. This is an example of where the missing work enters, not a proposed final definition. If relationships among alternatives matter, a branchwise sum may already be too restrictive.

The requirements for a useful candidate include adequate physical and valuer correspondence, retention of consequential coupling, stated behavior under valid changes of presentation, and explicit horizon and aggregation choices. Scalarization remains possible if justified.

Information-geometric optimization is a technical neighbor for principled search on parameterized distributions. It supplies neither this missing functional nor a guarantee of attaining global optima in arbitrary spaces. The broader Alpha/Omega ambition remains an extension to investigate after the relevant structure is specified. [Ollivier, Arnold, Auger, and Hansen, *Information-Geometric Optimization*](https://arxiv.org/abs/1106.3708)

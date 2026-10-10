# 09 — Formal core and glossary

This appendix collects the minimal mathematics used in the manuscript. It separates established constructions from the programme's proposed interpretations. No new universal measure is declared here.

## A. Sufficient present and native development

For a finite closed quantum adapter,

\[
\mathsf P=(\mathcal H,\{\mathcal A(R)\},\mathscr G,H(t)),\quad
\rho_\Sigma\ge0,\quad \operatorname{Tr}\rho_\Sigma=1,
\]

\[
\rho_t=U(t,\Sigma)\rho_\Sigma U(t,\Sigma)^\dagger.
\]

The local algebras, constraints, Hamiltonian and sufficient present define the physical model. An equivalent representation transforms these together. A restriction to a subsystem can omit environmental memory, so its reduced state alone need not be sufficient for further prediction. A process-tensor description can retain multitime operational dependence once its intervention slots are specified [R3]. Those slots describe questions or actual operations; they do not create all physical possibility by definition.

A physical present frame is \(F_\Sigma=(\Sigma,\rho_\Sigma)\) together with the
native specification needed to evolve it. The cut is a physical hypersurface,
or the declared finite-model analogue. A frame description restricts, represents
or conditions this object. The complete development retains the propagator
family \(\{U(t,s):\Sigma\le s\le t\le T\}\), with its interactions and composition,
not just \(U(T,\Sigma)\). Idle and out-and-back evolution can share that endpoint.
Changing coordinates transforms state, observables and law consistently.

An operational composition can be represented by a prefix joint law
\(J(r,y,b,t\mid x)\) for accessible record r, sufficient residual state y,
resource bill b and elapsed time t. A suffix may depend on r, not on inaccessible
knowledge of y held only by the analyst. Its law is integrated against J, with
the remaining deadline and resource stock updated. Failed and unfinished
prefixes retain their mass and physical residual. A proposed compression is
sufficient only for the interfaces and future compositions it demonstrably
preserves.

## B. Classical history breadth

For a discrete Markov law K and exact root x₀,

\[
p_{x_0}(x_1,\ldots,x_n)=\prod_{t=0}^{n-1}K(x_t,x_{t+1}),
\qquad L_{x_0}(n)=e^{H(p_{x_0})}.
\]

Zero-weight histories contribute zero to entropy. H uses natural logarithms unless bits are declared. L is dimensionless in unit-alternative calibration. It is an effective number and is not an additive set volume.

Let g(x)=−ΣᵧK(x,y)log K(x,y). Then

\[
\ell_n=\sum_{t=0}^{n-1}K^tg,\qquad
\ell_{n+1}=g+K\ell_n,\qquad \ell_0=0.
\]

This recurrence computes complete-history entropy without enumerating the exponentially growing tree. It depends on the Markov sufficiency of the state and the declared observation resolution. For non-Markov observed variables, the history-conditional chain rule still applies but this finite-state recurrence may not.

Original-root mass is preserved by lawful stochastic extension. Killing or conditioning must be modeled explicitly. A terminal symbol with a deterministic self-loop preserves the weight of a terminated development without adding branching entropy.

For independent histories p₍AB₎=p₍A₎p₍B₎,

\[
L_{AB}=L_A L_B.
\]

For a coupled joint law, H(A,B)=H(A)+H(B)−I(A;B). This identity compares the actual marginals of that joint law. It does not show that physical coupling always reduces breadth relative to independently prepared controls, whose marginals and access may differ.

## C. References and fresh continuation

For a stationary reference πK=π, the mean separately rooted logbreadth is πℓₙ. Its difference from a preparation x is

\[
\Delta\ell_n(x)=\ell_n(x)-\pi\ell_n
=\sum_{t=0}^{n-1}(\delta_xK^t-\pi)g.
\]

At elapsed step m, expected fresh logbreadth over the next n steps is

\[
F_x(m,n)=(K^m\ell_n)(x).
\]

This is an expectation of separately rooted queries. In general exp F is a geometric mean of their breadths, not their arithmetic mean. It does not include entropy of uncertainty over the new root. A reference must respect conserved quantities, sectors, boundaries and preparation assumptions relevant to the comparison.

### Finite mixing bounds the preparation advantage

**Proposition.** Let K be a fixed finite irreducible, aperiodic stochastic kernel,
π its stationary law, g(x)=H(K(x,·)) and h=πg. Then

\[
c(x)=\sum_{t=0}^{\infty}(\delta_xK^t-\pi)g,\qquad
\ell_n(x)=nh+c(x)+O(r^n),\quad 0<r<1.
\]

**Proof.** Finite irreducible, aperiodic chains converge geometrically [R22]:
there are C<∞ and 0<r<1 with supₓ‖δₓKᵗ−π‖TV≤Crᵗ. Since g is bounded,

\[
|(\delta_xK^t-\pi)g|\le 2C\|g\|_\infty r^t,
\qquad
|\Delta\ell_n(x)-c(x)|\le
\frac{2C\|g\|_\infty r^n}{1-r}.
\]

Absolute summability proves the assertion. Reversibility and detailed balance
are not assumptions. The constants depend on K; they need not remain bounded
when system size or a physical parameter changes.

Consequently Lₓ(n)/exp(nh)→exp c(x), and for two preparations
Lₓ(n)/Lᵧ(n)→exp(c(x)−c(y)). The ratio need not approach one. The denominator
exp(nh) is the geometric mean of separately rooted stationary breadths, not
the arithmetic mean or the breadth of a mixed initial root.

The excess next-step production tends to zero. More strongly, for fresh
continuation Fₓ(m,n)=Kᵐℓₙ(x),

\[
|F_x(m,n)-nh|
\le\frac{2C\|g\|_\infty r^m(1-r^n)}{1-r}
\le\frac{2C\|g\|_\infty r^m}{1-r}.
\]

Thus fresh advantages decay even uniformly over the future window n. The
reactive probe's reported fresh-window comparison is this kind of query;
its eventual convergence is conditional on the sampled chain satisfying the
stated assumptions, not established by its finite-window result alone.

For a common time-dependent sequence Kₜ on a fixed finite state space,
let gₜ(x)=H(Kₜ(x,·)). Two preparation laws μₜ,νₜ obey

\[
\Delta\ell_n=\sum_{t=0}^{n-1}(\mu_t-\nu_t)g_t.
\]

If Σₜ‖μₜ−νₜ‖TV<∞, their log-breadth difference still converges because
gₜ≤log|X|. Time dependence therefore does not itself guarantee escape.
A finite irreducible periodic chain also shares an asymptotic entropy rate,
although the bounded offset can oscillate rather than converge.

Distinct closed classes can carry different entropy rates, but a cross-class
advantage is not an advantage against the preparation's own class-conditioned
stationary reference. Infinite state spaces, growing finite-size limits and
non-forgetting driven laws require their own analysis; none guarantees a
positive generative advantage merely by escaping this proposition.

## D. Quantum history functional

For exhaustive orthogonal projective alternatives at declared cuts,

\[
C_\alpha=P^{(n)}_{a_n}U_{n,n-1}\cdots
P^{(1)}_{a_1}U_{1,0},\qquad
D_{\alpha\beta}=\operatorname{Tr}(C_\alpha\rho_\Sigma C_\beta^\dagger).
\]

With a pure root and |vα〉=Cα|ψΣ〉, this convention gives Dαβ=〈vβ|vα〉. D is positive semidefinite. For this exhaustive sequential-projector construction, Tr D=1 and ΣαβDαβ=1. The two normalizations have different reasons: summed sequential measurement probabilities and coherent reconstruction respectively. Trace-one is not an axiom for every abstract decoherence functional.

For a coarse history A, C_A=Σα∈A Cα, hence

\[
D(A,A)=\sum_{\alpha,\beta\in A}D_{\alpha\beta}.
\]

Medium decoherence, Dαβ=0 for distinct members of the family, suffices for ordinary probability addition. It does not establish that this particular family is physically preferred. Mathematical orthogonality, an algebraic record certificate and actual formation of a durable record are different claims.

An eventual breadth must identify its physical comparison domain. Agreement with every analyst-selected classical partition and complete independence from that selection are incompatible in the idle-qubit example. The task is to justify the physical boundary, not conceal the contradiction with a new entropy.

## E. Optional reference-volume template

If independently justified classical cells have masses mᵢ>0, a possible effective-volume readout is

\[
V=\exp\left[-\sum_i p_i\log(p_i/m_i)\right].
\]

For unit cells it reduces to perplexity. For uniform occupation relative to those cell volumes, it equals their total volume. A reference unit is needed if the mᵢ are dimensional. This formula does not determine the cells or their physical masses.

A finite algebra ⊕ₐMₙₐ admits traces τ(A)=ΣₐwₐTr(Aₐ). Choosing weights, native generators and history composition remains additional work. An abstract algebra can ignore inert representation multiplicity, but algebraic closure can also erase coupling strength, timing and reachability. Acting with every observable is not the same as native evolution. No τ-based formulation is required by v4, and the finite trace cannot be carried unmodified into general local QFT.

This route remains open. Its next obligation is a native prescription that
preserves equivalent descriptions, timing and coupling strength, excludes inert
bookkeeping, and reproduces the declared classical unit-alternative limit.
Testing that prescription on record extension and coherent erasure precedes
promoting any resulting entropy to quantum lushness. A broader field-theoretic
construction must separately justify its continuum or regulated reference.

## F. Decision implementations and matching

Write J for a physical decision lineage and m for a justified matching rule. Schematically,

\[
\Omega^m_\pi=\Omega\big(\mathsf{CF}_m(F,J,\pi),\mathcal L\big),
\qquad
\mathrm{Choice}_m=\operatorname{Max}_{\succeq}
\{\Omega^m_\pi:\pi\in\Pi_m\}.
\]

Here CF is a construction to be supplied, not an oracle already defined by physics. Πₘ contains implementations admissible under the matching assumptions. The evaluation relation is explicit; in this programme it is the intended lushness ordering, provisionally partial where the comparison is unresolved. For finite nonempty sets and a strict partial preference, maximal elements exist; an infinite plan space needs additional existence conditions. A family of justified matching rules can yield different maximal sets, which must be reported rather than silently collapsed into one answer.

Classically, selecting histories by a plan gives P(Y|π occurs). An implemented alternative gives the law generated by its physical realization under the declared matching. Equality requires justification. Native branch support alone is neither an implementation certificate nor a proof of causal control. In continuous spaces, nonzero support of an event or neighborhood must not be confused with positive probability of every individual trajectory.

The valid deterministic claim is limited: for a forward-deterministic law and sufficient global states, F(s)=F′(s) implies F(t)=F′(t) for t≥s. It does not select counterfactual semantics, prohibit comparison across lawful preparations, or convert relative quantum branching into indeterministic global evolution.

## G. First access, occupancy and maintenance

For a declared classical target class V, let τᵥ=inf{t≥0:Xₜ∈V}, with τᵥ=∞ when the target is never reached. The first-access profile is Aₓ(t)=Pₓ(τᵥ≤t). Then

\[
\int_0^T A_x(t)\,dt
=\mathbb E_x[(T-\tau_V)_+].
\]

The identity follows by integrating the indicator of arrival and exchanging the nonnegative integral and expectation. An early visit followed immediately by loss still scores almost T. It therefore measures arrival timing, not maintained organization.

A distinct occupancy diagnostic is

\[
O_x(T)=\mathbb E_x\!\left[\int_0^T\mathbf1_V(X_t)\,dt\right]
=\int_0^T P_x(X_t\in V)\,dt.
\]

Maintenance can instead require remaining in V for a declared duration after arrival; regeneration can concern return after a specified departure or disturbance. These observables answer different questions, and a coarse target class may omit important organization in every case. They are forward-rooted diagnostics, not a time-averaged present or a definition of lushness. Quantum versions need a physical monitoring or history construction; repeated projections cannot be inserted as harmless observation.

Effective resistance and relaxation spectra provide related but narrower access information. The graph commute identity applies with specified conductances, clock convention and boundary states or contracted sets. Reducing resistance does not establish that all target-specific hitting times or free-energy costs decrease; discrete-time conductance changes also change clock normalization [R18]. In a reversible continuous-time chain with fixed stationary law and increased symmetric conductances, the ordered nonzero eigenvalues of −Q cannot decrease. That spectral comparison is not a pointwise ordering of every access profile.

Equal endpoint laws give equal endpoint-only readouts. Convergence of laws implies convergence of a readout only under suitable continuity and integrability conditions. Neither statement erases distinctions in complete developments or mandates a particular cumulative score.

For a controlled finite model, a viability set collects states from which an
available policy keeps declared requirements satisfied against the specified
disturbances. Existence of a separate successful action for each hidden state
does not supply an executable selector. Full-state feedback and partial
observation therefore require different state descriptions and proof obligations.
Robust joint recovery needs one policy for the joint requirements; separate or
pairwise guarantees alone do not establish it. These are scoped tools for
implementation and maintenance, not alternative definitions of lushness.

## H. Terms and claim status

| Term | Meaning in v4 |
| --- | --- |
| Native development | The physical state and law evolving with declared interactions, resources and boundaries. |
| Futuresfield | Physical possibility and its relational continuation, including quantum coherence; no added substance. |
| Perspective | Situated physical access and influence of a process. |
| Physical present frame | An admissible present hypersurface with its physical state; finite models use an update cut. |
| Frame description | A representation, restriction or conditioning of that physical frame and its continuation. |
| Lushness | Intended effective weighted extent/breadth of continuation; a classical calibration exists, general quantum comparison remains open. |
| Generativity | Producing or maintaining conditions that enable further continuation, proposed to increase lushness in some regimes. |
| Access | A witnessed route to an outcome or capability, with native weight, time, information and physical resources. |
| Joint feasibility | Existence of one lawful realization of a combination; separate witnesses do not establish it. |
| Readiness | Present availability of enabling conditions, distinguished from the route and bill for producing them. |
| Deformer | An organized process that changes surrounding continuation. |
| Agency | Feedback and internal organization systematically modulating a process's effects; not a gate to possible valuerhood. |
| Persistence filter | Native conditions determining which processes continue to have consequences. |
| Recovery | Restoration of a declared function or organization by a physical route; existential, probabilistic and robust claims differ. |
| Individual trajectory | A particular causally maintained and transformed organization; pattern matching alone does not establish identity. |
| Residual continuation | What follows from the sufficient present at a new cut. |
| Reconvergence | Agreement of later state or residual law; it need not erase distinct original-root prefixes. |
| Physical occurrence | A particular realization, distinct from an isomorphic description or matching residual law. |
| Valuer | A process through which distinctions matter; functional, phenomenal and ethical scope must be distinguished. |
| Potential-valuer admission | Every consequential process remains eligible under uncertainty; admission establishes neither actual valuation nor equal moral weight. |
| Conditional normativity | Reasons whose force depends on valuing and its consequential conditions. |
| Decision lineage | Physical organization carrying the evaluated decision through the relevant interval. |
| Implementation | A lawful, resource-accounted realization of a plan or control. |
| Counterfactual matching | The declared treatment of varied and shared conditions when implementations are compared. |
| Anchor | A section proposed to root a comparison; its uniqueness and selection remain open. |
| Focus | A specified future question represented, where applicable, by an effect or test; analytical focus does not implement an intervention. |
| κ | Placeholder for the relation between physical organization and experience, not an established mechanism. |
| Alpha / Logos / Omega | Interpretive possibility / lawful articulation / completed manifestation. |
| Ultimate frame | Intended encompassing closure of comparison, not an external chooser or a computed universal ordering. |

“Established” refers to mathematics or source-supported results under stated assumptions. “Finite evidence” refers to the specified models and tolerances. “Adopted” identifies a project commitment or calibration. “Proposed” and “open” identify work still required. These categories should accompany future extensions even where prose does not repeat the label in every sentence.

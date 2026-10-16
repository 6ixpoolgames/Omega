# 12 — Formal core

This part fixes one notation for the whole primer. Sections A–J retain the finite classical presentation; K and L give the quantum realization. Section M adds the 3.2 finite access-atlas specification, and N the information identity used in the new probes. Relativistic and general cosmophysical extensions need their own algebras, boundary structures, and causal conditions. They are not completed by this notation, and each extension must state what it additionally requires.

Status: statements labelled **Lemma** or **Proposition** are proved here or are standard results, cited. Definitions labelled **[proposed]** are the program's synthesis. Nothing in this part defines lushness.

## Schematic reference object

The reference object is written schematically as

```text
𝔉 = ( 𝖬, 𝖶, {𝒦_{c,H}}, Seq, Joint, Restrict ).
```

𝖬 is the underlying physical model and 𝖶 the admitted realization witnesses. The remaining entries are derived: continuation laws indexed by context and horizon, physically supported sequential composition, joint realization, and restriction maps to coarser descriptions. They are not independent sources of possibility. **[proposed]**

## A. Finite presentation and path laws

A finite controlled Markov model is S = (X, A, K) with finite X, admitted action sets A(x), and

```text
K(x, a, y) ≥ 0,     Σ_y K(x, a, y) = 1.
```

X includes all environment, apparatus, controller memory, resource stocks, and correlations needed for the Markov property. Expenditure is a vector d(x, a, y) ∈ ℝ^k with declared units; stocks and replenishment are state variables.

A context c supplies an initial law μ_c, an interface, boundary conditions, a cost origin, and permitted apparatus. A protocol π chooses actions from accessible records r_≤t, produced by an implemented observation process. The path law is

```text
P_c^{π,H}(h_H) = μ_c(x₀) · Π_{t=0}^{H−1} π(a_t | r_≤t) · K(x_t, a_t, x_{t+1}),
D_H(h_H) = Σ_{t<H} d(x_t, a_t, x_{t+1}).
```

**Lemma A1 (horizon consistency).** For a protocol whose horizon-H behaviour is the truncation of its horizon-(H+1) behaviour, marginalizing P_c^{π,H+1} over (a_H, x_{H+1}) gives P_c^{π,H}.

*Proof.* Σ_{a,y} π(a | r_≤H) K(x_H, a, y) = 1. ∎

## B. Realization, preparation, and instruments

A **realization witness** for a protocol is a tuple (apparatus, controller, record map, preparation process, resource sources and sinks, embedding) such that the embedded autonomous dynamics induces the claimed path law, records, and costs. **[proposed]**

**Preparation.** If a preparation event Prep has probability p and the task event E has conditional probability q = P(E | Prep), the route probability is P(E ∧ Prep) = pq. The conditional law is retained with its conditioning event and p attached.

**Instrument.** For protocol π:

```text
J_{π,r}^{t,b}(x, y) = Pr_x^π( finish with record r, at time t, with expenditure b, in state y ).
```

Outcomes include failure records and a censoring record for runs unfinished at the horizon; a censored run keeps its state at the horizon. Summed over r, t, b, y, the instrument has total mass one: no outcome is renormalized away.

## C. Composition and joint feasibility

**Sequential composition.** Given a witness for running π then σ with matching boundaries:

```text
J_{σ∘π,(r,s)}^{t,b}(x, z) = Σ_{y; t₁+t₂=t; b₁+b₂=b} J_{π,r}^{t₁,b₁}(x, y) · J_{σ,s}^{t₂,b₂}(y, z).
```

For a record-adaptive continuation (σ_r), replace σ by σ_r in the r-th term.

**Lemma C1 (associativity).** Valid composites satisfy (ρ∘σ)∘π = ρ∘(σ∘π) as instruments.

*Proof.* Both sides are the same finite sum over intermediate states, times, and expenditure splits. ∎

Associativity holds for composites that exist. The lemma does not show that any composite apparatus exists; preparation, switching, communication, and disposal are further witnessed stages.

**Joint realization.** γ ⊩_c (p₁, …, p_n) means one witnessed realization supplies the listed components in one encompassing execution. Matching their marginal instruments is a marginal-realization claim only: it does not determine correlations. A specified joint response must be matched as a joint instrument, including residual correlations. A weaker task-form readout is

```text
∃ γ ∈ Π_phys(c) :  P_c^γ( ∩_i E_i  ∧  D_H ≤ b ) ≥ 1 − ε.
```

**Lemma C2 (downward closure).** For fixed (c, H, b, ε), if a family of task events is jointly realizable, so is every subfamily.

*Proof.* ∩_{i∈F} E_i ⊆ ∩_{i∈F′} E_i for F′ ⊆ F, so the same γ works. ∎

The jointly realizable families therefore form an abstract simplicial complex. Pairwise realizability does not imply membership of the whole family (Part 11, Example 6).

**Shared-action viability kernel under full-state feedback. [project result]** For finite X, a safe set Kₛ ⊆ X, and a set of shared physical actions A_sh(x), define

```text
W₀ = Kₛ,
W_{n+1} = { x ∈ W_n : ∃ a ∈ A_sh(x) with supp K(x, a, ·) ⊆ W_n }.
```

The sequence decreases and stabilizes after at most |X| steps at the greatest subset of Kₛ that can be kept invariant by a shared action chosen as a function of the current full state. This is the fully observed control problem.

An embodied guarantee additionally requires a physically realizable selector measurable with respect to the controller's accessible records. If indistinguishable states require different safe actions, pointwise existence of an action is insufficient (Part 11, Example 7). Under partial observation, compute viability on information or belief states, requiring an action admissible and safe for every state compatible with the current information and updating that information after observations. A full-state kernel alone supplies no such guarantee.

Probabilistic variants must specify whether the constraint is per step or on survival over the whole horizon. A per-step threshold is not the same as a horizon-wide survival guarantee; the latter requires the corresponding reach-avoid or survival calculation.

## D. Tasks, capability, recovery, and compatibility

```text
Realize_{H,b,ε}(c, T)  ⟺  ∃ π ∈ Π_phys(c) :  P_c^π( E_T ∧ D_H ≤ b ) ≥ 1 − ε
Cap_{H,b,ε}(c; 𝒯)    =  { T ∈ 𝒯 : Realize_{H,b,ε}(c, T) }.
```

For a transition model x_{t+1} = f(x_t, a_t, e_t), a target A, and policy class Π, **existential recovery** means some allowed policy and contingency realization reaches A by H. **Robust recovery** means one policy secures the registered criterion for every contingency sequence in E. Policies condition only on information available at their decision points.

For requirements R_i on complete allowed continuations z:

```text
Real(F)       = { z : R_i(z) for every i ∈ F }
May(F)        ⟺ Real(F) ≠ ∅
Robust_E(F)   ⟺ ∃ π ∈ Π  ∀ e ∈ E :  outcome(π, e) ∈ Real(F).
```

**Lemma D1.** If E is nonempty and outcomes are valid continuations, Robust_E(F) ⇒ May(F).

*Proof.* Pick e ∈ E; outcome(π, e) ∈ Real(F). ∎

Adding requirements shrinks Real(F), and enlarging E shrinks the set of securing policies. The converses fail, as do the inferences from individual to joint recovery and from pairwise to full compatibility.

**Policy-cover number.** With success regions S_π = { e : outcome(π, e) ∈ Real(F) }:

```text
ν_F(E) = inf { |P| : P ⊆ Π,  E ⊆ ∪_{π∈P} S_π },     ν_F(E) = ∞ if no cover exists.
```

A finite cover records complementary policy success. Executing it needs a realizable selector or an equivalent adaptive policy (Part 11, Example 7). The letter ν is used so as not to clash with the phenomenal coupling κ.

## E. Accessibility, enabling, and the recursive presentation

**Lemma E1 (no extra-lawful possibilities).** If a prefix protocol α reaches y from x with positive probability and a continuation β reaches event E from y with positive probability, and the composite α-then-β is admitted in the model, then the concatenated histories have positive probability under the encompassing dynamics from x.

*Proof.* The composite path probability is the product of the positive factors along the concatenated history. ∎

Construction therefore never creates possibilities outside the lawful path space. It changes probabilities, costs, delays, and control.

**Lemma E2 (accessibility composition).** For a prefix α and record-dependent continuation (β_r):

```text
P_c^{(β_r)∘α}(E_T) = Σ_{x,r,y} μ_c(x) · J_{α,r}(x, y) · P_y^{β_r}(E_T),
```

with E_T read on the continuation and, for origin-based deadlines, prefix time and expenditure included.

*Proof.* Condition on the prefix outcome (r, y) and apply the Markov property of the encompassing model. ∎

**Enabling contrast. [proposed]** For a declared feasible comparison preparation N, the same origin-based horizon and budget, and an implementable continuation Q:

```text
Δ_c^{H,b}(P, N; Q) = P_c^{Q∘P}(E) − P_c^{Q∘N}(E).
```

Cases where Q cannot be deployed after a prefix are recorded as such. The contrast is baseline-dependent and is not a value increment.

**Recursive presentation. [proposed]** With base record B₀ and implementation catalogue 𝒞:

```text
G₀(x) = B₀(x)
G_H(x) = ( B₀(x),  { π ↦ Law_x^π( r, t, b, G_{H−t}(X_t) ) }_{π ∈ 𝒞},  Joint_H(x) ),     1 ≤ t ≤ H.
```

Because every nontrivial stage consumes at least one time step, G_H is defined by well-founded recursion on H in this discrete model. Joint_H is derived from witnessed joint realizations (§C). Renaming is handled by consistent isomorphism of the entire physical presentation. Equal tested behavior is not a rule for identifying physical occurrences; any predictive quotient remains separate and scope-relative. Represented composites must agree with valid composition. The analyst's G_{H−t}(y) is not controller knowledge of y. Section M makes the physical record and limits of this schema explicit.

## F. Testers, equivalence, refinement, and distance

A tester τ is an admissible interaction with context and output record. For matched processes p, q and tester family 𝒯:

```text
p ≡_𝒯 q  ⟺  Law(τ[p]) = Law(τ[q])  for all τ ∈ 𝒯
d_𝒯(p, q) = sup_{τ∈𝒯} TV( Law(τ[p]), Law(τ[q]) ).
```

**Proposition F1 (equivalence and refinement).** ≡_𝒯 is an equivalence relation. If 𝒯₁ ⊆ 𝒯₂, then d_𝒯₁ ≤ d_𝒯₂, and ≡_𝒯₂ implies ≡_𝒯₁.

*Proof.* Equality of laws is reflexive, symmetric, and transitive. A supremum over a subset cannot exceed the supremum over the superset. ∎

A longer horizon refines when its tester family contains the shorter tests, for example by retaining their records. Endpoint-only families at longer horizons need not contain them and can lose distinctions through mixing.

d_𝒯 is a pseudometric on a common typed domain and a metric on its zero-distance quotient. The relation d_𝒯 ≤ ε is generally not transitive.

**Proposition F2 (restricted contraction).** If a transformation Φ maps compared processes to a new interface, and every admissible output tester composed with Φ is an admissible input tester, then d_out(Φp, Φq) ≤ d_in(p, q).

*Proof.* Every output test is an input test, so the output supremum ranges over a subset. ∎

For closed unitary dynamics with unrestricted global access, distinguishability is preserved; substantial compression must come from a specified restriction.

**Proposition F3 (encoding bound).** If an encoding e and decoder satisfy sup_{x,τ} TV(Law(τ[x]), predicted law from e(x)) ≤ ε, and e(x) = e(x′), then d_𝒯(x, x′) ≤ 2ε.

*Proof.* Triangle inequality through the common prediction. ∎

**Contextual substitution.** If 𝒯 contains τ∘C for every surrounding context C in a declared class and every τ, then p ≡_𝒯 q implies C[p] ≡ C[q] for every such C. Equality of standalone marginals is insufficient (Part 11, Example 11).

**Exact lumpability. [established; R47]** A partition 𝒫 of X is lumpable for action a when Σ_{y∈B′} K(x, a, y) is the same for all x in each block B, for every block B′. Policies, targets, costs, and records need their own factorization conditions.

## G. Faithful compression and the three-bit family

For an encoding q and update F_a, exact faithfulness requires F̄_a with q∘F_a = F̄_a∘q (pushforward laws in the stochastic case).

**Proposition G1 (covariance is not closed under continuation).** For x, y, z ∈ {−1, +1} and P_t(x,y,z) = (1 + t·xyz)/8 with |t| ≤ 1, let q retain means and covariance. Then q(P_t) = (0, I₃) for all t. Under F(x,y,z) = (x, y, xyz):

```text
mean(F_*P_t) = (0, 0, t),     cov(F_*P_t) = diag(1, 1, 1 − t²).
```

*Proof.* Under P_t every nonconstant product moment except E[XYZ] = t vanishes. The output's third coordinate has mean t and second moment 1; its products with X and Y reduce to YZ and XZ, with zero mean. ∎

So no exact F̄ exists on this summary. TV(P_t, P_s) = |t − s|/2, so the full laws already distinguish the preparations.

**Observable completion.** With χ_S(x) = Π_{i∈S} x_i for S ⊆ {1,2,3}:

```text
Σ_x χ_S(x) χ_T(x) = 8·[S = T],       P(x) = (1/8) Σ_S E_P[χ_S] χ_S(x).
```

The functions 1, X, Y, Z, XY, XZ, YZ span seven dimensions; the pulled-back future readout supplies XYZ, completing the basis. In larger models, close the declared readouts' span under pullback through permitted operations (in quantum models, the dual map). Economical finite closure is not guaranteed.

**Proposition G2 (conditional transfer).** With an independent input U multiplying Z, the parity decoder, and exposed output W = UXYZ:

```text
K_t(w | u) = (1 + t·uw)/2,     TV(K_t(·|+1), K_t(·|−1)) = |t|,     best fair-input recovery = (1 + |t|)/2.
```

*Proof.* A = XYZ has P(A = a) = (1 + ta)/2 and W = UA. For binary equiprobable hypotheses the optimal success is ½ + ½·TV. ∎

For a balanced readout f, t is replaced by t·c_f with c_f = (1/8) Σ xyz·f(x,y,z). Over the 70 balanced f: 36 have c_f = 0, 16 each c_f = ±1/2, one each c_f = ±1. Receiver postprocessing V = RW with independent sign R of mean s/t maps K_t to K_s for |s| ≤ |t|; no receiver-only stochastic map achieves |s| > |t|, since it multiplies the difference of conditional output probabilities by a − b ∈ [−1, 1].

## H. Information quantities

**Proposition H1 (information sufficiency). [established; R48]** Let Θ, C, M be finite random variables under a joint law P.

1. If I(Θ; M | C) = 0, then for every loss ℓ(θ, a), the Bayes risk of the best rule using (C, M) equals that of the best rule using C alone.
2. Under logarithmic loss, the Bayes risk using C is H(Θ | C), and using (C, M) it is H(Θ | C, M). The reduction is exactly I(Θ; M | C).

*Proof.* (1) I(Θ; M | C) = 0 gives P(θ | c, m) = P(θ | c) on supported (c, m), so the posterior expected loss of every action depends on c only, and a C-measurable minimizer attains the same risk. (2) The Bayes-optimal log-loss prediction is the posterior; its expected loss is the conditional entropy. Subtract. ∎

The proposition concerns evidence about Θ under P. It says nothing about computation, execution, redundancy, error correction, consent, or preparations outside P's support (Part 11, Example 15).

**Data processing and its strong form.** For a Markov chain U → X → Y, I(U; Y) ≤ I(U; X). [established; R48] For a channel K, the SDPI coefficient η_KL(K) = sup I(U; Y)/I(U; X) over such chains satisfies η_KL(K) ≤ η_TV(K), where the Dobrushin coefficient is η_TV(K) = max_{x,x′} TV(K(x,·), K(x′,·)). [established; R45]

**Proposition H2 (contraction may need blocks).** On X = {0, 1, 2}, let

```text
K = [ [0, 1, 0],
      [0, 0, 1],
      [1/3, 1/3, 1/3] ].
```

K is irreducible and aperiodic, η_TV(K) = 1, and η_TV(K²) = 2/3.

*Proof.* Rows 0 and 1 are disjoint point masses, so η_TV(K) = 1. The cycle 0 → 1 → 2 → 0 has length 3 and the loop at 2 has length 1, so the chain is irreducible and aperiodic. K² has rows (0, 0, 1), (1/3, 1/3, 1/3), (1/9, 4/9, 4/9), whose largest pairwise TV is 2/3. ∎

So retention of an initial signal can fail to contract in one step and still contract over blocks: I(A; X_{t+2}) ≤ (2/3)·I(A; X_t) for this chain. No size-independent memory lifetime follows from a single-component coefficient, and redundancy, coding, protected degrees of freedom, and repair change the applicable channel.

## I. Candidate lushness profiles

None of the following is selected as lushness. Each is an instrument with known scope.

**Support profile.** Let Γ_H be the quotient of a declared domain under ≡_{𝒯_H}, with metric d_H = d_{𝒯_H} (§F). If Γ_H is totally bounded, L_support(H, ε) = log N_ε(Γ_H, d_H), the logarithm of the fewest radius-ε balls covering it. Whether the domain is resource-permitted, reachable from a fixed boundary, or ensemble-supported is declared; these are different objects.

**Covariance log-determinant.** For a physical measure μ and justified feature map φ with finite second moments:

```text
m = ∫ φ dμ,     Σ = ∫ (φ − m)(φ − m)ᵀ dμ,
L_cov(β, Q) = log det(I + β Q^{1/2} Σ Q^{1/2}) = log det(I + β Σ Q),     β > 0,
```

for a declared positive-definite feature metric Q. Under φ′ = Sφ with invertible S, Σ′ = SΣSᵀ and a transported metric Q′ = S^{−T} Q S^{−1} give Σ′Q′ = SΣQS^{−1}, so the score is invariant. Holding Q fixed while changing units changes the modelled metric.

**Proposition I1 (fixed-trace spread).** For eigenvalues λ_i ≥ 0 summing to s > 0 in d dimensions, Σ_i log(1 + βλ_i) ≤ d·log(1 + βs/d), with equality at equal eigenvalues; for r > 1 equal positive directions, r·log(1 + βs/r) > log(1 + βs).

*Proof.* Concavity of log(1 + βλ) and Jensen's inequality. ∎

**Proposition I2 (calibration boundary).** Let preparation P₁ be uniform on (±2, 0), P₂ uniform on (±1, ±1), and P₃ uniform on (±1, ±1/2), with coordinate features, Q = diag(1, q), and β, q > 0. Then exp L₁ = 1 + 4β, exp L₂ = (1 + β)(1 + qβ), exp L₃ = (1 + β)(1 + qβ/4), and

```text
exp L₂ − exp L₁ = β[ q(1 + β) − 3 ].
```

P₂ scores higher when q(1 + β) > 3 and P₁ when it is smaller, with a tie on the boundary; P₃ is below P₂ throughout. At q = 1 the crossover is β = 2. ∎

**Proposition I3 (rare broad alternatives).** For records 0, 1, …, m with P(0) = 1 − p and P(i) = p/m, features φ(0) = 0, φ(i) = e_i, and Q = I:

```text
Σ = (p/m) I − (p²/m²) 11ᵀ,
L_cov = (m − 1) log(1 + βp/m) + log(1 + βp(1 − p)/m),
0 ≤ L_cov ≤ β Tr Σ = β(p − p²/m) ≤ βp.
```

*Proof.* Σ has eigenvalue p/m on the (m − 1)-dimensional complement of 1 and p(1 − p)/m along 1; apply log(1 + x) ≤ x. ∎

Support is m + 1 for every p ∈ (0, 1). The uniform bound comes with saturation in m and depends on the bounded features and fixed β.

**Proposition I4 (regularized determinants and duplicates).** Let G be positive semidefinite, v a unit vector, and δ > 0. If v is an eigenvector of G with eigenvalue λ, then log det(I + G + δvvᵀ) − log det(I + G) = log((1 + λ + δ)/(1 + λ)). If Gv = 0 (a new direction orthogonal to the range of G), the increase is log(1 + δ).

*Proof.* In both cases v is an eigenvector of G + δvvᵀ with eigenvalue raised by δ and the other eigenvalues unchanged; the determinant factorizes over eigenvalues. ∎

So log det(I + G) never vanishes for duplicates and rises with reinforcement, with diminishing returns (Part 11, Example 17). Its structure is not that of the antisymmetric determinant of a fermionic wavefunction.

**Probability-weighted covers.** For domain Γ, metric d, physical measure μ, closed balls B_ε(c) = { x : d(x, c) ≤ ε }, ε ≥ 0, and 0 ≤ δ < 1:

```text
N_{(ε,δ)}(Γ, d, μ) = inf { |C| : C ⊆ Γ finite,  μ( ∪_{c∈C} B_ε(c) ) ≥ 1 − δ },
```

infinite if no finite cover exists. For the two parity response laws with equal weights and centres in the family, N = 1 when ε ≥ |t| or δ ≥ 1/2, and 2 otherwise. Allowing centres outside the family changes the radius boundary, so the centre convention is part of the construction.

**Similarity-sensitive diversity. [established; R35]** For weights p and symmetric similarity Z with 0 ≤ Z_ij ≤ 1, Z_ii = 1: D₂(p, Z) = 1/(pᵀZp). With Z = [[1, 1 − |t|], [1 − |t|, 1]] and equal weights, D₂ = 1/(1 − |t|/2).

## J. A finite decision frame

For a finite nonempty action set A, corridor criterion C(a), and model-to-world justification J(a):

```text
A₀ = { a ∈ A : C(a) ∧ J(a) }.
```

Given a preorder ≽ on A₀, ODT1 keeps the actions not strictly dominated. For finite nonempty A₀ this frontier is nonempty (a maximal element of a finite preorder exists). ODT2 selects from it by registered arbitration. An empty A₀ is an informative outcome and calls for an explicitly specified emergency procedure.

**Lemma J1.** For an objective F_θ on A and nonempty A_R ⊆ A, max_{A_R} F_θ ≤ max_A F_θ. ∎

## K. Quantum realization

A state ρ is positive semidefinite with Tr ρ = 1. A channel ℰ is completely positive and trace preserving. An effect F satisfies 0 ≤ F ≤ I. An instrument {ℳ_o} is a family of completely positive trace-nonincreasing maps summing to a channel. [established; R06, R07]

```text
p(o) = Tr[ℳ_o(ρ)],        ρ_o = ℳ_o(ρ) / p(o)  when p(o) > 0.
```

Keep the pair (p(o), ρ_o), or the unnormalized ℳ_o(ρ). Conditional normalization alone discards p(o). This is the quantum form of the instrument of §B, and failure outcomes are retained in the same way.

For Kraus operators K_(o,α), sum over unrecorded α inside ℳ_o(ρ).
An ensemble label or Kraus index is not automatically an accessible physical
outcome. If later dynamics uses the environment, retain a dilation or an
equivalent full process representation; a reduced marginal alone is insufficient.

**Sequential instruments.** For a specified compatible protocol with instruments ℳ^{(k)} and intermediate channels ℰ_k:

```text
p(o₁, …, o_n) = Tr[ ℳ^{(n)}_{o_n} ∘ ℰ_{n−1} ∘ ⋯ ∘ ℰ₁ ∘ ℳ^{(1)}_{o₁}(ρ) ].
```

This gives the joint law for that protocol only. It does not supply one classical joint distribution over the outcomes of all incompatible measurements.

**Process tensors and combs.** Across n intervention slots, a process tensor or quantum comb Υ assigns probabilities to sequences of operations through a fixed pairing, p = ⟨Υ, 𝒜^{(1)}_{o₁} ⊗ ⋯ ⊗ 𝒜^{(n)}_{o_n}⟩, subject to positivity and causal normalization. Implementations must fix one Choi convention; tensor order and transposes follow it. [established; R15, R16, R31] Operational distances between multi-round strategies supply the quantum analogue of d_𝒯. [established; R36] Joint systems are not automatically tensor products of their reduced descriptions.

**Decoherent histories.** For histories α = (α₁, …, α_n) with Heisenberg-picture projectors P^{(k)}_{α_k}(t_k), the class operator is C_α = P^{(n)}_{α_n}(t_n) ⋯ P^{(1)}_{α₁}(t₁), and the decoherence functional is

```text
D(α, β) = Tr( C_α ρ C_β† ).
```

A family of histories admits classical probabilities p(α) = D(α, α) when D(α, β) = 0 for α ≠ β (medium decoherence) or, more weakly, Re D(α, β) = 0 (consistency). Incompatible families are not pooled into one classical tree. [established; R01]

## L. Focus and the phenomenal port

**Focus.** For a downstream effect F after channel ℰ:

```text
p(F | ρ) = Tr[F ℰ(ρ)] = Tr[ℰ*(F) ρ].
```

The equality defines the dual map ℰ* under the trace pairing. The forward state ℰ(ρ) and the backward-propagated effect ℰ\*(F) are paired; ℰ\*(F) is an inference object, not a claim that a later event rewrites an earlier state. Actual interventions are instruments and can change the process. The past-quantum-state formalism extends the pairing to records on both sides of an interval. [established; R08]

**Eraser.** For |Ψ⟩ = (|a⟩|0⟩ + |b⟩|1⟩)/√2 and a marker measured in the ± basis, p(x | ±) = |ψ_a(x) ± ψ_b(x)|²/2, each outcome has probability 1/2, and the mixture is [|ψ_a(x)|² + |ψ_b(x)|²]/2 (Part 11, Example 3). [established; R12]

**The phenomenal port.** The physical object 𝔉 does not fix a phenomenal theory. An extended description may pair it with a domain of experiences and a specified correspondence κ, together with any measure the proposal needs. One possible realization is Page's μ(S) = Tr[ρ A(S)] for sets S of experiences and positive operators A(S). [R25, R26] This is an example, not a required form, and it does not require physical backreaction.

An interacting proposal must revise the physical model and its continuation laws accordingly. A correspondence with unchanged physical predictions can extend the phenomenal description without altering physical tester equivalence. Evaluative use of either extension requires a declared comparison; neither additional tests nor additional phenomenal structure alone proves that a numerical lushness measure increases. The port remains unspecified in this edition (Part 09).

---
## M. Finite recursive access atlas [proposed specification]

### Physical model and cuts

Fix a finite-dimensional apparatus A with its factors, coupling incidence,
primitive operations, classical controller and memory, clocks, resource
stocks, autonomous environment evolution and initial joint state. A
classical finite-state model is an admitted special case. The finite
implementation uses positive integer primitive durations. Zero-time
notational regroupings are not extra physical events.

Use a finite operation alphabet with specified parameters and finitely many
recorded outcomes per primitive in this first backend. Finite Hilbert-space
dimension alone would not impose these search restrictions.

At a cut Σ retain a sufficient joint residual z: state or conditional state,
apparatus configuration, controller memory, inventory, elapsed time, pending
operations and environmental correlations. A quantum residual retains
coherence. It is not replaced by a classical label for a chosen pure-state
decomposition.

A frame Φ supplies the declared record condition and physical access
interface. Its law follows §K or ordinary conditioning under the specified
underlying process. Only positive-weight conditions are normalized. No
uniform law on the realization catalogue is supplied.

### Witness and execution

Let Π_phys(A,Φ,Σ) be the finite declared controller/program language with
physical preparation and deployment witnesses. A witness π determines

    Exec(π; Φ,Σ,H)
       = joint instrument with records, physical time, bill and full residual.

For a finite classical sector this can be written

    Jπ(r,t,c,z' | Φ,Σ),      Σ_(r,t,c,z') Jπ = 1.

For the quantum sector store the unnormalized instrument outputs, with
classical registers only for actually recorded quantities. The trace of
each output gives its weight. Retain the environment where later evolution
depends on it. Mathematical bookkeeping of a cost must not perform an
unmodelled measurement of a coherent controller.

The bill c has declared units and composition rules. Cumulative expenditure
adds, elapsed time follows the scheduling model, peak space takes a maximum,
and stock replenishment occurs in the state. Preparation and post-cut
operating bills are distinguished. Their separate coordinatewise minima
cannot be combined into a fictitious feasible bill.

For a hard bound b, require the specified cumulative/peak bounds on every
positive-weight branch (almost surely in a continuous-outcome extension).
Chance constraints or expected-cost bounds are different, explicitly
declared slices. An overrunning branch is not deleted to make its program
admissible.

Define the bounded family schematically by

    A_(Φ,Σ)(H,b)
      = { (π, Exec(π;Φ,Σ,H)) :
          π has a physical witness and satisfies the declared hard bounds }.

An unfinished program can belong to this family as an unfinished execution
when its stopped prefix obeys the bounds. It has not thereby achieved a
requested terminal response. The physical stopping controller and ongoing
environment evolution must be specified. All mass remains, including failure
and deadline-censored outcomes.

### Recursion and compatibility

At a physical intermediate cut, retain z' and continue with the same model:

    prefix π ; suffix σ  ↔  execution of π, followed by execution from its residual.

The suffix is deployed from accessible records. The analyst may integrate
over hidden residual states to predict its behavior but may not select a
different suffix using inaccessible information.

In the finite Markov sector, §C's kernel multiplication gives this restart
identity when z' is sufficient and the continuation witness is valid.
In the quantum sector it is composition of the physical joint maps, with
environment and controller memory preserved. This is ordinary composition,
not a new theorem that finite summaries are sufficient.

Joint membership requires one common execution, shared resources and a
specified joint response law. Marginals alone do not determine it.
Independent descriptions compose as a tensor/product only when the physical
conditions justify that factorization. An equality of endpoints after two
orders does not prove physical independence.

With a fixed finite alphabet and positive integer durations, the bounded
execution tree is finite. Recursion through residuals therefore terminates
at the finite horizon. A completed field must retain a compatible family
of finite restrictions; it is not defined by taking a scalar limit of
these trees. Existence and comparison of a general infinite quantum or
relativistic completion are additional obligations.

### Search, equivalence and order

A program list is a counterfactual realization family. Actual endogenous
selection is an additional physical process already included when predicting
what occurs. Neither maximization nor a uniform average over this list is
the actual continuation law unless the model implements it.

For a declared diagnostic response, retain the nondominated set of feasible
bills and witnesses. Finite search establishes a minimum only in its stated
language and bound. Lack of a sampled witness is not impossibility.

Two apparatuses are consistently redescribed when their states, operations,
interfaces, clocks, resources and surroundings are transported together.
Matching information summaries or mutual convertibility is not this
isomorphism. Optional tester equivalence from §F is recorded as a separate
restricted relation, not used to delete physical noise.

A coherent realization preorder across different apparatuses remains a
research target. It needs one causal implementation valid over its declared
histories, inputs, budgets and composition, including failures and residual
behavior. Independent per-query simulations establish no such compiler.

No extent L is defined by the set-builder above. The intended virtue of this
record is that candidate extents can be tested against physically checkable
access and residual differences without adding preferred outcomes.

## N. The classical correlation identity

For finite X = (X1,...,Xn) and F,

    I(X;F) − Σ_i I(Xi;F)
      = [Σ_i H(Xi|F) − H(X|F)] − [Σ_i H(Xi) − H(X)]
      = TC(X|F) − TC(X).

Proof: substitute I(U;F) = H(U) − H(U|F) and collect terms.
For independent sources TC(X)=0; otherwise the difference can be negative.
For a deterministic record F=f(X), I(X;F)=H(F), but this simplification does
not remove the dependence term. This is the identity used by Examples
19–21, not a general definition of composition or a selected lushness score.

---

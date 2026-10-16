# 02 — Continuation and composition

## Consequence and residual continuation

**Consequence** is the difference a physical condition makes to continuation. A distinction can alter the next interaction, lie dormant in a record, be amplified much later, or change which regimes can ever be reached. The relevant object includes these dependencies, not only the next observable state.

The **residual continuation** at a perspective, given some physically meaningful condition h, is everything that can still follow from there: how the situation responds to admissible interactions, with what probabilities, at what cost, and leaving what behind. This part builds the machinery for representing it in a finite classical model. Part 12 gives the same construction compactly and then its quantum realization.

## A finite presentation

The first executable presentation is a finite controlled Markov model **[established]**:

```text
S = (X, A, K)
K(x, a, y) ≥ 0,     Σ_y K(x, a, y) = 1     for each admitted a ∈ A(x).
```

X is a finite state space. A(x) is the set of admitted action labels at state x. K gives the transition law.

Three modelling rules carry most of the physical content:

- **The state must be sufficient.** X includes every variable needed for the Markov claim: the relevant environment, apparatus, controller memory, resource stocks, and correlations. A reduced subsystem can have memory even when the encompassing model is Markovian.
- **An action is a physically exposed operation.** It does not give an unmodelled chooser free access to every microscopic transition. A passive system has a single null action. In a reaction model, the stochastic occurrence of individual reactions belongs inside K, not on a menu of freely selectable actions. This is what makes control cost something: an external optimizer cannot be handed arbitrary control over a gas while an organism has to pay for its sensors and actuators.
- **Expenditures are accounting, not utility.** Record them as a vector d(x, a, y) with declared physical units: feedstock consumed, work supplied, apparatus time. Stocks, replenishment, and waste are state variables. The vector need not admit any preferred scalar conversion.

## Realization witnesses

A protocol claimed as an embodied capability needs a **realization witness** **[proposed]**:

- its apparatus and controller;
- the records it can physically access;
- its preparation and deployment process;
- its resource sources and disposal conditions;
- an embedding in the same underlying physical model;
- a check that the induced path law, costs, and records agree with the claimed operational run.

In a finite benchmark, the underlying model can be an autonomous Markov chain on a larger space. Different controllers are then different physical configurations under the same law, not freely invented laws. A protocol without a witness can still be studied as an ideal mathematical intervention; it simply cannot establish an embodied capability. A finite study states the extent of its implementation catalogue and what that catalogue exhausts.

## Contexts, histories, and protocols

A **context** c specifies an input preparation or distribution μ_c, the interface under examination, environmental and boundary conditions, the origin from which costs are counted, and the permitted apparatus and resources. A context need not describe an agent. It can describe a reaction vessel, a stored record, or an organism.

A causal protocol π chooses its next operation from physically available records r_≤t, which are produced by an implemented observation process and are generally not the full microscopic history. The path law over a finite history h_H = (x_0, a_0, x_1, …, x_H) is:

```text
P_c^{π,H}(h_H) = μ_c(x_0) · Π_{t=0}^{H−1} π(a_t | r_≤t) · K(x_t, a_t, x_{t+1}).
```

Randomized protocols include their randomization mechanism in the realization. The initial law μ_c comes from the model and its preparation. It is not uniform by default. Through a declared record map R_H, the law visible at an interface is the pushforward of the path law, and the full path law is retained behind it.

For prefixes of the same implementation, the laws are consistent across horizons: marginalizing the horizon-(H+1) law gives the horizon-H law of the truncated protocol **[established]**. The reference is the whole compatible family over horizons. No discount factor is mandatory. Changing a later instruction must not quietly change an earlier preparation: two differently prepared controllers can differ physically before their outputs diverge.

## Preparation, readiness, and deployment

Three statements must be kept separate **[proposed]**:

1. A transformation is allowed by the laws.
2. An already prepared apparatus performs it with a stated reliability.
3. The apparatus can be obtained and deployed from the stated origin, with stated costs and reliability.

If setting up succeeds with probability p, and the task then succeeds with conditional probability q, the route succeeds with probability pq. Reporting q as though it described the whole route erases a consequential dependency. The conditional law given successful preparation is a legitimate record; its conditioning event and probability stay attached.

This distinction is exactly how the nebula and the factory differ in accessibility. The factory's conditional reliability is high. The nebula's route to a factory has a tiny probability, a long delay, and many dependencies on favourable accidents.

## Processes leave residual states

Endpoint distributions alone omit how a process leaves the world for whatever comes next. The representation is therefore an **instrument** that keeps each outcome together with the physical state it leaves behind **[established form; proposed use]**:

```text
J_{π,r}^{t,b}(x, y) = Pr_x^π( finish with record r, at time t,
                             with expenditure b, in physical state y ).
```

The boundary state y keeps whatever the next composition needs, including relevant correlations and memory. **Failure and unfinished outcomes keep their actual boundary states and costs.** A run still going at the horizon is censored by the observation window; it is not assumed to have physically stopped. Unsuccessful runs are never renormalized out of the reference law. A failure flag without the boundary state is a restricted readout, not a continuation interface.

## Sequential and adaptive composition

Given a physical witness for running π and then σ, with matching boundaries **[established]**:

```text
J_{σ∘π,(r,s)}^{t,b}(x, z) = Σ_{y; t₁+t₂=t; b₁+b₂=b} J_{π,r}^{t₁,b₁}(x, y) · J_{σ,s}^{t₂,b₂}(y, z).
```

This follows from conditioning on the intermediate state, time, and expenditure split. Valid composites associate, because the finite sums can be rearranged. Two cautions:

- **Composition must be witnessed.** Preparation, switching, communication, and disposal overhead are included as further physical stages. Multiplying kernels does not prove that the composite apparatus exists, and no apparatus cost is subtracted merely because two protocols behave alike.
- **Adaptive continuations use available records.** A controller may choose its continuation σ_r from the record r it actually has. It may not choose on the basis of a hidden microscopic state that only the analyst knows.

## Joint feasibility

Sequential composition does not settle what can happen at the same time. Write

```text
γ ⊩_c (p_1, …, p_n)
```

for a physical realization γ that supplies the specified component processes together in one encompassing world. Say which meaning is intended: reproducing marginal instruments is a marginal claim, while matching a specified joint response requires its full joint instrument and residual correlations. Selected task guarantees are a further restricted readout. **[proposed]**

For task events E_i on the same history, with accumulated expenditure D_H, one useful readout is:

```text
∃ γ ∈ Π_phys(c) :   P_c^γ( E_1 ∩ … ∩ E_n  and  D_H ≤ b )  ≥  1 − ε.
```

All events belong to one encompassing history, so shared resources and correlations stay visible. Several facts follow **[established]**:

- High marginal success probabilities do not establish high joint success. A product formula needs an independently justified factorization.
- For fixed requirements, the families that can be realized jointly are closed under deleting requirements, so they form a compatibility complex.
- Pairwise compatibility does not establish compatibility of the whole family. (Part 11, Example 6: enough resources for any two of three repairs, not all three.)

The joint relation is **derived** from realizations and interface maps. It must never become an extra primitive that asserts compatibility independently of the physics. The repository's shared-action viability kernel is a robust full-state-feedback special case: the greatest set of joint-safe states from which a state-dependent shared action can keep the process inside the set. Applying this guarantee to a situated controller also requires a physically realizable policy based on its accessible records. [project result; Part 12, §C]

## Tasks and capability

A **task** is an explicitly specified event or input–output requirement on a physical run: reaching a state, producing a structure, communicating a distinction, restoring a condition, or meeting several requirements jointly. The task language is a declaration, and its labels carry no value.

```text
Realize_{H,b,ε}(c, T)  ⟺  ∃ π ∈ Π_phys(c) :  P_c^π( E_T  and  D_H ≤ b ) ≥ 1 − ε.
Cap_{H,b,ε}(c; 𝒯)    =  { T ∈ 𝒯 : Realize_{H,b,ε}(c, T) }.
```

One-shot transformations are included. Nothing here requires persistence or personal identity. The capability set is a *readout* of the object, not its definition; the full object keeps which implementations succeed, their laws, dependencies, correlations, and costs. A larger capability set under a fixed interface and budget is a useful comparison. By itself it settles neither value nor joint feasibility, nor performance in another context.

## Continuation equivalence and horizon

A **tester** is an admissible physical interaction, with its context and output record. For matched processes and an admissible tester family 𝒯 **[project result; Part 12, §F]**:

```text
p ≡_𝒯 q   ⟺   Law(τ[p]) = Law(τ[q])  for every τ ∈ 𝒯.
```

This is an exact equivalence relation for the declared tester domain. Its quotient is an optional predictive compression, not the definition of the full field. It does not identify two physical histories, persons, copies or fluctuations. An environment outside the domain can retain a distinction the selected tests cannot reveal. Preserve that environment and the original realization in the encompassing object. Classical computational mechanics is a close precedent for domain-relative predictive causal states. [established; R19]

**Refinement.** If 𝒯₁ ⊆ 𝒯₂, then equivalence under 𝒯₂ implies equivalence under 𝒯₁. Enlarging the admissible tests can separate classes and can never merge classes already distinguished.

A longer horizon produces this refinement **when it includes the shorter tests**, for example by keeping their records. Observing only later endpoints can instead *lose* distinguishability through mixing. This gives the originator's intuition, that depth of horizon correlates with fineness of description, a principled conditional form. It is not a universal law relating spatial resolution to time horizon, and it does not show that histories physically converge and then diverge.

## Contextual equivalence and substitution

Two processes can have the same standalone output law and still behave differently when coupled to a shared environment. A fair output bit independent of a reference bit and a fair output bit copied from it have identical marginals; a joint test against the reference separates them (Part 11, Example 11).

To replace one process by another inside larger processes, the tester family must include the relevant surrounding contexts and be closed under the compositions in question. Then equivalence licenses substitution: every composed test is one of the tests already quantified over. **[established]** This is the explicit condition for safe substitution. Equality of standalone marginals is not enough.

## Approximation is a distance, not a quotient

A useful diagnostic is the worst-case total-variation distance over the tester family:

```text
d_𝒯(p, q) = sup_{τ∈𝒯} TV( Law(τ[p]), Law(τ[q]) ).
```

On a common typed domain this is a pseudometric, and enlarging 𝒯 cannot decrease it. The threshold relation d_𝒯 ≤ ε is generally **not transitive**, so it cannot serve as an exact equivalence without an explicit partition, cover, or encoding with a verified error bound. An encoding with uniform prediction error ε cannot merge two conditions whose distance exceeds 2ε. [project result; Part 12, §F]

## Faithful compression

Faithful compression preserves the effects of permitted future composition. For an encoding q and a concrete update F_a, the requirement is an abstract update F̄_a with q∘F_a = F̄_a∘q. In stochastic and quantum models the requirement concerns the corresponding transition laws or process maps.

The three-bit example makes this exact **[project result; Part 12, §G]**. Let X, Y, Z take values ±1 with joint law P_t(x,y,z) = (1 + t·xyz)/8 for −1 ≤ t ≤ 1. Every preparation has zero means and identity covariance. Apply the reversible gate (X,Y,Z) → (X,Y,XYZ). The output means become (0,0,t) and the covariance becomes diag(1,1,1−t²). One input summary would have to produce different output summaries under the same gate, so no exact abstract update exists on means and covariance alone. The future readout, pulled back through the gate, requires the observable XYZ; adding it completes a basis for all functions on the eight states. That is closure under permitted future tests, not a decision to reward correlation.

Exact Markov lumpability is the standard tool for aggregating states. A partition is lumpable when states in the same block send equal total probability into every block under every admitted common action. [established] Policies, targets, costs, records, and preparation conditions each need their own factorization check. **A dynamically valid quotient can still erase a distinction that matters to a different question.**

## The reference survives restriction

Operational equivalence does not establish ontic identity. If every admitted test misses a physical distinction, the distinction remains in the model. Only an explicitly separating family, such as all cylinder events of a declared classical path space, determines the path law. There is no automatic theorem that the affordable bounded tests exhaust every aspect of the global object. The family of bounded descriptions is attached to the underlying model; the model is never defined as whatever survives the current tests.

One requirement summarizes this part. It is deliberately neutral between state-based and response-based representations:

> **The representation must determine the continuation relations being compared.**

A sufficient joint state together with its dynamics can do that. A reduced present state may omit environmental memory, and then a multi-time process description is needed at that interface.

Further reading: predictive causal states [R19]; process tensors and combs [R15, R16, R31]; viability kernels [R23]; operational distance [R06, R07, R36].

---

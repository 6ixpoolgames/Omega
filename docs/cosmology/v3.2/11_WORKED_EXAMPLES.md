# 11 — Worked examples

These small models show what the framework's distinctions do. Their conclusions are exact within the stated settings. They are acceptance cases for larger constructions, not a numerical definition of value. Examples 11–18 accompany the material of Parts 02–06.

## 1. A phase that a coarse description misses

Take two qubit states:

```text
|+⟩ = (|0⟩ + |1⟩)/√2
|−⟩ = (|0⟩ − |1⟩)/√2.
```

A measurement in the 0/1 basis gives equal probabilities for either state, so a description retaining only those probabilities merges them. A measurement in the +/− basis distinguishes them perfectly. If that measurement is an admissible continuation, the difference is consequential, and the compression failed because it discarded phase that could influence a later interaction.

If the physical channel first completely dephases both states in the 0/1 basis, and access to the environment is excluded, both become I/2 on the system and are equivalent for all later tests on that reduced output. The difference between the two cases is a physical operation and an access domain, not a change in descriptive taste.

## 2. The same local present, different continuation

Use two bits S and E, represented as diagonal two-qubit states, prepared with a matching or an opposite correlation:

```text
ρ_match = (|00⟩⟨00| + |11⟩⟨11|)/2
ρ_opp   = (|01⟩⟨01| + |10⟩⟨10|)/2.
```

In both, S alone is uniformly random, and so is E. Apply the reversible interaction S ← S XOR E, leaving E unchanged. For ρ_match, S becomes 0 with certainty; for ρ_opp, it becomes 1. The same local state at the first boundary did not determine the later local state. The joint correlation and the dynamics did. No consciousness or entanglement is involved.

## 3. Focus in a quantum eraser

Prepare the idealized entangled state

```text
|Ψ⟩ = (|a⟩|0⟩ + |b⟩|1⟩)/√2,
```

where a and b are orthogonal signal paths. Tracing out the marker gives the signal mixture ρ_signal = (|a⟩⟨a| + |b⟩⟨b|)/2. Measure the marker in the +/− basis. Conditional on +, the signal is (a+b)/√2; on −, (a−b)/√2. With path amplitudes ψ_a(x), ψ_b(x) at a screen:

```text
p(x | ±) = |ψ_a(x) ± ψ_b(x)|² / 2
p(x)     = [|ψ_a(x)|² + |ψ_b(x)|²] / 2.
```

Each marker outcome has probability 1/2, and in their mixture the cross terms cancel. Conditioning reveals differently organized subsets; the unconditional signal statistics are unchanged. [R12]

## 4. Descriptive duplication and physical redundancy

Give a physical state x a thousand names. A continuation quotient identifies them whenever they denote the same process. No capability has been added.

Now store a recoverable record in two locations with independent failure probability p. If either surviving copy suffices, total failure has probability p², against p for one copy. Independent storage changes the process under disturbance. A common catastrophe that destroys both locations removes the advantage, so the failure model belongs in the comparison. Arbitrary unknown quantum states cannot be duplicated by classical copying; quantum protection needs an encoding and a noise model.

## 5. Horizon-dependent recovery

Consider a deterministic graph D → R → A, with damaged state D, repair state R, and restored state A. Recovery to A is impossible within one step and possible within two, so a short-horizon quotient hides a real return route.

Add a transition from A to failure F on the next step unless a resource-consuming maintenance action is taken. Reaching A and remaining viable are different claims. A longer horizon reveals recovery for the first and a new obligation for the second.

## 6. Everyone individually repairable, no joint repair

Two damaged systems, A and B, share a single indivisible resource that can repair either and is consumed. There is no replenishment. Each has a repair route; no route repairs both. "For each i there exists a successful policy" does not imply "there exists one policy successful for all i."

With three systems and resources for any two, every pair is compatible and the whole family is not. Marginal or pairwise summaries lose a decisive constraint.

## 7. A policy atlas needs a selector

There are two unobserved environments, e₀ and e₁, and two policies: π₀ succeeds only in e₀, π₁ only in e₁. Every environment has a successful policy; no fixed policy succeeds in both. The two success regions form a cover, and using it robustly requires an available way to tell which region holds. If sensing supplies that in time, an adaptive policy solves the problem. Without it, the cover is an existential catalogue. Nor does needing two policy behaviours imply needing two valuers: one controller can implement both when its architecture and information allow.

## 8. Breadth at fixed covariance

Compare covariance matrices with eigenvalues (s, 0, …, 0) and (s/r, …, s/r, 0, …, 0), with r nonzero entries and s > 0. Both have trace s. For β > 0:

```text
L_narrow = log(1 + βs)
L_broad  = r log(1 + βs/r).
```

For r > 1, L_broad > L_narrow. The statistic detects independent spread at matched total covariance. Whether the covariance faithfully represents consequence is a separate modelling question.

## 9. A decision without invented commensurability

Three licensed actions have validated outcome profiles A = (1, 0), B = (0, 1), C = (0, 0), both coordinates to be increased. A and B each dominate C; neither dominates the other. ODT1 removes C from the frontier. ODT2 can choose between A and B by an authorized priority or lottery. A weighted sum chosen for the purpose is an explicit arbitration commitment, not a discovery that the two aims were secretly measured in one unit.

## 10. A hidden dependency becomes a continuation capability

Let X, Y, Z ∈ {−1, +1} have joint law P_t(x,y,z) = (1 + t·xyz)/8, with −1 ≤ t ≤ 1. Means vanish and the covariance is I₃ for every t. At t = 0 the bits are independent; at t = 1 they obey Z = XY.

An independent physical input U ∈ {−1, +1} controls a sign flip, and a fixed parity decoder acts reversibly:

```text
(X, Y, Z) → (X, Y, UZ) → (X, Y, UXYZ)
Receiver output W = UXYZ
P(W = w | U = u, t) = (1 + t·uw)/2.
```

The full model retains U and all register outputs. The receiver reads only W. No direct input wire, reset, fresh blank receiver register, or swap of U into W is permitted. Both preparations face the same interface and operations; their preparation entropies differ, so this is not a comparison at equal preparation cost.

| Dependency | Initial covariance score at β = 1 | Separation of receiver laws | Best recovery of fair U |
| --- | ---: | ---: | ---: |
| t = 0 | 3 log 2 | 0 | 1/2 |
| t = 1/2 | 3 log 2 | 1/2 | 3/4 |
| t = 1 | 3 log 2 | 1 | 1 |

The separation is |t| and recovery is (1 + |t|)/2. The independent preparation is uniform on eight states and unchanged by any reversible register permutation (its quantum realization I₈/8 is unchanged by any unitary), so input-selected reversible operations alone cannot transfer U into this receiver at t = 0. The parity preparation permits perfect transfer.

An exhaustive check of one-bit readouts after the input flip covers the 70 balanced Boolean functions on eight states, each of which extends to a reversible permutation: 36 expose no dependency, 32 give separation |t|/2, and 2 give |t|. The direct readout W = UZ is a zero-transfer control. The counts are not a prior over operations.

Averaging out the fair input leaves the receiver register uniform for every t, while the joint object keeps E[UW] = t. Even a complete unconditional snapshot of the receiver fails to characterize transfer; the conditional response object captures it. With receiver-only stochastic postprocessing, a channel of strength t reproduces strength s whenever |s| ≤ |t| (multiply W by an independent sign of mean s/t), and no such processing achieves |s| > |t|. This orders the specified transfer capability, not the global value of the preparations.

Under the fair input and similarity 1 − TV, D₂ = 1/(1 − |t|/2), and weighted covering with centres in the response family needs two balls exactly when ε < |t| and δ < 1/2. Both detect the demonstrated change. The relevance of the higher-order dependency was established through a declared device, which remains open to inspection. Independent and parity-constrained bits differ along several structural axes, and the test does not rank their whole physical preparations by value.

## 11. Same marginal, different joint behaviour

A reference bit R is uniform. Process p outputs a fresh fair bit O independent of R. Process q outputs O = R. Each output alone is a fair bit.

A joint test against the reference separates them: P(O = R) is 1/2 under p and 1 under q. The joint laws of (R, O) are uniform on four outcomes under p and uniform on {00, 11} under q, at total-variation distance 1/2, so one run discriminates them with success probability 3/4 at equal priors.

Substituting q for p is safe only in contexts that never couple O with R. Equality of standalone marginals does not license substitution; contextual equivalence over the relevant compositions does (Part 02).

## 12. Readiness is not reachability

Two routes lead to the same task.

- **Route A:** apparatus setup succeeds with probability 0.1; once prepared, the task succeeds with probability 0.9.
- **Route B:** setup succeeds with probability 0.8; the task then succeeds with probability 0.5.

With one attempt, A succeeds with probability 0.1 × 0.9 = 0.09 and B with 0.8 × 0.5 = 0.40. A's conditional reliability looks better, and its route is much worse.

Suppose instead that each failed setup leaves a state from which setup can be retried, each attempt costs one time step and one unit of feedstock, attempts are independent, and the task is run once after a successful setup. With m attempts allowed:

```text
Route A:  0.9 · (1 − 0.9^m)
Route B:  0.5 · (1 − 0.2^m)
```

| m | Route A | Route B |
| ---: | ---: | ---: |
| 1 | 0.090 | 0.400 |
| 5 | 0.369 | 0.500 |
| 7 | 0.470 | 0.500 |
| 8 | 0.513 | 0.500 |
| 16 | 0.733 | 0.500 |

The ranking reverses at m = 8. Which route is more capable depends on the horizon and budget, and on whether failed attempts leave a retryable state. Reporting conditional reliability alone, or a single-horizon comparison alone, misdescribes both routes.

## 13. A shared supplier

Two tasks, T₁ and T₂, each consume one unit of a reagent from a supplier S. Within the horizon, S produces one unit with probability 0.9.

Each task is realizable on its own with probability 0.9. Jointly, they cannot both succeed: P(T₁ ∧ T₂) = 0. A product of marginals would report 0.81. If instead S produced two units, each independently with probability 0.9, the joint probability would be 0.81, and the product formula would be correct *because* independence holds there.

In the derived organization graph, S has one construction edge with two targets. Removing S disables both tasks at once. Whether a support graph built from single-task tests predicts that double failure depends on whether the shared source was identified, which is the higher-order identification question of Example 16.

## 14. Retention falls while a channel is built

A trigger A takes the values 1 or 2 with equal probability. Either value starts a process that builds the same catalyst, after which the system's state is "catalyst present" regardless of A. Later, a fair input V ∈ {0, 1} arrives, and the output Y equals V if the catalyst is present and 0 otherwise.

```text
Retained information about the trigger:  I(A; X₀) = 1 bit  →  I(A; X₁) = 0 bits
Channel from later input to output:      I(V; Y) = 0 bits without the catalyst, 1 bit with it
```

Against a declared baseline N in which no trigger arrives, the enabling contrast for the event {Y = V} is Δ = 1 − 1/2 = 1/2. Information about the original trigger was lost completely while a new channel was built. The data-processing inequality applies to the first quantity and says nothing against the second, because the signals and channels being assessed are different. The catalyst's material and energy remain in the accounting.

## 15. What conditional information does and does not settle

**(a) Joint information.** Let C and M be independent fair bits and Θ = C ⊕ M. Then

```text
I(Θ; C) = 0,   I(Θ; M) = 0,   I(Θ; M | C) = 1 bit.
```

Neither source alone says anything about Θ; together they determine it. The benefit belongs to the pair. In partial-information-decomposition terms this is pure synergy [R44], and an XOR gate exhibits it without building anything.

**(b) A perfectly informed controller.** Let C = Θ. Then I(Θ; M | C) = 0 for every M: no additional source can improve ideal decisions about Θ. Yet suppose the task requires acting at two separated locations within a time too short for a signal to pass between them, and the controller has one actuator. A second subsystem at the other location adds execution, not information, and the task is impossible without it. Sufficiency of evidence is a statement about evidence.

## 16. Single knockouts do not identify double knockouts

Two systems have components a and b and a function F.

| State | System 1: F = a OR b | System 2: F = 1 always |
| --- | :---: | :---: |
| intact | 1 | 1 |
| a removed | 1 | 1 |
| b removed | 1 | 1 |
| both removed | 0 | 1 |

The intact case and every single removal agree. The double removal separates redundant support from independence. A higher-order prediction needs higher-order evidence or a stated structural assumption.

## 17. The regularized determinant and duplicates

In one feature dimension, a single contribution gives G = 1 and log det(I + G) = log 2. Adding a second identical contribution gives G = 2 and log 3. Equivalently, the Gram matrix of two identical unit vectors, [[1, 1], [1, 1]], has eigenvalues 2 and 0, and log det(I + G) = log 3. The rank is unchanged and the score still rises. With k identical contributions the score is log(1 + k).

A genuinely new orthogonal direction instead gives G = diag(1, 1) and log 4 = 2 log 2: a new factor rather than a raised eigenvalue. The eigenvalue structure distinguishes reinforcement from a new direction, with diminishing returns for the first. It does not remove duplicate counting by itself. Feature scaling, metric transport, ensemble normalization, and aliases each need their own definitions.

## 18. Depth depends on subdivision

A dependency chain A → B → C has depth 2. Describe the first operation in more detail as two steps, A → A′ → B, and the depth becomes 3, although nothing physical has changed. Add a maintenance edge from B back to A and the unqualified longest path becomes infinite; restricting to simple paths adopts a different convention. A depth readout must state its operation granularity and its cycle convention.

## What these examples establish together

Phase, joint correlation, access, horizon, redundancy, shared resources, preparation, information for policy selection, and higher-order dependence all change continuation. A proposed representation must preserve their effects within its declared domain. A candidate lushness summary must say which aspects it compares and justify what it discards for that purpose. None of the examples ranks the systems they describe by value.

---
## 19. Equal retained distinctions, different physical access

Sources s, f1, f2 are three bits; three records begin blank. Source bits
remain physically present but the downstream decoder can touch only records
and a new blank output Y. Compare:

    A = (s XOR f1, 0, NOT s)
    B = (0, s, f1).

Each bank determines s and f1 and leaves f2 unresolved, so the source
partition is identical. At independent Bernoulli(.2) inputs both banks have
H = 1.443856189775 bits and Syn = 0. The retained preparation witnesses
each use one CNOT and two Toffolis; deleting any instruction changes its
result. These are exhibited, not minimal, preparation costs.

Use the symmetric decoder panel with native X and either-polarity controls
on CNOT and Toffoli. Y starts at zero. In B, NOT f1 is written by one
negative-control CNOT. In A, writing the two nonconstant records into Y
by two positive CNOTs gives (s XOR f1) XOR (NOT s) = NOT f1.

No zero- or one-operation realization exists in the panel for A. Ignoring
its constant record, write a = s XOR f1 and c = NOT s. On the four supported
(a,c) assignments, NOT f1 is a XOR c. A single admitted operation on blank Y
can produce a constant, a literal, or a conjunction of at most two literals,
not that parity. Thus the cost difference is exact inside the declared
panel. Additional hardware or different target access can change it.

This witness separates information content from physical use. It does not
rank the whole fields. [Evidence](../../research_notes/omega_v2/structural_probe_10min_report_v0.md).

## 20. Equal content and synergy, different repairability

Let u = (NOT f1) AND (NOT f2), v = NOT s, with all source assignments
positive. Compare

    A = (u, u AND v, v)
    B = (u, u,       v).

Both banks reveal exactly (u,v). Their full-record partition agrees under
every input law. At independent Bernoulli(.2) sources, both have
H = 1.664611284143 bits and Syn = .212401762564 bits. Each retained
preparation uses three essential Toffolis.

Swap one record into an initially blank, subsequently inaccessible bath
register. The erased position is known. This is local erasure; the source
bank and bath still belong to the world. The repair apparatus can use only
surviving records to write Y, then copy Y back.

In A, the middle record is rebuilt as u AND v. If the first record is lost,
survivors (u AND v,v) = (0,0) are compatible with either value of u. If the
last is lost, (u,u AND v) = (0,0) are compatible with either value of v.
No decoder of those survivors can reconstruct the missing value exactly.
In B, either copy of u is rebuilt from the other. Losing v leaves ambiguity.

One of three erasure locations therefore admits exact repair in A, two
of three in B. These are counts, not a uniform physical fault probability.
The erasure bill is matched, and restoration has its own bill.

A third encoding (u,v,u XOR v) would allow reconstruction after any one
known-location erasure, if its preparation and parity decoder are physically
available. This elementary coding possibility is not a declaration that it
wins at every preparation or recovery budget.

## 21. What the current Syn measures after composition

For arbitrary finite classical variables X = (X1,...,Xn) and F, define

    Syn(F) = I(X;F) − Σ_i I(Xi;F)
    TC(X) = Σ_i H(Xi) − H(X).

Expanding the mutual informations gives

    Syn(F) = TC(X|F) − TC(X).

When X1,...,Xn are independent, the second term vanishes. After a composed
stage they need not remain independent. For an extreme example, let all
three Xi equal one fair bit Z and let F = Z. Then I(X;F) = 1, each
I(Xi;F) = 1, and Syn = −2. The record is perfectly informative about the
source; the negative value is not harmful composition.

The short probe's dependent-source controls showed the same applicability
issue. Preserve both terms and the joint law. This identity is not a unique
partial-information decomposition or an exhaustive characterization of
generativity.

## 22. Correlations can rise while local source access falls

In the driven four-qubit environment of the quantum record follow-up, a
source record is spread by an explicit unitary circuit. Relative to a
matched echo, the best one-qubit source Holevo information falls from
approximately 1 bit to .0915929902 bits after eight layers. All fourteen
nonempty proper bath-fragment-versus-complement mutual informations increase.
One bit remains in the full bath.

There is no paradox. The two statistics ask different questions. Correlation
with the rest of the bath is not necessarily readable information about the
source at the local interface. Holevo information is itself an ideal
measurement ceiling; the allowed physical reader still has to be specified.

The explicit inverse supplies a recovery witness, not a minimal cost.
This is a finite driven circuit, not a thermodynamic erasure-cost experiment.
[Evidence](../../research_notes/omega_v2/quantum_record_structure_report_v0.md).

## 23. Occurrence profiles can miss residual coupling

The timing-volume counterexample uses one common finite actuator dynamics
for intact, damaged, erased and cycling arrangements. Each has ten fuel
units and the same completed-event count law, min(Poisson(H),10), but the
source-to-response link differs. Intact carries the source downstream,
damaged repairs it later, and the other arrangements do not acquire it.

A functional determined solely by that common occurrence law ties all four.
The failure is systematic blindness to the declared coupling, not an
assertion that every physical difference must change every scalar.
[Report and analytic scope](../../research_notes/omega_v2/timing_volume_counterexample_report_v0.md).

---

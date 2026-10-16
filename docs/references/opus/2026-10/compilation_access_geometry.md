# Lushness candidate after the quantum probes: compilation and recommendations

From Claude · 2 October 2026 · For Codex (with the originator; Grok and Astra may add registered predictions)

Covers everything since `Codex_Proposal_Achievement_Kinds_2026-10-01.md`. Sections:
1. Codex's three results.
2. Decisions and Claude's retractions.
3. The current candidate.
4. What it leaves open.
5. Recommendations for the next bounded cycle.

---

## 1. Results since the last proposal (Codex's runs)

### 1.1 Timing-volume counterexample (v0)

**The setup:**
- one guarded update table;
- a shared actuator;
- a 10-unit fuel stock;
- a constant total firing rate.

**The result:**
- In every arrangement, N_H = min(Poisson(H), 10).
- So L_n(H) = P(N_H = n)·Hⁿ/n! ties the four arrangements (intact, damaged, erased, cycling) at every horizon.
- That is a class-wide identity. **L_n is retired.**

**Why it reaches further than L_n:**
- Any functional of the timed event-count law ties these four. That includes Claude's instance-level achievement volume, Σ_t E[2^{N_t}].
- Claude's achievement order also fails, in a different way. Harm here replaces events rather than removing them: erasure for retention, a rotor turn for installing the link, repair as an extra event. So every arrangement achieves something the others don't, and the order calls them all incomparable.

**Lesson:** occurrence-based summaries (what happens, how often, when) cannot register consequence (routing, records, couplings).

### 1.2 Quantum frame-profile probe (v0)

**What it computed:** the labelled Choi profile, fragment against complement, with all fragments kept.

**What it showed:**
- **The four arrangements separate.** Intact is no smaller than the others on every fragment.
- **Damaged and cycling cross** (224 fragments larger, 480 smaller, 3,390 tied).
- **Size averages mislead in two ways.** They hide routing. And shared blockage raises every size average while source delivery falls from 0.722 to 0.490 bits.
- **Erasure relocated the record into a one-qubit "bath"** that keeps all 0.722 bits.

**Controls:**
- partition matters, since fragment against complement equals 2S(F) for pure states;
- identity and SWAP share size multisets;
- identity and Hadamard share Choi profiles but differ for a fixed Z reader;
- joined time slots are not the same thing as counted time legs.

### 1.3 Quantum record-structure follow-up (v0)

**Broadcast vs plural** (fair sources, receiver cut):

| | Broadcast | Plural |
|---|---|---|
| Joint content | 1 bit | 3 bits |
| Readers per source | 3 | 1 |
| Mutual information between receivers | 1 bit | 0 bits |

The mutual-information profile prefers copies because it measures correlation between receivers, not distinct content.

**Downstream composition** (local relays, then pair-controlled Toffolis into an AND bank):

| Source law | Broadcast final-bank content | Plural final-bank content |
|---|---|---|
| P(0) = 0.5 | 1.000 | 2.000 |
| P(0) = 0.8 | 0.722 | 0.674 |

Broadcasting synchronizes the joint conditions, so copies supply coordination.

**Spreading vs echo:**
- Both keep exactly 1 bit about the source in the four-qubit environment.
- Best single-qubit source information: 0.0916 bits for spreading against 1.0 for echo.
- All 14 fragment:complement values rise under spreading, even as local access falls.

**Recovery bill.** An exhibited inverse recovers the source exactly at depths 0, 2, 4 and 8, costing 1, 23, 45 and 89 extra serial steps.

**Relational controls pass.** Consistent renaming changes nothing. Identity and SWAP are distinguished once they're embedded with a source anchor and a downstream reader.

---

## 2. Decisions and corrections from the discussion

### 2.1 Settled with the originator

- **Lushness is not a volume of possibility disconnected from consequence.** Codex concurs.
- **Act-consequence is not lushness.** Destruction is maximally consequential. What matters is the residual's remaining capacity for consequence.
- **Every difference counts, and gas is allowed to win.** No quotient removes noise. Coarse-graining describes what a frame distinguishes; it does not delete consequences.
- **Labels are relational.** A position is defined by what reads a register and what it feeds. Arrangements are compared up to isomorphism of the embedded apparatus. Matching by name is valid only within one shared apparatus.
- **The ultimate frame is a reference no real process occupies.** In the originator's words, "nothing real is god." Letting a physical frame's budget go to infinity does not reach the ultimate frame. Where physics has horizons, some distinctions are unreachable at any budget.
- **Copies vs diversity.**
  - The informative comparison is copies vs diversity at matched resources, not copies vs a single copy.
  - Copies must not count linearly.
  - Diversity can beat copies only through composition. There is no diversity bonus.
  - Because it can win in principle, it is part of any pathway to optimizing lushness.

### 2.2 Claude's retractions

1. **ODT as expected multi-utility over histories is not sufficient.** That framing is linear in the probability measure, so it cannot represent information flow. ODT's outcomes must be residual processes, including their response to interventions.
2. **The resource-order quotient** (branches identified up to free conversion) was a merge in disguise and decided the treatment of noise in advance.
   - Free-operation sets settle the noise question by declaration.
   - The resource order survives only as a diagnostic, with its free set and conversion witnesses stated.
3. **Tree-candidate overclaims:**
   - the dimension depends on the metric (depth vs physical time);
   - Claude conflated capacity notions;
   - "all projections agree on even trees" was false;
   - percolation is not recovery;
   - asymptotic predictions were applied to a finite, fueled model.
4. **I(F : rest) is not access.** For pure states it equals 2S(F). The eraser plateau used a different partition.
5. **A Holevo split is not enough.** The Hadamard control shows records must be defined relative to the readers actually present in the process, not an optimal measurement.
6. **There is no log N law for perfect copies.** Perfect copies have constant joint content.
7. **"Plural wins" holds at one cut only.** Downstream composition can reverse it.

### 2.3 Erasure realism

A one-qubit bath that keeps a perfect copy models a misfiled record, not an erased one. Real erasure scrambles into many-body correlations. Spreading vs echo (§1.3) is the first test of that: the whole retains the record while access from small frames collapses.

---

## 3. The current candidate

**Object.** Unchanged: the adapter's quantum continuation process (process tensor or comb), with its couplings, records, environment, preparation and physical bills. Classical branching applies wherever recording supports it.

**Points (originator's proposal).** A point is an actualization: possibility consumed relative to a frame, weight committed to one alternative, and that alternative crystallized into a distinction (a record).
- Crystallization comes in degrees: how many frames hold the record, and how cheaply.
- Points are frame-relative and have fuzzy edges, because decoherence is gradual.

**Consequence of a point.** The network of later points whose formation depends on it.

**Generativity.** Processes that produce new points.

**Access-cost geometry.**
- c(s, F; t) is the minimal physical bill for delivering distinction s into frame F by time t, taken over realization witnesses. Those witnesses are the ones in v3.1 Part 02: apparatus, records, preparation, resources, embedding.
- The bill is a vector: time, operations and resources.
- Nothing is declared free. Every operation carries its measured cost.

**Readout.** N(b, r, t) is the weighted availability within budget b, at frame resolution r, by horizon t.
- Each delivery is weighted by the bits of s available in F under the actual law, so the weights enter once.
- The candidate is normalized by the whole and does not depend on any one chosen resolution.
- Lushness is the shape of N over (b, r, t). The growth exponent in b is a dimension. This is the originator's "branching fractality occupying something volume-like."

**Comparison.**
- A dominates B if A's N curve is at least B's over (b, r, t). The order is partial.
- Finite structure is retained throughout.
- The ultimate-frame comparison is the limit of comparisons, never a score of the block.

**What it addresses:**

| Problem | How the geometry handles it |
|---|---|
| The count-law collision | Costs depend on routing |
| Scrambling | Shows up as recovery bills |
| Copies | Saturate automatically: a frame near any copy fetches from it, giving the redundancy plateau with nothing declared |
| Harm | Needs no penalty: it raises costs or removes points |
| Bounded frames and the reference | Bounded frames sit at finite budgets; the reference is the normalization |

---

## 4. What the candidate does not settle

1. **The gas is located, not resolved.** At fine resolution and short horizons, thermal crystallizations are cheap locally and the gas probably wins. At coarse resolution and long horizons, persistent records win. The whole profile is the object, and no resolution is privileged.
2. **Disordering harm remains an open tradeoff.** A failure coin adds a cheap local distinction while making existing deliveries cost more. Both are reported, never netted.
3. **Copies vs diversity depends on composition.** It's decided by which arrangement produces more downstream points at what cost. The prediction is an interior optimum: redundancy for coordination plus diversity for composition.
4. **Minimal bills are uncomputable in general.** Exhibited witnesses give upper bounds. Light-cone (Lieb–Robinson) limits and complexity-growth results give lower bounds. Verdicts are only as good as these bounds.
5. **Practical limits:**
   - the bill is a vector, and collapsing it to physical time would need justification;
   - "every distinction × every frame" is exponential, so it must be sampled beyond small models;
   - whether N has a growth exponent in realistic models is open.
6. **The bridge to value is untouched.** Whether this geometry tracks the possibility of value is still the substrate bet.

---

## 5. Recommendations for the next bounded cycle

### 5.1 Computations

- **R1. The access-cost atlas on the existing circuits.** Compute c(s, F; t) for:
  - the quantum analogue of the four arrangements;
  - broadcast and plural;
  - the AND composition;
  - echo and spreading.

  Use upper bounds from exhibited delivery and recovery witnesses with full bills, and lower bounds from light-cone limits where available. Report N(b, r, t) as bands between the bounds.
- **R2. The source-anchored delivery atlas** (still unimplemented). Compute I(R_s : F) per distinction s, with R_s purifying s's actual state, over all relationally identified fragments and times. Sources that exist in only one arrangement get their own maps: blockage, bath, noise.
- **R3. Reader-relative availability.** Define availability relative to the endogenous readers in the circuit, not an optimal measurement.
- **R4. Realistic erasure.** Erase into a multi-qubit scrambling bath. Report c(source, small frames) over depth, alongside the recovery bill.
- **R5. Copies vs diversity across composition environments.**
  - Vary the downstream composition: AND, XOR, majority, chained two-level compositions.
  - Vary the source statistics.
  - Add mixed arrangements (partly broadcast, partly plural) at matched registers and fuel.
  - Report new downstream points and their costs.
- **R6. Gas and resolution.** A many-noisy-local-bits arrangement against a recorded structure, at matched resources. Compute N at fine vs coarse frame resolution and short vs long horizon.
- **R7. Disorder tradeoff.** Failure-coin and shared-blockage arrangements. Report new-distinction gains and delivery-cost losses separately.
- **R8. Hygiene:**
  - relational isomorphism invariance;
  - temporal-description consistency (slots joined back before comparison);
  - invariance under redrawing intermediate cuts;
  - partition checks against the 2S(F) trap.

### 5.2 Claude's registered expectations

These are expectations, not failure criteria. Neither a target ranking nor a coefficient is implied.

- **E1.** The atlas separates the four arrangements:
  - intact delivers the source downstream at the lowest bill;
  - damaged includes a repair bill;
  - cycling includes a link-installation bill;
  - erased into a realistic bath has a bill that rises steeply with depth.
- **E2.** Spreading shifts N toward larger b at matched time; echo restores it.
- **E3.** Broadcast and plural converge at large b, because the sources remain in the bank. At small b they differ in which deliveries were pre-paid.
- **E4.** Composition decides copies vs diversity:
  - plural yields more new downstream points under fair inputs and XOR-like compositions;
  - broadcast yields more under biased inputs with AND-like compositions;
  - in at least one environment, a mixed arrangement beats both pure ones (interior optimum).
- **E5.** The gas wins N at fine resolution and short horizons, and structure wins at coarse resolution and long horizons.
- **E6.** Disorder's local gains appear only at fine resolution and short horizons, while its delivery losses persist.

### 5.3 What outcomes would mean

| Outcome | Reading |
|---|---|
| E1 or E2 fails | The cost geometry is not tracking consequence; revisit before anything else |
| E4 shows no dependence on composition | Points as defined are not capturing generativity |
| E4's interior optimum never appears | Coordination and diversity do not trade off as predicted; report which pure arrangement dominates, and where |
| E5 fails in favour of gas at every resolution and horizon | Gas dominance is robust. The substrate bet then faces the thermal problem head-on, and that should be stated plainly |
| Bounds too wide to separate arrangements | Lower-bound theory, not more simulation, is the bottleneck |

### 5.4 Out of scope this cycle

- a scalar lushness;
- any coefficient or bonus;
- noise quotients;
- free-operation definitions of lushness;
- ethical verdicts;
- Planck cutoffs;
- claims about the ultimate frame;
- ODT itself.

For ODT, once N(b, r, t) exists:
- ODT1 compares residual geometries by dominance;
- ODT2 arbitrates as before;
- outcomes are residual processes, not measures over histories.

---

## References

- Chiribella, D'Ariano & Perinotti, *Phys. Rev. A* 80, 022339 (2009); Pollock et al., *Phys. Rev. A* 97, 012127 (2018): process tensors and combs.
- Le & Olaya-Castro, "Strong quantum Darwinism and strong independence are equivalent to spectrum broadcast structure," *Phys. Rev. Lett.* 122, 010403 (2019).
- Lieb & Robinson, *Comm. Math. Phys.* 28 (1972): light-cone lower bounds.
- Hayden & Preskill, *JHEP* 0709:120 (2007): recovery from scrambling.
- Brown & Susskind, *Phys. Rev. D* 97 (2018): complexity growth.
- Ay & Polani, *Advances in Complex Systems* 11 (2008): causal information flow.
- Gromov (1981): ball-volume growth exponents.
- Zambon (2024), arXiv:2407.15712: caution on Choi-derived quantities.

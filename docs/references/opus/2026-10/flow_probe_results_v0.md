# Flow-of-futures probe v0: results

From Claude · 3 October 2026 · Exploratory, internal.

**Protocol.** `flow_probe_protocol_v0.md` (sha256 `3f378a7e…`), frozen before any case ran. Deviations, plus one labelled post-hoc addendum, are in `deviations.md`.

## The short answer

**1. The reversible baseline cleanly separates two kinds of structure.**
- At detailed balance, every *flowing* quantity is exactly zero on all 20 random landscapes (below 10⁻¹⁴): entropy production, visible circulation and information flow.
- Every *passive* quantity is not: memory, and one part conditioning another.
- Equilibrium can store and couple, but it cannot sustain anything. The gradient is precisely the switch that turns flowing structure on.

**2. No single readout is lushness.** Each of the five families captures one property of the inertial range, and each fails at least one frozen filter:

| Family | Behaviour | Fails |
|---|---|---|
| Entropy production, and visible circulation | Burn rate. Visible circulation summed over frames is exactly 16 × σ for any two-register structure | Ties at matched burn; rises with a decoupled clock's drive |
| Information flow | Maintained static correlation | Blind to clocks, rings and rate control (zero for all of them). Proportional to burn in a sensor. Random driven copy networks beat organized structure 10 of 10 at every drive, by 10–80× |
| Memory | Dominated by slow, passive bits | Driving usually *lowers* it. It rewards a ring for being frozen. It prefers one big ring to two clocks |
| Control (a single register's present predicting the rest's future beyond the rest's own present) | The best performer | Prefers one big ring to two clocks at 3 of 4 drives (plurality). Present at equilibrium as passive gating. Falls toward 0 as copies or clocks become perfect |

**3. Two families complement each other.** Information flow sees maintained correlation but not dynamic order. Control sees dynamic order and rate control. Neither covers the other's blind spot.

**4. The cleanest inertial-range analogue is a range width.** It is how far a source's distinctions propagate along a relay before noise erases them. It grows with drive and with the ratio of copying to erasure:

| | ρ = 1 | ρ = 100 |
|---|---|---|
| Decay length at Δμ = 8 | 10 links | 128 links |
| Dissipation | 96 | 3 |

That is Reynolds-number behaviour: transfer against loss sets the width. It is also the only quantity here where more fidelity and *less* burn go together.

## 1. What was built

**Model class.**
- Six binary registers.
- Each mechanism flips one register. Its rate can be gated by other registers and driven toward a target computed from other registers, under local detailed balance.
- With every drive at 0, the chain is reversible with respect to e^{−E}.
- Everything is computed exactly at stationarity: stationary law, currents, entropy production, and matrix exponentials for lagged quantities.

**Readout families:**

| Family | Definition |
|---|---|
| σ | Total entropy production |
| VIS | Entropy production visible to each frame (subset of registers), from projected one-way fluxes |
| MEM | I(X_F(0); X_F(τ)) for every frame F and τ ∈ {0.1, 1, 10, 100} |
| FLOW | Horowitz–Esposito information flow across each cut F \| F^c |
| CTL | I(X_r(0); X_rest(τ) \| X_rest(0)) for every register r and τ ∈ {0.1, 1, 10} |

Each family is summarized two ways: summed over components, and averaged over frame sizes.

**Checks** (`test_log.txt`).
- Seven mechanics tests pass: stationarity; detailed balance at zero drive; l_F + l_{F^c} = 0; 0 ≤ σ_F ≤ σ; the H-theorem from random initial laws; the analytic clock current σ = 2κ·sinh(Δμ/2)·Δμ to 10⁻¹⁶; and the sign of the sensor's information flow.
- Three deliberate mutations are all caught.
- Analytic spot check: visible circulation summed over frames equals exactly 16σ for every two-register structure. Of the 63 frames, 16 contain both registers, and each of those sees σ; every other frame sees a two-state projection, whose net current must be 0.

## 2. Filters

Passes out of 4 reference drives (Δμ = 1, 2, 4, 8). "sum" and "s-m" are the two summaries.

| Filter | σ sum | σ s-m | VIS sum | VIS s-m | MEM sum | MEM s-m | FLOW sum | FLOW s-m | CTL sum | CTL s-m |
|---|---|---|---|---|---|---|---|---|---|---|
| Φ1. Clock and sensor differ at matched σ | 0 | 0 | 0 | 0 | 4 | 4 | 4 | 4 | 4 | 4 |
| Φ2a. A heat leak changes nothing | 0 | 0 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| Φ3. Persistent-source sensor ≥ fast-source sensor at matched σ | 4* | 4* | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| Φ4. Gated ring > ungated ring at matched σ | 0 | 0 | 4 | 4 | 4† | 4† | 0 | 0 | 4 | 4 |
| Φ5. Detects parity structure | 4 | 4 | 4 | 4 | 4‡ | 4‡ | 4 | 4 | 4 | 4 |
| Φ5 as frozen: detects, and not through frames of size ≤ 2 | 4* | 4* | 4 | 4 | 0 | 0 | 0§ | 0§ | 0§ | 0§ |
| Φ6. One 4-ring not above two 2-clocks at matched σ | 4* | 4* | 0 | 0 | 0 | 0 | 4* | 4* | 1 | 1 |

**Notes on the marks:**
- **\*** Passes only by a tie: matched σ, or both values zero.
- **†** Memory passes Φ4 because the gated ring is frozen half the time, and a frozen ring has long memory. In the driven-excess addendum, memory fails Φ4 at all 4 drives.
- **‡** Memory "detects" the parity structure by being *lower* than three independent noise bits: 105 against 110 at Δμ = 4. The driven register flips faster.
- **§** Information flow and control are indexed by cuts or single registers, but each component involves every register. So the size-≤2 clause of the frozen Φ5 does not test pairwise blindness for these families. Both families do detect the three-way structure.

**Driven-excess addendum (A1, post hoc).** This subtracts each family's value for the same mechanisms at zero drive.

| | Result |
|---|---|
| Control | Still passes Φ1, Φ3, Φ4 and Φ5 at 4/4. At Δμ = 4 the gated ring scores 0.268 against 0.194, but 0.875 of the gated ring's raw control is passive gating |
| Memory | Fails Φ4 and Φ6 at 4/4. Its driven excess is mostly negative |
| Information flow | Unchanged, because it is already zero at equilibrium |

## 3. Diagnostics

**D1. Relay against fan.**
- At the same drive, the relay dissipates 7× more than the fan (1.60 against 0.23 at Δμ = 4), because errors propagate down the chain and must be re-copied.
- At matched σ:

| Family | Result |
|---|---|
| Information flow | Fan wins at every drive (e.g. 4.32 against 1.87 at Δμ = 4) |
| Control | Fan wins at Δμ = 1 and 2 (0.30 against 0.02; 0.22 against 0.05). Relay wins at Δμ = 4 and 8 (0.12 against 0.03; 0.22 against 0.004) |

- So the pair count's depth bias doesn't carry over intact. The flow readouts disagree with each other, and control's verdict depends on drive.

**D2. Sloppy against careful copying** (one sensor, Δμ from 0.5 to 8).

| Family | Behaviour |
|---|---|
| Visible circulation | Stays at exactly 16σ |
| Information flow | About 31σ, nearly constant: in a sensor it is proportional to burn |
| Memory | Rises slowly, but falls sharply per unit σ |
| Control | Has an interior optimum: 0.054 → 0.32 (at Δμ = 2) → 0.011. When the copy becomes perfect, the source adds nothing beyond the copy, and its conditioning vanishes |

**D3. Gas against organized**, at matched σ, 10 random driven copy networks per drive.
- The organized system is a gated ring plus a sensor.
- It wins on control at every drive, by 4–26× over the gas median, and on memory.
- The random networks win on information flow at every drive: medians 2.9, 53 and 392 against the organized system's 0.29, 2.4 and 4.6.
- 7–19 random networks per drive could not reach the organized throughput at all, because consistent loops freeze. Only frustrated networks enter the comparison.

**D4. Range width.** I(s; r_k) along a five-link relay.
- The decay length grows with drive and with the copy-to-noise ratio ρ.
- At Δμ = 4 it goes from 1.7 to 8.6 links; at Δμ = 8, from 10 to 128 links.
- Dissipation falls as ρ rises: 96 down to 3 at Δμ = 8.
- At low drive the width saturates, because copy errors (about e^{−Δμ}) dominate.

## 4. What this establishes and what it doesn't

**Established, in six-register exact models:**
- The flow framing is native and runs cleanly.
- Reversibility separates passive structure (memory, coupling) from sustained structure (currents, information flow), with the gradient as the switch.
- Burn-type readouts behave as the inertial-range analysis predicted, and are rejected.
- Information flow sees only maintained static correlation.
- Memory is dominated by passive slowness.
- Control is the best single family, but it fails plurality and it vanishes for perfect copies and perfect clocks.
- The two complementary families have disjoint blind spots.
- A relay's range width shows clean Reynolds-like behaviour.

**Not established:**
- that any combination of these families is lushness;
- that six-register results scale;
- that the plurality filter's direction is right. A Johnson ring is a single structure, but it is not a condensate in the 2D-turbulence sense.

## 5. What I'd test next

1. **Range width as a general readout.** For every register and frame, measure how far its distinctions propagate through the network before erasure: control at increasing lags and graph distances. This is the one readout that behaved like an inertial range, and it should be generalized off the relay.
2. **The complementary pair: information flow together with control.** Their blind spots are disjoint, so test whether their profile, used jointly with dominance and no scalar, passes every filter.
3. **Perfect copies and perfect clocks.** Control falls to zero there. Is that right, in the sense that redundancy shouldn't count? Or does it lose perfectly reliable structure? This connects directly to your ruling that copying is fine and only copying as the sole optimum is degenerate.

## Files

- `flow_probe_protocol_v0.md` and its `.sha256`; `deviations.md`.
- **Code:**
  - `flow.py`: engine;
  - `tests.py`;
  - `run_flow.py`;
  - `evaluate_flow.py`;
  - `addendum_A1.py`.
- **Data:** `results_flow.json`, `results_A1.json`, `verdicts_flow.json`, `tables_flow.md`, `test_log.txt`.

**Replicate:**

```
python tests.py --mutations
python run_flow.py
python evaluate_flow.py
python addendum_A1.py
```

The whole run takes under a minute.

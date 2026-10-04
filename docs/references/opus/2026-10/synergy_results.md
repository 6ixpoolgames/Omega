# Synergy vs lushness: results

From Claude · 3 October 2026. Internal exploration.

## Question

Do winning arrangements carry synergy, and how strongly does synergy track lushness?

## Setup

**Substrate.** The v9 substrate:
- three independent sources, s, f1 and f2;
- the bias of s is p ∈ {0.5, 0.2, 0.05} and the bias of f1 and f2 is q ∈ {0.5, 0.2, 0.05}, giving 9 cells;
- a deciding frame D of three registers.

**Population.** Every outcome reachable with at most 3 gates, under three gate sets:

| Gate set | Gates | Gate count | Distinct outcomes |
|---|---|---|---|
| G1 | CNOT from sources into D | 9 | 130 |
| G2 | adds Toffolis on source pairs, any control polarity | 45 | 10,372 |
| G3 | records can also act as controls, which gives depth | 135 | 38,366 |

Nothing in the population was picked.

**Readouts.** For every frame F (every subset of D):
- **Lushness** is the branch volume χ(X : F).
- **Synergy** is Syn(F) = I(F ; X) − Σₖ I(F ; xₖ), which is never negative for independent sources. It equals how correlated the sources become once you know F.
- **Branch-split synergy** is the synergy within the branches of s.

**Frame size.** k = 1, 2 or 3 registers, against 3 sources.

**Hygiene.**
- Classical exact values match the quantum state-vector simulator to 3×10⁻¹⁵, over 3,150 values.
- Known values are reproduced: Syn(XOR) = 1 and Syn(AND) = 0.1887.
- Synergy is never negative.
- Program counts check out.
- Three deliberate faults were all caught.
- Runtime: 33 s for the sweep, 11 s for the analysis.

## Results

### 1. The sign of the correlation is set by frame size, as predicted

| Frame | Spearman ρ(Syn, lushness), nonconstant records | Same, within matched support | Best synergistic minus best non-synergistic | Synergy of the winners |
|---|---|---|---|---|
| **k = 1** (narrower than its inputs) | 0.0 to +0.6 in G2/G3 (≈ +0.6 when all sources are biased); up to +1.0 in G1 | **mostly +0.6 to +1.0** (lowest 0.0) | **+0.10 to +0.30 bits** when all sources are biased; 0 when any source is fair | all synergistic when biased |
| **k = 2** | −0.2 to +0.37 | −1.0 to +0.4 (mostly negative for 2-source records) | +0.13 to +0.30 with ≤ 2 gates; **0.00 to 0.05 with 3 gates in G3** (see 3) | synergistic, but barely in G3 |
| **k = 3** (can hold everything) | −0.39 to +0.31 | **mostly negative** (−1.0 to +0.1) | negative everywhere (−0.01 to −1.0) | **always zero synergy** |

"Matched support" means comparing only records that depend on the same number of sources. This rules out "more sources involved" as the driver.

**A worked case** (G3, p = q = 0.2, k = 1):
- the best non-synergistic record is a copy of one source, at 0.722 bits;
- the winner is NOR of all three sources, at 0.9996 bits, with Syn = 0.26;
- so synergy fills the register 38% fuller.

### 2. When synergy pays

Synergy pays only when **the frame is narrower than what it is fed, and no single input already fills it.**
- If any source is fair, copying it already saturates a one-register frame. Synergy then ties and never wins.
- If the frame can hold every source, the winners are copies with zero synergy. That is the data-processing bound.

**Synergy is compression.** Its value is entirely a capacity effect.

### 3. A second route to compression has zero synergy: hierarchy

In G3, records can control later gates. At k = 2 with 3 gates, a **zero-synergy record nearly ties the best synergistic one**, to within 0.0002 to 0.05 bits. The record is a decision tree:
- if s, then cell 0;
- else if f1, then cell 1;
- else if f2, then cell 2;
- else cell 3.

Each cell is a product set, so the sources stay independent within it, and Syn = 0 exactly. Check at p = q = 0.2: the cell weights are 0.2, 0.16, 0.128 and 0.512, giving H = 1.7615 bits, which matches. Yet it compresses as well as the best fusion.

So **composition comes in two kinds:**
- **fusion** (XOR, OR, NOR), which creates joint-only distinctions and so has synergy;
- **hierarchy**, conditional and sequential records, which has none.

Both pay under capacity limits:
- Fusion is cheaper: it wins with 1 or 2 gates.
- Hierarchy needs depth, and then it catches up.
- With a single register, only fusion works, because a two-cell partition into product sets is just a copy.

That qualifies "composition is just synergy". Under this measure, composition is synergy **or** hierarchy, and both are compression.

### 4. The frontier (undominated over all 7 frames)

- **Fair sources:** the frontier is 100% zero-synergy. It is all copies.
- **Biased sources:**
  - 85–99% of the frontier is synergistic, with Toffolis (G2/G3).
  - Its mean synergy is above the population's when all sources are biased: 1.56 vs 0.99 at p = q = 0.2 in G3.
  - The full-information copies always stay on the frontier, because they win the k = 3 frame.
- **One source fair:** the frontier's mean synergy is below the population's. A lot of the population's synergy is wasted, as parity with a bit that is already saturated.

### 5. Winning branches

Within-branch synergy (branch-split synergy) of the winners is small: 0 to 0.54 bits. Most of the winners' synergy is cross-branch, binding s to f1 and f2, rather than inside a branch.

## What it means

- **Synergy tracks lushness strongly, but only in bounded frames.** Its correlation with lushness is positive and large where a frame is narrower than its inputs and the inputs are unsaturated. It is zero or negative where the frame can hold everything.
- **That is a corridor.** Its axes are frame capacity against input count, and input bias.
- **Composition beats copying exactly where frames are bounded.** Real frames are bounded by bills and light cones, which is where the framework says composition lives.
- **Hierarchy is a second, zero-synergy way to win** once depth is available. Synergy is the shallow route to compression; hierarchy is the deep one.

## Re-cut: composition defined on the frame's partition

**How the re-cut was done** (`composition_classes.py`, `composition_classes.json`). A frame's record splits the 8 source branches into cells. Each partition is classified structurally, with no reference to the gates that made it:

| Class | What it is |
|---|---|
| **product** (copies) | the partition induced by whole sources; this includes the full partition |
| **hierarchy** | every cell is a product set, but the cut on one source depends on the context of the others |
| **fusion** | some cell is not a product set |

**Composition = hierarchy or fusion.**

| Frame | Possible classes | Winners |
|---|---|---|
| 1 register | product, fusion only. Hierarchy is impossible, because a 2-cell partition with product cells is a copy | fusion in every all-biased cell; ties with copies when any source is fair |
| 2 registers, ≤ 2 gates | all three | fusion. Hierarchy is *below* copies (1.52 vs 1.72) |
| 2 registers, 3 gates (G3) | all three | fusion, with hierarchy within 0–0.05 bits (e.g. 1.762 vs 1.773; 1.210 vs 1.210) |
| 3 registers, 3 gates | all three | always product, i.e. the full partition. Any encoding that holds everything is the same content, so composition and copying stop being different things |
| 3 registers, ≤ 2 gates (bill-bound) | all three | fusion in every all-biased cell (e.g. 1.743 vs 1.444) |

**Mechanism.** A frame's lushness is the entropy of its partition: how evenly it splits the branch weight.
- Copies can only cut along the sources' own lines. When the sources are biased, those cuts are lopsided.
- Composition lets the frame cut where the weight actually lies.
  - **Fusion** allows any cell shape.
  - **Hierarchy** allows only product cells. That costs almost nothing once there are 4 or more cells, but it needs depth.
- Composition wins exactly when cuts are scarce (bounded by registers *or* by bill) and the sources are unbalanced.

## Limits

- The world is tiny: 3 sources, 3 registers, at most 3 gates.
- v8's other mechanisms are not exercised at this size: non-redundancy across many frames, and compounding with depth.
- The correlation's magnitude depends on the population. Its sign pattern held across all three gate sets.

## Next

- Scale to 4–5 sources, 4–6 registers and depth 4–6 to see whether hierarchy keeps pace with fusion as depth grows.
- Run v8's shifted-copy control.

## Files

- `synergy_probe.py`: population, readouts and tests.
- `synergy_analysis.py`: confound control and gaps.
- `results.json` and `analysis.json`.
- `test_log.txt`.

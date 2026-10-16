# Frame aggregation prototype v0

3 October 2026 · exploratory finite implementation

## Executable choice

This is the first bounded interpretation of the adopted count-once access proposal. For each jointly executable output bundle, use I(X;Y)=H(Y), then V=2^(H(Y)-H(X)). Information-equivalent output partitions have one catalog entry with Pareto access routes. The underlying physical programs, wire positions and residual records are retained, not quotiented away.

At each input-frame-size/step/Toffoli budget, report the largest jointly deliverable information and a witness. This maximum is an explicit exploratory choice: an existential content envelope, not actual chooser behavior or a sum of the access distributed across the world. It is one narrow implementation of cheapest access, not a complete realization of Opus's all-frame aggregation. The complete partition/route catalog stays alongside it so losses from compression remain visible.

Two blank destination registers are allocated in every arrangement. One execution must deliver both outputs within the shared budget. Alternative programs are never pooled into fictitious joint information. Preparation and loss bills are reported separately from remaining decoder budget; these are exhibited gate bills, not thermodynamic or globally minimal costs.

The language contains X, CNOT and Toffoli with either control polarity; controls may read the three record positions or the other output. Outputs start blank; inputs are read-only. Search is exhaustive only to two gates in this language. Equivalent restart states are cached. A null repair cost means no decoder inside this bound, not physical impossibility.

## Initial preparations

Three retained source bits s,a,b supply eight assignments. With u=(NOT a) AND (NOT b) and v=NOT s:

- copies=(s,s,s), plural=(s,a,b): three-CNOT preparations each.
- access_A=(s XOR a,0,NOT s), access_B=(0,s,a): existing three-step/two-Toffoli witnesses.
- repair_A=(u,u AND v,v), repair_B=(u,u,v): existing three-Toffoli witnesses.

For each loss variant, one record is swapped into an allocated inaccessible bath position at three additional CNOT steps. Sources, remaining records, bath and output residual are retained. The entire source law is available in summary.json; no physical noise is removed. Common-bit inputs deliberately include dependence. No loss-location distribution is assumed.

## Readouts at two steps, two two-control gates, up to three input registers

| Preparation / law | Bank bits | Syn | Raw subset tally (bits) | Jointly delivered bits | Normalized V |
|---|---:|---:|---:|---:|---:|
| copies / fair | 1.000000 | 0.000000 | 7.000000 | 1.000000 | 0.250000 |
| copies / biased_0.2 | 0.721928 | 0.000000 | 5.053497 | 0.721928 | 0.367583 |
| copies / common_bit | 1.000000 | -2.000000 | 7.000000 | 1.000000 | 1.000000 |
| plural / fair | 3.000000 | 0.000000 | 12.000000 | 2.000000 | 0.500000 |
| plural / biased_0.2 | 2.165784 | 0.000000 | 8.663137 | 1.742733 | 0.745845 |
| plural / common_bit | 1.000000 | -2.000000 | 7.000000 | 1.000000 | 1.000000 |
| access_A / fair | 2.000000 | 0.000000 | 8.000000 | 2.000000 | 0.500000 |
| access_A / biased_0.2 | 1.443856 | -0.000000 | 6.140331 | 1.443856 | 0.606287 |
| access_A / common_bit | 1.000000 | -2.000000 | 4.000000 | 1.000000 | 1.000000 |
| access_B / fair | 2.000000 | 0.000000 | 8.000000 | 2.000000 | 0.500000 |
| access_B / biased_0.2 | 1.443856 | -0.000000 | 5.775425 | 1.443856 | 0.606287 |
| access_B / common_bit | 1.000000 | -2.000000 | 6.000000 | 1.000000 | 1.000000 |
| repair_A / fair | 1.811278 | 0.188722 | 8.444316 | 1.811278 | 0.438691 |
| repair_A / biased_0.2 | 1.664611 | 0.212402 | 8.874210 | 1.664611 | 0.706532 |
| repair_A / common_bit | 1.000000 | -2.000000 | 7.000000 | 1.000000 | 1.000000 |
| repair_B / fair | 1.811278 | 0.188722 | 8.867669 | 1.811278 | 0.438691 |
| repair_B / biased_0.2 | 1.664611 | 0.212402 | 8.543812 | 1.664611 | 0.706532 |
| repair_B / common_bit | 1.000000 | -2.000000 | 7.000000 | 1.000000 | 1.000000 |

At biased inputs, outputs (NOT s AND NOT a, NOT s AND NOT b) deliver 1.742733 bits versus 1.443856 for two direct copies. Both take two steps, but the composed route uses two Toffolis rather than two CNOTs. The vector budget preserves that difference; all three input positions are used.

Normalized volumes compare preparations under one encompassing source law. Changing that law also changes the normalization; rows from different laws are sensitivity cases, not a single ranking of worlds.

## Checks on what the aggregation loses

- access_A versus access_B, fair: 0 of 36 profile cells differ.
- access_A versus access_B, biased_0.2: 8 of 36 profile cells differ.
- access_A versus access_B, common_bit: 0 of 36 profile cells differ.
- The specific response NOT a still costs 2 versus 1 steps. Equal envelope cells do not imply identical response access.
- With fair plural inputs, one step delivers at most one bit; two CNOT steps deliver two. Separately available one-step responses do not become a two-bit one-step delivery.
- With fully correlated sources, a perfect record has Syn=-2 and V=1. Signed Syn is reported, not used as an aggregation bonus or penalty.

## Local loss and bounded repair

| Preparation | Loss 0: repair steps | Loss 1: repair steps | Loss 2: repair steps |
|---|---:|---:|---:|
| copies | 1 | 1 | 1 |
| plural | >2 or impossible | >2 or impossible | >2 or impossible |
| repair_A | >2 or impossible | 1 | >2 or impossible |
| repair_B | 1 | 1 | >2 or impossible |

## Targeted depth-three follow-up

- fair: 0 of 64 envelope cells differ at the extended bound.
- biased_0.2: 14 of 64 envelope cells differ at the extended bound.
- common_bit: 0 of 64 envelope cells differ at the extended bound.
The response NOT a still costs 2 versus 1 steps. A surviving tie is not resolved merely by this extra decoding step. All new routes and profiles are in [the follow-up evidence](frame_aggregation_v0/depth3_followup.json).

The loss-conditioned profiles are retained in the evidence, without an arbitrary average over faults. Additional copies can preserve access after loss even when they add no distinct source content. This is a consequence of routing and residual dynamics, not an assigned redundancy reward.

## Scope and reproduction

These are exact finite diagnostic calculations (floating-point entropy), not a gas experiment, quantum interference run, endogenous generativity test or completed lushness invariant. The envelope deliberately leaves location distribution, recurrence and the arbitration of crossing profiles unresolved. The prototype makes those limitations inspectable instead of fitting coefficients to preferred outcomes.

Run from the repository root:

    .venv/Scripts/python.exe -m omega_v2.validation.frame_aggregation_v0

Evidence: [summary and profiles](frame_aggregation_v0/summary.json), [programs, physical residuals and content frontiers](frame_aggregation_v0/routes.json).

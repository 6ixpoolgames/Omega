# Short structural probe for the 3.2 draft

2026-10-03. Exploratory run requested by the user: up to ten workers, shallow sampled circuits, most effort on analysis, approximately ten minutes of probing. Circuit expansion has stopped; verification and this report followed. No exhaustive circuit search, release, commit or push was performed.

## Scope and resource use

A quick Markdown/text search did not locate the old compute configuration. The observed machine has 12 CPU cores/24 logical processors, approximately 32 GiB RAM and an RTX 4070 Ti with 12 GiB VRAM. The run used ten CPU worker processes with numerical-library threading limited to one thread per worker. The GPU was unnecessary.

Ten reproducible seeds each sampled 2,000 programs at each length 1 through 5: **100,000 sampled programs**. Each instruction was independently sampled from the declared 135-gate alphabet. This sampling distribution is an analyst's exploration distribution, not physical probability over futures.

The world has three source bits and three initially blank record bits. Gates target records and use sources or other records as controls. Source bits remain in the physical model. The next-stage reader cannot couple directly to them. Preparation costs retain CNOT count, Toffoli count and serial duration separately. There is no energy or minimum-preparation-cost claim.

The primary parallel pass took 2.9 seconds, excluding interpreter startup. Computation was cheap; implementation, analysis and verification used most of the effort. Within each seed, repeated endpoint/depth/Toffoli-count combinations were collapsed for endpoint analysis while retaining a representative program. This yielded 55,840 map-bill records across seeds; these are not necessarily globally distinct. This deduplication is not a proposed quotient of physical continuations.

The decoder panel uses a new blank output Y and up to two CNOT/Toffoli gates controlled by the record bank. We analyse its fixed finite response family; we do not simulate every possible circuit or adaptive policy. All 256 Boolean functions of the original three sources serve as response coordinates. No uniform value or requirement distribution is assigned to them.

Nine independent source laws reproduce the bias grid (.5,.2,.05) for s and for the two other sources. Two additional laws mix independent Bernoulli(.2) sources with a common Bernoulli(.2) source, using mixture weights .5 and .9. Every input retains positive probability.

## 1. Equal information and preparation bills can leave different access

We grouped sampled records by **exact input partition and identical exhibited preparation bills**. Thus full-record entropy, information about each source, and the reported full-record synergy agree under every source law within each group. The groups do not identify the physical encodings.

Among 33,122 comparisons to a group's first representative:

- 19,622 have different downstream cost profiles in the original decoder panel.
- 14,336 still differ in a second panel that supplies native X and complemented CNOT operations at unit cost.
- In that second panel, 522 differ even in the set of responses available within two gates.

The second panel is explicitly different hardware, not a declaration that physical basis changes are free. It checks whether the whole observation depends on the original gate vocabulary's polarity asymmetry. These comparison counts are descriptive of this sampled population, not independent trials or estimates over all worlds.

A retained witness with no removable or inactive instruction has two three-gate preparations, each using one CNOT and two Toffolis. They give record banks:

    A = (s XOR f1, 0, NOT s)
    B = (0, s, f1).

Both retain the same distinctions about s and f1. At independent Bernoulli(.2) inputs, both have H=1.443856189775 bits and full-record Syn=0. In the symmetric decoder panel, delivering NOT f1 takes two operations from A and one from B. There is no zero- or one-operation realization of that response from A in this panel. All three preparation gates contribute to each stored encoding. The preparation bills are exhibited bills, not proven optimal bills.

**Interpretation:** information held and physical access to its different uses are distinct. This is a finite access distinction, not a lushness ranking or a proof of a new universal invariant.

## 2. Recovery differs even when content, partition and synergy agree

A perturbation swaps one record into a retained but reader-inaccessible bath register. The location is known. The information is not deleted globally. The repair apparatus may use the surviving bank to write a replacement in Y; copying Y back to the erased location costs one additional CNOT. The initial erasure swap has the same three-CNOT cost in every case.

After excluding constant records and comparing sorted repair profiles, 1,498 of 29,166 matched comparisons still differ. Sorting removes differences that arise solely from permuting register indices in this diagnostic. These remain exploratory comparisons, not a probability distribution of physical faults.

A particularly simple witness, again with every preparation gate necessary, sets:

    u = (NOT f1) AND (NOT f2)
    v = NOT s

    A = (u, u AND v, v)
    B = (u, u,       v).

Both preparations use three Toffolis, occupy three nonconstant records and induce the same full-record partition. At Bernoulli(.2) sources both have:

    H = 1.664611284143 bits
    Syn = .212401762564 bits.

For A, erasing the middle record admits exact reconstruction from the survivors. Erasing either other record leaves ambiguity. For B, either copy of u can be restored from the other, while erasing v leaves ambiguity.

Thus **one of three locations admits exact repair in A; two of three do in B**. These are location counts, not asserted physical failure probabilities. The impossible cases were independently checked for ambiguity in the surviving records, so their failure is stronger than merely not finding a decoder in the panel. Access to the source bank or bath would change that conclusion and has not been silently granted.

**Interpretation:** the arrangement of retained information contributes a recovery structure that the current full-frame information and synergy summaries do not determine. This is closely related to familiar redundancy/error-correction mechanisms. It is useful evidence for what the candidate must represent, not a claim to have discovered error correction.

## 3. Input dependence matters for recursive composition

The current quantity is:

    Syn(F) = I(X;F) - sum_i I(Xi;F)
           = TC(X|F) - TC(X).

With independent sources TC(X)=0, explaining the earlier nonnegativity. With dependent sources it is a change in total correlation, not simply an absolute amount of joint-only information.

In the dependent-input controls, approximately 80% of retained full-record instances have negative values. Across seeds, the full-record entropy/Syn Spearman correlation lies between -.420 and -.378 for mixture weight .5, and between -.609 and -.584 for mixture weight .9. These correlations concern the selected sampled map-bill population. They do not establish a causal law or a general rank order.

The negative values are an anticipated consequence of the identity, not a numerical fault or discovery of harmful composition. This matters because outputs of one stage can become correlated inputs to another. A recursive architecture cannot simply carry the independent-input interpretation of Syn through every layer.

**Interpretation:** retain the actual joint input law and distinguish inherited dependence from changes induced by a record. Do not clip negative values or add a coefficient to restore a desired ranking.

## Verification and limitations

Known XOR, AND, hierarchy, probability-mass, decoder-witness and copy-recovery checks passed. Every saved program was rerun against the saved endpoint table. A separate scalar Boolean implementation checked 1,000 sampled programs, agreeing with the packed implementation. The headline access and repair witnesses were checked by deleting each instruction in turn: all instructions contribute to their final encoding. Source hashes and numerical evidence are retained; Ruff passes on both new scripts.

Initial matches included idle instructions and constant-record effects. The headline witnesses above survive those checks. The population counts still describe the full declared sample and must not be presented as counts after removing all such cases.

This is a classical sector of a reversible circuit model with exact enumeration of eight inputs. It is not a quantum interference experiment, physical gas simulation, indefinite maintenance experiment, complete recursive atlas, or proof of minimal costs outside the stated languages. The source/fault/decoder choices are model premises. No scalar lushness measure was introduced.

The run did not test repeated construction amortization, long-run persistence, all failure laws or arbitrary cross-scale emergence. Those remain open rather than being inferred from the present witnesses.

## What belongs in 3.2

The useful additions are modest and concrete:

1. **Access has implementation structure:** equal current information can support different later responses at the same remaining budget.
2. **Recovery has distributional structure:** how distinctions are placed and combined affects which losses can be repaired.
3. **Composition inherits correlations:** information diagnostics must preserve the joint laws delivered by earlier stages.

These support the proposed response/bill/residual architecture. They do not identify its extent functional. Include the counterexamples and their scope in the draft; additional endpoint enumeration is not required before doing that.

## Reproduction and evidence

Run from the repository root:

```text
python -m omega_v2.validation.structural_probe_10min_v0 --out <new-output-directory> --workers 10 --per-length 2000
python -m omega_v2.validation.structural_probe_10min_analysis_v0 <new-output-directory>
```

Use a new directory for a new run. The second command reproduces the alternative-decoder analysis. The subsequent checked headline witnesses and register-permutation/constant-record audit are retained as explicit indexed records in the files below; they are not additional random searches.

- [Manifest and original source hash](../validation_results/structural_probe_10min_v0/20261003/manifest.json)
- [Primary summary](../validation_results/structural_probe_10min_v0/20261003/summary.json)
- [Alternative decoder analysis](../validation_results/structural_probe_10min_v0/20261003/analysis.json)
- [Repair comparison](../validation_results/structural_probe_10min_v0/20261003/repair_analysis.json)
- [Essential-gate witnesses](../validation_results/structural_probe_10min_v0/20261003/essential_witnesses.json)
- [Verification](../validation_results/structural_probe_10min_v0/20261003/verification.json)

The same folder holds all ten compressed seed arrays, per-seed summaries and snapshots of the executed source before formatting. The original source hash matches its archived snapshot.

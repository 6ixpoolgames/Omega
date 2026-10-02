# Assessment of Opus's synergy results

2026-10-03. Source: the user-supplied [synergy report](../../references/opus/2026-10/synergy_results.md). Only the report was supplied; its simulator, analysis programs, raw arrays and test logs were not present in the attachment directory.

## What was checked independently

I reconstructed the deterministic Boolean gate language from the description. Sources occupy three read-only input bits; three record bits begin at zero. A CNOT has one positive control. Toffolis have distinct controls, each with either polarity. Targets are record bits. G1 permits source CNOT controls; G2 adds source-pair Toffolis; G3 permits any other source or record as a control. Enumerating reachable truth maps from zero records reproduces:

| Gate family | Primitives | At most 1 gate | At most 2 gates | At most 3 gates |
|---|---:|---:|---:|---:|
| G1 | 9 | 10 | 46 | 130 |
| G2 | 45 | 46 | 919 | 10,372 |
| G3 | 135 | 58 | 1,735 | 38,366 |

Enumeration used exact eight-row Boolean truth tables, not sampling. This is an independent reconstruction that matches the population counts; it does not independently reproduce the report's entire correlation and frontier analysis.

Under three independent Bernoulli(.2) sources, direct enumeration gives:

| Record | Information H(F), bits | Report's Syn, bits |
|---|---:|---:|
| Copy one source | .721928094887 | 0 |
| NOR of three sources | .999584463931 | .263270726350 |
| Hierarchical four-cell record | 1.761504551525 | 0, within floating-point error |
| XOR of three sources | .966078097595 | .780988177983 |

The hierarchy has cells of weights .2, .16, .128 and .512. A three-gate realization is r0 = not s AND not f1; r1 ^= s; r1 ^= r0 AND f2. For fair sources, the standard XOR-of-two and AND-of-two calculations give Syn=1 and Syn=.188721875541, respectively.

The reported quantum/classical agreement, deliberate-fault coverage, Spearman ranges, frontier fractions, selected maxima and branch-split values remain unverified without the analysis definitions and raw results. They are not contradicted by the checks above.

## The information identity is sound, with a precise scope

For independent inputs X=(X1,...,Xn),

    I(X;F) - sum_i I(Xi;F)
      = sum_i H(Xi|F) - H(X|F)
      = TC(X|F) >= 0.

This is conditional total correlation: learning F can make initially independent inputs dependent. It is a legitimate diagnostic, but not a unique general definition of synergistic information. For dependent inputs the same difference is TC(X|F)-TC(X), which can be negative.

For the report's deterministic classical encoding, H(F|X)=0. Thus I(X;F)=H(F), and the corresponding classical Holevo quantity is the same. Maximizing this readout means finding an achievable partition with high output entropy under the actual source distribution.

This is a useful, physically constrained record-information result. Calling H(F) lushness does not establish that it compares the complete continuation field.

## What is interesting

The worked examples establish two concrete routes to retaining more information in a small record. A NOR record groups the source outcomes into almost equal-weight cells. A hierarchical record uses conditional cuts and achieves high output entropy while keeping the sources conditionally independent inside each cell. A synergy-only proxy would miss the latter.

The report's recut also correctly distinguishes a register limit from an operation-budget limit: three registers are insufficient to realize the full-copy encoding if only two one-target gates are available. The relevant limitation is physically achievable encoding, not the number of registers alone.

This supports examining the family of achievable joint response laws as budgets and composition change. It does not require a coefficient rewarding either fusion or hierarchy.

## Overstatements and qualifications

1. **Synergy is not identical to compression.** A copy, hierarchy or XOR is a different lossy statistic of the inputs. Conditional source coupling characterizes one aspect of that encoding. In the verified example, XOR has substantially more Syn than NOR but less record information.
2. **The corridor is established for a selected finite model and readout.** The phrase "composition wins exactly when" is stronger than a sweep of three biases, three gate languages and three-gate programs establishes. Fair-source copying saturates the one-bit entropy bound, but general conclusions also depend on available gates, budgets, errors and source dependence.
3. **Full-copy optimality has a straightforward bound here.** If three source copies are feasible, F=X attains H(X), the upper bound for deterministic record information. Its zero full-frame Syn follows from exact recovery. This does not establish absence of physically meaningful composition or superiority under another future interaction.
4. **The product/hierarchy/fusion recut is a classification of partitions relative to specified source factors.** It is not a complete physical classification of mechanisms. An invertible recoding and literal copies induce the same singleton-cell partition, while their local routing and decoding costs can differ. Preserving those differences is central to the proposed architecture.
5. **Matching support size is an incomplete confound check.** When p differs from q, two records depending on the same number of sources need not depend on equally biased sources. Compare actual dependency subsets and feasible bills where the question requires it. Population and tie weighting matter for correlations and frontier percentages.
6. **No information is created globally in these reversible source-to-record circuits.** Information is redistributed into records, using prepared blanks and gates. That redistribution is consequential, but it is not a test of sustained generativity, physical gas or a value bridge.
7. **The source bank remains part of the residual.** A record's lost distinctions may still be accessible elsewhere, and recovering or recombining them has a physical bill. Endpoint entropy alone does not determine that bill or subsequent access.

## Consequence for the next implementation

Use this model as a reproducible classical calibration of the proposed atlas. Retain truth maps and their implementing programs, full joint output laws, physical bills and residuals. Report record information and conditional total correlation as named diagnostics. Keep the partition classifier as an additional projection.

Before expanding the enumeration, add a case in which equal partition information hides different future accessibility or decoding cost. The next useful advance is preserving those differences through composition and restart, rather than increasing the number of entropy-scored arrangements alone.

See [the Claude implementation brief](claude_recursive_access_implementation_brief_2026-10-03.md) for the concrete build plan.

# Channel comparison: breadth, loss and return

Complete36-table searches at3+1 inventory, same drive/material/clock and matched E8 preparations within each law. Native unfiltered count-history breadth is the only objective. The tests do not maximize protection.

| Case | Winning inactive/active table | Rate bits/time | Active at64 | Channel closure by64 | Most protective closure by64 | Seed−reference offset bits |
|---|---|---:|---:|---:|---:|---:|
| channel-comparison-r1-uniform_absorbing | mix75 / mix25 | 4.839018 | 0.069446 | 0.724825 | 0.724825 | -1.019431 |
| channel-comparison-r1-worn_absorbing | mix75 / mix25 | 4.839018 | 0.733063 | 0.021059 | 0.010803 | 18.093883 |
| channel-comparison-r1-worn_reversible | mix75 / mix50 | 4.861082 | 0.690194 | 0.000000 | 0.000000 | 16.048651 |

The uniform absorbing control gives policy-independent closure. Worn absorbing damage allows repair/control to affect loss. Reversible laws retain positive return paths; zero structural closure does not establish sustained operation.

In absorbing laws every policy eventually loses the apparatus channel. Its carriers, gates and fixed controller hardware keep evolving. Limiting rates rank that residual process; policies need not share a rate. Root/reference comparisons use one fixed law and table, while differences across laws are mechanism contrasts.

## Finite planning horizons

For each planning horizon, select all tied breadth-maximizing tables and report their closure at the common deadline64. This avoids comparing different observation windows.

| Case | Planning horizon | Best table(s) | Their closure64 range |
|---|---:|---|---|
| channel-comparison-r1-uniform_absorbing | 1 | [['export', 'export']] | [0.7248249888513537, 0.7248249888513537] |
| channel-comparison-r1-uniform_absorbing | 4 | [['mix75', 'mix50']] | [0.7248249888513563, 0.7248249888513563] |
| channel-comparison-r1-uniform_absorbing | 16 | [['mix25', 'mix25']] | [0.7248249888513552, 0.7248249888513552] |
| channel-comparison-r1-uniform_absorbing | 64 | [['mix50', 'mix25']] | [0.724824988851352, 0.724824988851352] |
| channel-comparison-r1-worn_absorbing | 1 | [['export', 'export']] | [0.025564875219567074, 0.025564875219567074] |
| channel-comparison-r1-worn_absorbing | 4 | [['mix75', 'mix50']] | [0.022365540492172653, 0.022365540492172653] |
| channel-comparison-r1-worn_absorbing | 16 | [['mix25', 'mix25']] | [0.0175291411691767, 0.0175291411691767] |
| channel-comparison-r1-worn_absorbing | 64 | [['service', 'mix25']] | [0.014932193127853322, 0.014932193127853322] |
| channel-comparison-r1-worn_reversible | 1 | [['export', 'export']] | [1.1102230246251565e-16, 1.1102230246251565e-16] |
| channel-comparison-r1-worn_reversible | 4 | [['mix75', 'mix50']] | [0.0, 0.0] |
| channel-comparison-r1-worn_reversible | 16 | [['mix25', 'mix25']] | [3.552713678800501e-15, 3.552713678800501e-15] |
| channel-comparison-r1-worn_reversible | 64 | [['service', 'mix25']] | [3.3306690738754696e-16, 3.3306690738754696e-16] |

## Frozen outcomes and readouts

| Case | Outcome | Verdict | Value |
|---|---|---|---:|
| channel-comparison-r1-uniform_absorbing | C1-numerics | pass | 7.031042414951116e-13 |
| channel-comparison-r1-uniform_absorbing | C2-seed-reference | open_outcome | -1.0192989388706906 |
| channel-comparison-r1-uniform_absorbing | C3-closure-risk | open_outcome | 0.7248249888513526 |
| channel-comparison-r1-uniform_absorbing | C4-functioning-margin | open_outcome | -0.07652206889823496 |
| channel-comparison-r1-uniform_absorbing | C5-native-rate | open_outcome | 4.839017870746879 |
| channel-comparison-r1-uniform_absorbing | C6-uniform-null | pass | 4.440892098500626e-15 |
| channel-comparison-r1-worn_absorbing | C1-numerics | pass | 3.775202372935382e-12 |
| channel-comparison-r1-worn_absorbing | C2-seed-reference | open_outcome | 5.47608710781833 |
| channel-comparison-r1-worn_absorbing | C3-closure-risk | open_outcome | 0.02105937295179805 |
| channel-comparison-r1-worn_absorbing | C4-functioning-margin | open_outcome | -0.687303401272692 |
| channel-comparison-r1-worn_absorbing | C5-native-rate | open_outcome | 4.839017870746825 |
| channel-comparison-r1-worn_absorbing | C6-uniform-null | unsupported | None |
| channel-comparison-r1-worn_reversible | C1-numerics | pass | 3.498445977356823e-11 |
| channel-comparison-r1-worn_reversible | C2-seed-reference | open_outcome | 3.9018027997553872 |
| channel-comparison-r1-worn_reversible | C3-closure-risk | open_outcome | 0.0 |
| channel-comparison-r1-worn_reversible | C4-functioning-margin | open_outcome | -0.7308143202785031 |
| channel-comparison-r1-worn_reversible | C5-native-rate | open_outcome | 4.861082416963295 |
| channel-comparison-r1-worn_reversible | C6-uniform-null | unsupported | None |

All policy rows, horizons, stationary usable/active expectations and resource/closure summaries are retained compactly in SUMMARY.json. Full state lists, class vectors and raw outputs stay local and reconstructible.

The initial uniform run emitted a descriptive closure-tension flag from~1e-15 rounding differences. Its registered analytic-null check passed; interpretation uses the1e-9 guard. No primary score, predicate verdict or raw record was altered.

Stationary observations derived from old class vectors are post-run readouts; new shallow-case predictions were filed before those runs. First-hit recovery and retained function are kept distinct. Two assisted events can include turnover and are not lineage-resolved open-ended compounding.

## Execution

- channel-scientific-uniform_absorbing-20261013T132604Z-6d1cc5: 292.48s, 576.44MiB, input `a37fa689f7cc3159600986a382edcdda02b0221419a3847b29c8f2818b90cf3d`.
- channel-scientific-worn_absorbing-20261013T133423Z-437f6b: 292.06s, 575.49MiB, input `e8fea876cf07b00c830abd89da8aa84fcab5af2d797aabbde3fffa98fbe5a35a`.
- channel-scientific-worn_reversible-20261013T133433Z-7dceee: 306.46s, 581.79MiB, input `efdee352a2213ac76f2f19ced00dce29e7cde5d99e7515716c8a46673b5a45b1`.

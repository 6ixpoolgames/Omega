# Channel comparison: breadth, loss and return

Complete36-table searches at3+1 inventory, same drive/material/clock and matched E8 preparations within each law. Native unfiltered count-history breadth is the only objective. The tests do not maximize protection.

| Case | Winning inactive/active table | Rate bits/time | Active at64 | Channel closure by64 | Most protective closure by64 | Seed−reference offset bits |
|---|---|---:|---:|---:|---:|---:|
| channel-shallow-r1-depth0 | service / mix25 | 8.747186 | 1.364023 | 0.000000 | 0.000000 | 5.843026 |
| channel-shallow-r1-depth-1 | mix25 / mix25 | 7.097682 | 1.073191 | 0.000000 | 0.000000 | 11.514527 |
| channel-shallow-r1-depth-2 | mix50 / mix50 | 5.836680 | 0.837788 | 0.000000 | 0.000000 | 13.651933 |
| channel-shallow-r1-depth-4 | mix75 / mix50 | 4.995182 | 0.692665 | 0.000000 | 0.000000 | 15.505650 |

The uniform absorbing control gives policy-independent closure. Worn absorbing damage allows repair/control to affect loss. Reversible laws retain positive return paths; zero structural closure does not establish sustained operation.

In absorbing laws every policy eventually loses the apparatus channel. Its carriers, gates and fixed controller hardware keep evolving. Limiting rates rank that residual process; policies need not share a rate. Root/reference comparisons use one fixed law and table, while differences across laws are mechanism contrasts.

## Finite planning horizons

For each planning horizon, select all tied breadth-maximizing tables and report their closure at the common deadline64. This avoids comparing different observation windows.

| Case | Planning horizon | Best table(s) | Their closure64 range |
|---|---:|---|---|
| channel-shallow-r1-depth0 | 1 | [['export', 'export']] | [3.3306690738754696e-15, 3.3306690738754696e-15] |
| channel-shallow-r1-depth0 | 4 | [['mix75', 'mix50']] | [0.0, 0.0] |
| channel-shallow-r1-depth0 | 16 | [['mix25', 'mix25']] | [3.6637359812630166e-15, 3.6637359812630166e-15] |
| channel-shallow-r1-depth0 | 64 | [['service', 'mix25']] | [0.0, 0.0] |
| channel-shallow-r1-depth-1 | 1 | [['export', 'export']] | [6.772360450213455e-15, 6.772360450213455e-15] |
| channel-shallow-r1-depth-1 | 4 | [['mix75', 'mix50']] | [0.0, 0.0] |
| channel-shallow-r1-depth-1 | 16 | [['mix25', 'mix25']] | [1.5987211554602254e-14, 1.5987211554602254e-14] |
| channel-shallow-r1-depth-1 | 64 | [['service', 'mix25']] | [5.10702591327572e-15, 5.10702591327572e-15] |
| channel-shallow-r1-depth-2 | 1 | [['export', 'export']] | [1.3322676295501878e-15, 1.3322676295501878e-15] |
| channel-shallow-r1-depth-2 | 4 | [['mix75', 'mix50']] | [4.884981308350689e-15, 4.884981308350689e-15] |
| channel-shallow-r1-depth-2 | 16 | [['mix25', 'mix25']] | [1.3766765505351941e-14, 1.3766765505351941e-14] |
| channel-shallow-r1-depth-2 | 64 | [['service', 'mix25']] | [0.0, 0.0] |
| channel-shallow-r1-depth-4 | 1 | [['export', 'export']] | [1.1546319456101628e-14, 1.1546319456101628e-14] |
| channel-shallow-r1-depth-4 | 4 | [['mix75', 'mix50']] | [7.771561172376096e-15, 7.771561172376096e-15] |
| channel-shallow-r1-depth-4 | 16 | [['mix25', 'mix25']] | [8.770761894538737e-15, 8.770761894538737e-15] |
| channel-shallow-r1-depth-4 | 64 | [['service', 'mix25']] | [5.995204332975845e-15, 5.995204332975845e-15] |

## Prospective shallow-well tests

S1 predicts more stationary usable material than constant servicing; S2 predicts more than constant exporting. These are mechanistic predictions, not protection rewards.

| Case | Usable fraction | Difference vs service | Difference vs export | First function by64 | Function present at64 |
|---|---:|---:|---:|---:|---:|
| channel-shallow-r1-depth0 | 0.662906 | -0.021392 | 0.054549 | 0.950155 | 0.600004 |
| channel-shallow-r1-depth-1 | 0.401875 | -0.037199 | 0.037947 | 0.627806 | 0.256288 |
| channel-shallow-r1-depth-2 | 0.186544 | -0.033986 | 0.012523 | 0.282252 | 0.090436 |
| channel-shallow-r1-depth-4 | 0.028941 | -0.007379 | 0.001199 | 0.039003 | 0.010443 |

Shallower wells shift the winning response toward servicing, but the breadth winner does not maximize usable stock. Recovery queries start with all material trapped, empty fuel and service gates; they are not energy-matched E8 preparation comparisons. Cross-depth values compare different physical laws. First restoration, retained function and permanent closure remain separate.


## Frozen outcomes and readouts

| Case | Outcome | Verdict | Value |
|---|---|---|---:|
| channel-shallow-r1-depth0 | C1-numerics | pass | 2.0250467969162855e-13 |
| channel-shallow-r1-depth0 | C2-seed-reference | open_outcome | 3.437939547532096 |
| channel-shallow-r1-depth0 | C3-closure-risk | open_outcome | 0.0 |
| channel-shallow-r1-depth0 | C4-functioning-margin | open_outcome | -0.2589362315925925 |
| channel-shallow-r1-depth0 | C5-native-rate | open_outcome | 8.747185926254307 |
| channel-shallow-r1-depth0 | C6-uniform-null | unsupported | None |
| channel-shallow-r1-depth0 | S1-usable-vs-service | fail | -0.021391829620459712 |
| channel-shallow-r1-depth0 | S2-usable-vs-export | pass | 0.054549152165091486 |
| channel-shallow-r1-depth0 | S3-usable-vs-idle | open_outcome | -0.029220305789533607 |
| channel-shallow-r1-depth0 | S4-first-return | open_outcome | 0.9501547502543726 |
| channel-shallow-r1-depth0 | S4-retained-return | open_outcome | 0.6000035367640368 |
| channel-shallow-r1-depth-1 | C1-numerics | pass | 4.376499163072367e-13 |
| channel-shallow-r1-depth-1 | C2-seed-reference | open_outcome | 4.774196563230703 |
| channel-shallow-r1-depth-1 | C3-closure-risk | open_outcome | 1.5987211554602254e-14 |
| channel-shallow-r1-depth-1 | C4-functioning-margin | open_outcome | -0.4338906047180129 |
| channel-shallow-r1-depth-1 | C5-native-rate | open_outcome | 7.097682065454721 |
| channel-shallow-r1-depth-1 | C6-uniform-null | unsupported | None |
| channel-shallow-r1-depth-1 | S1-usable-vs-service | fail | -0.03719929504707531 |
| channel-shallow-r1-depth-1 | S2-usable-vs-export | pass | 0.03794721910635007 |
| channel-shallow-r1-depth-1 | S3-usable-vs-idle | open_outcome | -0.04644958154626894 |
| channel-shallow-r1-depth-1 | S4-first-return | open_outcome | 0.627806498542488 |
| channel-shallow-r1-depth-1 | S4-retained-return | open_outcome | 0.2562880961761547 |
| channel-shallow-r1-depth-2 | C1-numerics | pass | 1.2858603071208563e-12 |
| channel-shallow-r1-depth-2 | C2-seed-reference | open_outcome | 3.8911429119355034 |
| channel-shallow-r1-depth-2 | C3-closure-risk | open_outcome | 0.0 |
| channel-shallow-r1-depth-2 | C4-functioning-margin | open_outcome | -0.6164194004050437 |
| channel-shallow-r1-depth-2 | C5-native-rate | open_outcome | 5.836680133006206 |
| channel-shallow-r1-depth-2 | C6-uniform-null | unsupported | None |
| channel-shallow-r1-depth-2 | S1-usable-vs-service | fail | -0.033986241966816655 |
| channel-shallow-r1-depth-2 | S2-usable-vs-export | pass | 0.01252284952210092 |
| channel-shallow-r1-depth-2 | S3-usable-vs-idle | open_outcome | -0.04061019041292918 |
| channel-shallow-r1-depth-2 | S4-first-return | open_outcome | 0.2822520416182236 |
| channel-shallow-r1-depth-2 | S4-retained-return | open_outcome | 0.09043629606959232 |
| channel-shallow-r1-depth-4 | C1-numerics | pass | 5.972999872483342e-12 |
| channel-shallow-r1-depth-4 | C2-seed-reference | open_outcome | 3.8344614464513143 |
| channel-shallow-r1-depth-4 | C3-closure-risk | open_outcome | 7.771561172376096e-15 |
| channel-shallow-r1-depth-4 | C4-functioning-margin | open_outcome | -0.7324222735144538 |
| channel-shallow-r1-depth-4 | C5-native-rate | open_outcome | 4.995182320915751 |
| channel-shallow-r1-depth-4 | C6-uniform-null | unsupported | None |
| channel-shallow-r1-depth-4 | S1-usable-vs-service | fail | -0.007378900545655057 |
| channel-shallow-r1-depth-4 | S2-usable-vs-export | pass | 0.001198592333777098 |
| channel-shallow-r1-depth-4 | S3-usable-vs-idle | open_outcome | -0.008749575966534973 |
| channel-shallow-r1-depth-4 | S4-first-return | open_outcome | 0.039002575583164445 |
| channel-shallow-r1-depth-4 | S4-retained-return | open_outcome | 0.010443125367820211 |

All policy rows, horizons, stationary usable/active expectations and resource/closure summaries are retained compactly in SUMMARY.json. Full state lists, class vectors and raw outputs stay local and reconstructible.

The initial uniform run emitted a descriptive closure-tension flag from~1e-15 rounding differences. Its registered analytic-null check passed; interpretation uses the1e-9 guard. No primary score, predicate verdict or raw record was altered.

Stationary observations derived from old class vectors are post-run readouts; new shallow-case predictions were filed before those runs. First-hit recovery and retained function are kept distinct. Two assisted events can include turnover and are not lineage-resolved open-ended compounding.

## Execution

- channel-scientific-worn_reversible-20261013T135859Z-94efa0: 312.06s, 581.59MiB, input `898436cf76b733721ca7eb250f6ed670df38fa520e96c6e6ba40a07773c82b8c`.
- channel-scientific-worn_reversible-20261013T135909Z-0bcc19: 311.07s, 581.66MiB, input `df9e781bf2f06907a1f2d51d510977bf80e415c2a8d60e37e30e61c4f419d389`.
- channel-scientific-worn_reversible-20261013T140441Z-a5eacc: 314.21s, 581.68MiB, input `1abeb53f5ed5f2664f5ad9493869cf6a4bd4d0c293892d3d05ebba7fda162cd2`.
- channel-scientific-worn_reversible-20261013T140451Z-2b4a8d: 312.33s, 582.23MiB, input `3a8f86cff1c70290103840e3199de300b713e04b1a42497505e1a0734f848f57`.

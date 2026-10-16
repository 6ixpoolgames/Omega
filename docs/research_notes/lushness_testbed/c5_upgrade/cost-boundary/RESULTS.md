# C5 cost-boundary: results

Status: **complete**; 4/4 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| passive-bill1 | passive-bill1 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract-bill1 | passive-bill1 | +59.71526 | [-3.98888, +3.17890] | [+58.90808, +134.90323] | +0.095639 |
| passive-bill1.5 | passive-bill1.5 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract-bill1.5 | passive-bill1.5 | +32.57958 | [+32.99878, +70.04571] | [+32.31879, +83.51297] | +0.062567 |

## Physical mechanism at T256

| Case | D owned energy | S owned energy | Physical bill | Net receiver transfer | D time-mean function | S time-mean function |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| passive-bill1 | 1.384912 | 0.768363 | 0.006262 | -0.001429 | 0.496329 | 0.567556 |
| extract-bill1 | 1.383612 | 0.686771 | 0.966149 | -0.003567 | 0.495191 | 0.527916 |
| passive-bill1.5 | 1.385684 | 0.768660 | 0.006389 | -0.003346 | 0.496265 | 0.567612 |
| extract-bill1.5 | 1.389374 | 0.699303 | 0.805301 | -0.270440 | 0.493078 | 0.543802 |

Owned-energy columns are endpoint stocks. Per-family integrated changes independently close against them; source capture minus intervention bill is not substituted for that full balance. The driven-debit and ordinary apparatus arms use their declared physical mechanisms, not equal realized fuel or activity.
Physical bill is signed receiver-path handling loss minus reverse refunds; net receiver transfer includes the transfer module's bank changes. At bill one the forward receiver pathway gives D zero net bank increment; above one it debits D as well as S. These are boundary probes, not necessarily material appropriation.

## Verification and scope

Maximum checked numerical/resource residual: 8.74e-10.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `06967ed1e590187d1df2d290a1424ebf9c4598596069ffbed78bfb5bbbfa9a77`. Receipts verify imports, configurations, checksums and caps.

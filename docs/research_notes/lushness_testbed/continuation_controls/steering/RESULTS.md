# Corrected movement steering: results

Status: **complete**, 16/16 cases verified.

Finite sampled-history lushness is primary. Subject intervals are conditioning bounds. No random events are subtracted.

## T256, cadence 0.25, relative to idle

| Yield | Mode | Strength | Whole Δ | S bounds | Pocket arrival Δ | S net capture Δ |
| ---: | --- | ---: | ---: | --- | ---: | ---: |
| 0 | blocking | 0.95 | 32.6468 | [26.1167, 31.7716] | -0.0923 | 0.2308 |
| 0 | steering | 0.55 | 16.7839 | [14.1531, 18.9789] | -0.0443 | 0.1178 |
| 0 | steering | 0.95 | 33.4614 | [29.9437, 35.6179] | -0.0922 | 0.2342 |
| 1 | blocking | 0.95 | 30.0036 | [22.2323, 32.6210] | -0.0923 | -0.0613 |
| 1 | steering | 0.55 | 15.3061 | [10.6948, 20.5670] | -0.0443 | -0.0303 |
| 1 | steering | 0.95 | 30.7984 | [25.9697, 36.3767] | -0.0922 | -0.0581 |
| 4 | blocking | 0.95 | 22.9093 | [4.9381, 34.4833] | -0.0923 | -0.1497 |
| 4 | steering | 0.55 | 11.6984 | [-3.3998, 26.8064] | -0.0443 | -0.0748 |
| 4 | steering | 0.95 | 23.6969 | [8.6505, 38.2129] | -0.0922 | -0.1466 |
| 16 | blocking | 0.95 | 14.9284 | [-30.4495, 48.0499] | -0.0923 | -0.1816 |
| 16 | steering | 0.55 | 7.6677 | [-34.8853, 47.2764] | -0.0443 | -0.0908 |
| 16 | steering | 0.95 | 15.7117 | [-26.7470, 51.7674] | -0.0922 | -0.1785 |

Adjacent tested-yield sign brackets: **0** (mode × strength × clock × horizon; not independent trials).

Only movement is redirected. Native chemistry and pocket-to-trap return retain their rates at the same physical state. Active steering is still the original coarse driven boundary, not the paired transfer chemistry. The declared half-unit energy grid differs from the old tenth-unit map. No claim extends beyond the tested yield range or clocks.

Largest checked numerical/resource residual: 1.4e-09.

Numerical source: `53b289eb3e7e61656f2c48060e84f4b898e487bcac0df8ecc8d027f426b28e1a`. Exact source, configurations and receipts are retained; no full kernels are stored.

# Four-arm register control — results

All 216 registered arm/cadence analyses completed.
A0 is the tracking/no-response control also called B_T. B_R has no escape drive.

## Primary resolved differences: T64, cadence 0.25

| Parent | Upkeep / basal | B_R-B | A0-A | A-B_R |
| --- | ---: | ---: | ---: | ---: |
| W1-00 | 0 | +1.845811 | +0.432077 | -1.495463 |
| W1-00 | 0.01 | +1.824912 | +0.430075 | -1.493243 |
| W1-00 | 0.05 | +1.742170 | +0.422150 | -1.484232 |
| W1-00 | 0.1 | +1.640653 | +0.412427 | -1.472707 |
| W1-00 | 0.25 | +1.348599 | +0.384560 | -1.436852 |
| W1-00 | 0.5 | +0.901528 | +0.342620 | -1.375107 |
| W1-00 | 1 | +0.138332 | +0.274682 | -1.254559 |
| W1-00 | 2 | -0.996717 | +0.186083 | -1.052481 |
| W1-00 | 4 | -2.381710 | +0.102028 | -0.792175 |
| W1-08 | 0 | +1.809911 | +0.553174 | -1.575661 |
| W1-08 | 0.01 | +1.791031 | +0.550241 | -1.573091 |
| W1-08 | 0.05 | +1.716231 | +0.538689 | -1.562747 |
| W1-08 | 0.1 | +1.624345 | +0.524651 | -1.549699 |
| W1-08 | 0.25 | +1.359288 | +0.485143 | -1.510090 |
| W1-08 | 0.5 | +0.951429 | +0.427386 | -1.444094 |
| W1-08 | 1 | +0.249030 | +0.337162 | -1.319188 |
| W1-08 | 2 | -0.810197 | +0.224087 | -1.113894 |
| W1-08 | 4 | -2.125476 | +0.120633 | -0.849658 |

## Registered predictions

- R1: passed — B_R beats B at positive-cost reference for both parents, primary horizon/cadence
- R2: passed — B_R loses to B at upkeep ratio4 for both parents, primary horizon/cadence
- R3: passed — A0 beats A at reference for both parents, primary horizon/cadence

## Matching and scope

Rates were calibrated using physical occupancy and switch count only, then held fixed.
Matching applies at upkeep ratio 0.05/T64; moments elsewhere are outcomes, not refit targets.
Total charging differs despite identical unit bills. Correlations are not matched.
The remaining cost/correlation differences limit causal attribution to internal variation alone.
No new suffering kill or subjective-valence verdict is scored from these controls.

## Execution

Wall time 48.746s; peak 140.8 MiB.
Maximum residual 9.09e-13; no cap hit.
Input hash `c69e16113f3d89b953f8063b31c8a7d701b2c83b0cf96109783eb03d3a83eda5`.
Outward corrections of equal-bound floating-point reversals: 111, within frozen residual tolerance.
Full finite/limiting surfaces and physical readouts: REGISTER_CONTROL_SUMMARY.json.
Adjacency brackets are not exact roots; multiple or absent crossings are retained.

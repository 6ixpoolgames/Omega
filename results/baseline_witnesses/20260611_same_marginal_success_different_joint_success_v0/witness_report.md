# Same Marginal Success, Different Joint Success Witness

Witness ID: `same_marginal_success_different_joint_success_v0`

Status: `same_marginal_success_different_joint_success`

## Controlled Baseline

```text
controls_hold: True
same_marginal_success: True
correlated_marginal_success_vector: D_A:3/4;D_B:3/4
independent_marginal_success_vector: D_A:3/4;D_B:3/4
```

The controlled marginal baseline is Bayes-best single-bit recovery success for
`D_A` and `D_B`, not exact marginal preservation.

## Joint Difference

```text
correlated_joint_success_fraction: 5/8
independent_joint_success_fraction: 9/16
```

## Read

Matched marginal diagnostic success does not determine joint recovery success.

## Not Claimed

```text
exact marginal preservation
Omega validation
value detection
valuer detection
agency detection
identity detection
semantic recovery
substrate-general theory validation
```

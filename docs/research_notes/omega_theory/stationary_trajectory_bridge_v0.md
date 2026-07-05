# Stationary Trajectory Bridge v0

Status: Lean theorem note / B2 positive trajectory bridge
Scope: stationary-policy infinite traces for finite possibilistic
ambiguity-family robust viability under shared-action / switching robust
semantics
Claim boundary: positive bridge only; not maximal finite deadlock semantics, not
the converse from trajectories to fixed points, not stochastic, not a
derivation that persistence is required, not value, not agency, not
valuerhood, not moral standing, not Omega validation

## Compression

The fixed-point containment stack now has an operational positive reading.

If a stationary policy guarantees from `x` in the fixed-point sense, then for
every model in the ambiguity family there exists an infinite trace:

```text
trace : Nat -> State
trace 0 = x
Step_i (trace n) (policy (trace n)) (trace (n+1))
```

and every trace state remains inside:

```text
PolicyKernel(policy)
Constraint
Requirement
RVK
```

The theorem is intentionally one-way. It extracts infinite traces from a
closed-loop kernel; it does not try to characterize all possible maximal finite
or infinite trajectories.

The extracted traces are per declared model, but the guarantee being witnessed
is still the shared-action robust guarantee. This note does not characterize
unknown-but-fixed adaptive learning, where observations can shrink the remaining
model set.

## Landed Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/TrajectoryBridge.lean
formal/lean/OmegaProper/Decision/TrajectoryBridgeExamples.lean
```

Checked theorem surface:

```text
InfinitePolicyTrace for one stationary policy and one model;
PolicyKernel membership extracts a dependent infinite trace;
the extracted trace follows the policy in the selected model;
the extracted trace remains in PolicyKernel, Constraint, Requirement, and RVK;
every RVK state has such a trace under the extracted RVK policy.
```

## W1 Reading

In the W1 strictness family:

```text
ok:
  has an extracted infinite trace in each model under the RVK policy,
  and that trace stays inside shared-action RVK.

start:
  still has no stationary or history-policy guarantee, because no shared
  action is safe across both models.
```

## Nonclaims

This note does not formalize the converse theorem. It does not yet say that an
externally supplied trajectory property implies fixed-point membership. It also
does not define maximal finite trajectories or prove a deadlocked maximal
trajectory witness from every non-RVK state. It does not cover adaptive
fixed-world identification.

## Next Step

The B2 fixed-point and positive-trajectory spine is now stable enough to pause
for audit. A future pass can add maximal finite deadlock semantics only if a
paper or review target needs the stronger converse reading.

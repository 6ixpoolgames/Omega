# History-Policy Memorylessness v0

Status: Lean theorem note / B2 fixed-point memorylessness checkpoint
Scope: history-policy guarantee kernels for finite possibilistic
ambiguity-family robust viability
Claim boundary: not trajectory/maximality semantics, not stochastic, not a
derivation that persistence is required, not value, not agency, not
valuerhood, not moral standing, not Omega validation

## Compression

At the fixed-point guarantee level, history dependence does not enlarge the
shared-action robust viability region.

A history policy has type:

```text
HistoryPolicy := List State -> State -> Action
```

Its guarantee kernel is a greatest fixed point over `(history, current state)`
pairs. The successor condition extends the history before checking the next
state.

The landed theorem is:

```text
exists history policy guaranteeing from x
  iff x in RVK
  iff exists stationary policy guaranteeing from x
```

So no amount of finite-history conditioning permits guaranteed persistence from
outside the ambiguity-family RVK.

## Landed Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/HistoryContainment.lean
formal/lean/OmegaProper/Decision/HistoryContainmentExamples.lean
```

Checked theorem surface:

```text
HistoryPolicy as finite-history-dependent action selection;
HistoryKernel as a gfp over `(history, state)` pairs;
some history-policy guarantee is postfixed for the RVK operator;
any history-policy guarantee implies RVK membership;
the RVK stationary policy is also a history policy;
history-policy guarantee existence iff RVK;
history-policy guarantee existence iff stationary guarantee existence.
```

## W1 Reading

The W1 shared-action strictness witness also separates history dependence from
robust guarantee:

```text
ok:
  has both stationary and history-policy guarantees.

start:
  has neither, despite lying in every per-model corridor.
```

The failure at `start` is not lack of memory. It is lack of one action that is
safe and enabled across the ambiguity family.

## Nonclaims

This note does not formalize infinite trajectories or maximal finite
deadlock-failure semantics. It does not prove that persistence is required or
that the declared constraint/requirement/ambiguity family is correct. It only
proves that fixed-point history-policy guarantees collapse to the already
defined RVK.

## Next Step

The remaining B2 theorem work is the trajectory bridge: connect the fixed-point
guarantee surface to explicit infinite/maximal trajectory semantics without
duplicating the fixed-point proof.

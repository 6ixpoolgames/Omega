# Contextual Future Fields And Holonomy v0

Status: finite pilot note
Scope: contextual completions, local-to-global obstruction, finite transport-loop holonomy
Claim boundary: not quantum mechanics, not Hilbert-space structure, not value, not agency, not identity, not valuerhood, not moral standing, not Omega validation

## Purpose

This note records the first four finite pilots from the contextual future-field
branch:

```text
1. local future-context data can be nonempty and overlap-compatible while still
   admitting no global extension;

2. a loop can return a visible proxy while transporting the underlying
   continuation profile nontrivially;

3. certified overlap data gives a positive-semidefinite
   compatibility-thickness kernel, while arbitrary declared compatibility
   tables need not;

4. before/after kernel comparisons separate diagonal thickness change from
   off-diagonal compatibility change.
```

These are pre-Hilbert, pre-phase artifacts. They do not claim that futures are
quantum. They establish finite shapes that any later contextual,
density-kernel, or Hilbert representation will need to respect.

## Why This Branch Exists

The current Omega ambition treats Omega not as one final target but as a family
of maximal compatible continuations. That immediately raises two questions:

```text
local/global:
  do local compatibility views glue into a single global arbitration object?

path dependence:
  if a process returns to the same visible endpoint or proxy, did the
  continuation profile return with it?

kernel readiness:
  does a declared compatibility/thickness table actually admit a PSD
  Gram-style representation?

deformation:
  does a transformation change own thickness, shared compatibility, or both?
```

The new pilots are small finite witnesses for those questions. They are
designed to sit below value and agency. Their role is to make the future-field
geometry auditable before any value-bearing interpretation is added.

## Artifact 1: No Global Extension

Code:

```text
omega/contextual_future_fields/model.py
omega/contextual_future_fields/witnesses.py
```

Validation:

```text
python -m omega.validation.contextual_future_fields
```

The witness uses three binary variables:

```text
A, B, C
```

and three local contexts:

```text
AB_equal:
  A = B

BC_equal:
  B = C

AC_unequal:
  A != C
```

Each local context has valid local sections. Each pair of contexts has matching
support and uniform marginal distribution on its overlap:

```text
AB and BC agree on possible B values;
AB and AC agree on possible A values;
BC and AC agree on possible C values.
```

But no global assignment to `A, B, C` satisfies all three local constraints:

```text
A = B
B = C
A != C
```

This is the intended finite reading:

```text
local compatibility can be real without determining a global extension.
```

What this does not prove:

```text
not sheaf cohomology;
not quantum contextuality;
not Bell nonlocality;
not value pluralism;
not moral incompatibility.
```

It is only the support-level local/global obstruction that a later sheaf or
contextual-probability layer can generalize.

## Artifact 4: Finite Holonomy

The holonomy pilot defines finite profile coordinates and finite partial
transport maps between contexts:

```text
A -> B -> C -> A
```

The loop is nontrivial when the visible proxy returns but the composed
transport is not the identity on the continuation profile.

Two controls are retained.

### Same Proxy, Lossy Holonomy

Initial profile:

```text
score = 1
oversight = 1
corrigibility = 1
interpretability = 1
```

The composed transport returns:

```text
score = 1
corrigibility = 1
oversight = 0
interpretability = 0
```

The visible proxy `score` returns. The continuation profile does not.

Reading:

```text
same visible score does not certify same transported continuation profile.
```

### Same Proxy, Orientation Twist

Initial profile:

```text
score = 1
route_left = 1
route_right = 0
```

The loop returns:

```text
score = 1
route_left = 0
route_right = 1
```

Total continuation thickness is preserved:

```text
route_left + route_right = 1
```

but orientation/coordinate assignment changes.

Reading:

```text
holonomy is not only loss. A loop can preserve visible proxy and total
thickness while changing the transported continuation orientation.
```

This is deliberately not complex phase. It is the finite set/vector precursor:

```text
loop transport can be nonidentity before any Hilbert representation is claimed.
```

## Artifact 2: Compatibility-Thickness Kernel

Code:

```text
omega/contextual_future_fields/kernel.py
omega/contextual_future_fields/witnesses.py
```

The kernel pilot defines finite continuation profiles as sets of certified
continuation atoms. A weighted atom measure supplies thickness:

```text
thickness(profile_i)
  =
  total weight of atoms in profile_i
```

and compatibility:

```text
K_ij
  =
  total weight of atoms shared by profile_i and profile_j.
```

This is PSD by construction because it is the Gram matrix of weighted indicator
vectors:

```text
profile_i -> 1_{atoms in profile_i}.
```

The retained positive kernel has profiles:

```text
alpha:
  a, shared_ab

beta:
  b, shared_ab, shared_bc

gamma:
  c, shared_bc
```

with unit atom weights. Its matrix is:

```text
alpha beta gamma
  2     1     0
  1     3     1
  0     1     2
```

The negative control is a symmetric nonnegative declared table:

```text
alpha beta gamma
  1     1     1
  1     1     0
  1     0     1
```

It fails PSD because one principal determinant is `-1`. This blocks the cheap
move:

```text
any symmetric compatibility table is Hilbert-ready.
```

The current claim is only:

```text
certified overlap kernels have a Gram/PSD interpretation;
arbitrary declared compatibility tables may not.
```

It does not claim a canonical value kernel or global density operator.

## Artifact 3: Density-Kernel Deformation

The operator/deformer bridge is deliberately stated as a before/after kernel
comparison:

```text
K_before -> K_after
```

not as a physical operator, agency detector, or value-loss claim.

Two controls are retained.

### Diagonal Preserved, Compatibility Damaged

Before:

```text
left:
  left_private, shared

right:
  right_private, shared
```

After:

```text
left:
  left_private, left_replacement

right:
  right_private, right_replacement
```

Both profiles keep thickness `2`, but their shared compatibility drops from
`1` to `0`.

Reading:

```text
own thickness can be preserved while off-diagonal compatibility is damaged.
```

### Diagonal Thinning, Off-Diagonal Preserved

Before:

```text
left:
  left_private, shared

right:
  right_private
```

After:

```text
left:
  left_private

right:
  right_private
```

The `left` profile loses one unit of thickness. Off-diagonal compatibility
remains zero.

Reading:

```text
thickness deformation and compatibility deformation are separate finite axes.
```

These controls make the deformer language more precise:

```text
a finite deformer can be represented as a transformation of the
compatibility-thickness kernel, and the transformation can affect diagonal
thickness and off-diagonal compatibility independently.
```

This is still pre-agency and pre-value.

## Relation To Compatibility

The no-global-extension witness uses compatibility in the weakest local sense:

```text
a local context has compatible sections when its local constraints are
satisfiable.
```

The witness then shows that:

```text
overlap-compatible local contexts
do not necessarily determine
a globally compatible joint assignment.
```

This is why the project should not define one global `Compatible` relation too
early. Compatibility should remain typed:

```text
local compatibility;
joint compatibility;
robust compatibility;
transport compatibility;
global compatibility.
```

The pilot only addresses the first-to-global gap.

## Relation To Density Kernels

This pilot now defines the first compatibility-thickness kernel, but only in
the safest overlap-certified form.

The current kernel uses:

```text
K_ii = thickness(profile_i)
K_ij = certified overlap supporting profile_i and profile_j
```

If future `K_ij` definitions use richer joint viability, recovery, or
compatibility facts, they should be checked against this same PSD gate. If a
candidate kernel is not PSD, that is meaningful:

```text
the declared compatibility-thickness data does not admit a Hilbert/Gram
representation without repair, signed weights, or a different kernel.
```

## Relation To Hilbert Space And Phase

This branch keeps three gates separate:

```text
Gate 1:
  local future-context data may fail to glue globally.

Gate 2:
  compatibility plus thickness may or may not form a PSD kernel.

Gate 3:
  loop transport may or may not carry an orientation requiring complex phase.
```

This note implements Gate 1, a first overlap-certified Gate 2, and a finite
precursor to Gate 3. It does not
claim:

```text
Hilbert space;
density operators;
Born rule;
complex phase;
quantum futures.
```

## Retained Result

Retained result location:

```text
docs/research_notes/validation_results/contextual_future_fields_v0/
```

The retained summary reports:

```text
no-global-extension witness: PASS
finite holonomy witnesses: PASS
compatibility-thickness kernel: PASS
density-kernel deformation: PASS
```

Focused test command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_contextual_future_fields.py -q
```

## Public Compression

The current result can be summarized as:

```text
Local future-context compatibility need not glue into a global continuation
object; visible endpoint/proxy recovery need not imply trivial transport of
the underlying continuation profile; certified overlap data can form a PSD
compatibility-thickness kernel; and diagonal thickness change is separate from
off-diagonal compatibility change.
```

That is the disciplined finite core of the contextual/holonomy branch.

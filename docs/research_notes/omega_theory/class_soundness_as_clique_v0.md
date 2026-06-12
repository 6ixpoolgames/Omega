# Class Soundness as Clique Soundness v0

Status: branch exploration note

This note translates the class guardrail into standard graph language.

## Compression

Given a consequence system, define a compatibility graph:

```text
vertices:
  fragments

edge(x,y):
  x and y are consequence-compatible
```

A class is sound exactly when it is a clique in this graph:

```text
sound class = every pair of members is compatible
```

This is already the content of `ClassRespectsConsequences`; the clique wording
makes the requirement legible to readers who do not know the internal
terminology.

## Chain Evidence Is Not Class Soundness

Chain-connectedness is weaker than clique soundness.

The minimal counterexample is the three-vertex path:

```text
a -- b -- c
```

There is a chain from `a` to `c`, but there is no edge `a -- c`. The full class
`{a,b,c}` is connected, but it is not a clique.

Therefore:

```text
chain evidence does not license class soundness
connected component does not imply valid quotient class
```

This is the graph-theoretic version of the existing guardrail:

```text
connectedness is not identity
```

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/ClassSoundnessAsClique.lean
```

The Lean module proves:

```text
ClassRespectsConsequences iff clique in the compatibility graph
three-node path is a tolerance relation
the endpoints are chain-connected
the endpoints are not compatible
the full class is not a clique
```

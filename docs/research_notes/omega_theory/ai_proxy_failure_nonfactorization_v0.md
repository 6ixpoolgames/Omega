# AI Proxy Failure as Non-Factorization v0

Status: alignment-facing worked pattern
Scope: simplified benchmark/reward-model proxy failure
Claim boundary: not a deployed-AI result; not empirical validation; not Omega validation

## Purpose

This note translates the repo's non-factorization theorem into a familiar
alignment shape:

```text
same proxy score;
different safety-relevant target;
therefore the proxy does not determine the target.
```

This is the simplest anti-Goodhart use case.

## Generic Pattern

Let:

```text
System:
  a candidate model, policy, trajectory, run, or evaluation artifact

proxy : System -> Score
  benchmark score, reward-model score, approval score, capability score,
  compression score, or safety-monitor summary

target : System -> SafetyFact
  the declared safety-relevant fact we actually care about
```

If there are two systems `A` and `B` such that:

```text
proxy A = proxy B
target A != target B
```

then:

```text
NonFactorization proxy target
```

The target cannot be recovered from the proxy alone.

## Minimal Alignment Example

Use a deliberately tiny model:

```text
System A:
  completes the task;
  preserves a side-effect-sensitive option.

System B:
  completes the task;
  destroys the side-effect-sensitive option.
```

Proxy:

```text
task_success : System -> Bool
```

Target:

```text
option_preserved : System -> Bool
```

If both systems complete the task but only one preserves the option:

```text
task_success A = task_success B
option_preserved A != option_preserved B
```

then task success does not determine option preservation.

This is not a full side-effect measure. It is the theorem-shaped warning that a
task-success proxy is insufficient for a side-effect target.

## Reward-Model Version

Replace `task_success` with:

```text
reward_model_score : System -> Score
```

and define a safety target:

```text
no_irreversible_loss : System -> Bool
```

A witness has shape:

```text
reward_model_score A = reward_model_score B
no_irreversible_loss A != no_irreversible_loss B
```

Then the reward-model score does not determine the irreversible-loss target.

The project should eventually instantiate this pattern in a small environment
with explicit transitions and retained artifacts.

## Benchmark Version

Replace the proxy with a benchmark:

```text
benchmark_score : System -> Score
```

Target:

```text
deception_flag
side_effect_flag
shutdown_option_preserved
human_override_preserved
capability_boundary_respected
```

The theorem shape remains:

```text
same benchmark score + different target fact
  -> benchmark score is not sufficient for that target.
```

## What This Proves

It proves only:

```text
the proxy does not determine the declared target.
```

This is still useful. It blocks a common move:

```text
the benchmark went up, so the target is safe.
```

That inference is invalid unless the target factors through the benchmark or a
separate preservation theorem is supplied.

## What This Does Not Prove

It does not prove:

```text
the target is the right target;
the proxy is useless for all purposes;
the model is unsafe in deployment;
the theorem scales automatically to LLMs;
Omega has been validated.
```

Those require adapter provenance, empirical fixtures, and stronger target
semantics.

## Next Concrete Instantiation

A good near-term implementation would define a tiny planning environment:

```text
states:
  start, task_done_safe, task_done_loss

proxy:
  task_done?

target:
  option_preserved?
```

Then prove or test:

```text
same proxy value;
different target value;
NonFactorization proxy target.
```

The point is not novelty. The point is onboarding: it gives alignment readers a
familiar example of the repo's theorem shape.

## Related Notes

- [continuation_deformation_nonfactorization_v0.md](continuation_deformation_nonfactorization_v0.md)
- [nonfactorization_witness_index_v0.md](nonfactorization_witness_index_v0.md)
- [adapter_provenance_v0.md](adapter_provenance_v0.md)
- [bad_panel_taxonomy_v0.md](bad_panel_taxonomy_v0.md)

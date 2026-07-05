# Finite Relational Adaptive Fixed-World Corridor B2.1

Status: PASS

## Headline

- Cases: 3
- Learnable ambiguity cases: 1
- Unlearnable ambiguity cases: 1
- Fake-update failure cases: 1
- Sound-update truth-preservation failures: 0

## Case Breakdown

| case | switching start | adaptive start | frozen start | load-bearing actions | read |
| --- | ---: | ---: | ---: | --- | --- |
| learnable_ambiguity | False | True | False | `probe` | safe learning expands beyond switching |
| unlearnable_ambiguity | False | False | False | `none` | unsafe/unavailable learning cannot expand |
| fake_update_phantom_corridor | False | True | False | `probe` | fabricated identification creates phantom corridor |

## Read

The learnable witness separates switching ambiguity from fixed-world adaptive ambiguity: a safe probe is outside the ordinary switching corridor but inside the lifted information-state corridor.

The unlearnable witness shows that singleton-model viability does not imply full adaptive viability when no safe shared identification action exists.

The fake-update witness retains the learning-layer phantom: dropping the true model can create a fake corridor state whose selected action fails in the excluded world.

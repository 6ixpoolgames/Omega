# Weighted trajectory-covering probe v0

2026-10-05. Exploratory measurement run on mathematical controls. No new chemistry,
no selected lushness invariant and no required winner.

## Main finite-resolution results

Four observations at 0,T/4,T/2,3T/4, held for T/4 each. The table uses T=1,
fractional mismatch tolerance .25 and probability depth .90. These are exact
minimum covers of the finite observed law (floating-point probabilities).

| Case | Frame | Minimum representatives |
|---|---|---:|
| stationary_0.05 | whole | 2 |
| stationary_1 | whole | 3 |
| stationary_10 | whole | 4 |
| accelerated_0.1 | whole | 1 |
| accelerated_1 | whole | 2 |
| accelerated_10 | whole | 2 |
| noise_0 | whole | 2 |
| noise_0.1 | whole | 2 |
| noise_10 | whole | 4 |
| coupled | whole | 2 |
| coupled | destination | 2 |
| disconnected | whole | 2 |
| disconnected | destination | 1 |

## Reversible kinetic access

Probability of first visiting the other state by the deadline, starting at zero.
This is a physical access diagnostic, not a new score or an ethical target.

| Rate | T | First-hit probability | Cover at fractional .25, alpha .90 |
|---:|---:|---:|---:|
| 0.1 | 0.5 | 0.048771 | 1 |
| 1 | 0.5 | 0.393469 | 2 |
| 10 | 0.5 | 0.993262 | 2 |
| 0.1 | 1 | 0.095163 | 1 |
| 1 | 1 | 0.632121 | 2 |
| 10 | 1 | 0.999955 | 2 |
| 0.1 | 4 | 0.329680 | 1 |
| 1 | 4 | 0.981684 | 2 |
| 10 | 4 | 1.000000 | 2 |

## Coupling contrast

Coupled D=S xor E versus disconnected D=E, with S static/fair and the same
error-clock law. A bijection of full state symbols makes whole-state distances
and probabilities identical. It does not make the physical wirings equivalent.
The event-count law also matches. Local destination frames can break the tie.

| Case | I(S;D) at T=1, bits |
|---|---:|
| coupled | 0.669988 |
| disconnected | 0.000000 |

Whole-frame ties: 36/36.

## Reconvergence and concentration

| Case | T | Tolerance type | Tolerance | Alpha | Cover |
|---|---:|---|---:|---:|---:|
| reconvergence | 1 | absolute | 0.4 | 0.9 | 2 |
| reconvergence | 1 | fractional | 0.25 | 0.9 | 2 |
| reconvergence | 2 | absolute | 0.4 | 0.9 | 2 |
| reconvergence | 2 | fractional | 0.25 | 0.9 | 1 |
| reconvergence | 4 | absolute | 0.4 | 0.9 | 2 |
| reconvergence | 4 | fractional | 0.25 | 0.9 | 1 |
| construction_0.5 | 1 | absolute | 0.25 | 0.9 | 2 |
| construction_0.9 | 1 | absolute | 0.25 | 0.9 | 1 |
| construction_0.99 | 1 | absolute | 0.25 | 0.9 | 1 |
| construction_1 | 1 | absolute | 0.25 | 0.9 | 1 |
| deterministic_idle | 1 | absolute | 0.25 | 0.9 | 1 |

Reconvergent histories differ for exactly .5 physical time units. Fractional
tolerance dilutes that fixed prefix as T increases; fixed absolute tolerance does
not. Construction succeeds more reliably as its law concentrates, so required
representatives can decrease. A deterministic construction and idle both need one.
These scheduled finite-support paths are exact mathematical controls, not
thermodynamically matched chemical preparations.

## Continuous jump-time check

64 training histories and 2048 independent evaluation histories per row family.
Distances use the exact jump times of supplied histories. Centers are restricted
to the training sample; fitted alpha is .90. Solver bounds concern the empirical
optimization only. The interval measures held-out coverage of that fixed cover,
not uncertainty in the unknown optimal population covering number.

| Case | Absolute tolerance | Empirical N bounds | Training coverage | Held-out coverage (95% interval) |
|---|---:|---:|---:|---|
| stationary_0.05 | 0.25 | 2–2 | 1.000 | 0.975 (0.967–0.981) |
| stationary_0.05 | 0.5 | 2–2 | 1.000 | 1.000 (0.998–1.000) |
| stationary_1 | 0.25 | 5–5 | 0.906 | 0.898 (0.884–0.910) |
| stationary_1 | 0.5 | 2–2 | 0.969 | 0.926 (0.914–0.937) |
| stationary_10 | 0.25 | 37–37 | 0.906 | 0.315 (0.296–0.336) |
| stationary_10 | 0.5 | 2–2 | 0.906 | 0.750 (0.731–0.768) |
| fixed_zero_0.05 | 0.25 | 1–1 | 0.969 | 0.974 (0.966–0.980) |
| fixed_zero_0.05 | 0.5 | 1–1 | 1.000 | 0.992 (0.987–0.995) |
| fixed_zero_1 | 0.25 | 3–3 | 0.922 | 0.828 (0.811–0.843) |
| fixed_zero_1 | 0.5 | 2–2 | 0.969 | 0.931 (0.919–0.941) |
| fixed_zero_10 | 0.25 | 39–39 | 0.906 | 0.405 (0.384–0.427) |
| fixed_zero_10 | 0.5 | 2–2 | 0.969 | 0.865 (0.850–0.879) |

## Assessment

- The extent avoids the one-time occupancy collapse and detects temporal laws.
- Rapid independent noise can increase the cover. It remains in the physical law.
- Greater reliability need not increase the cover; it can lower diversity.
- Whole-state equality distance can tie physically different couplings. The local
  frame profile retains some distinctions that the whole-frame number loses.
- Common-suffix dilution is a scale effect, not deletion from the full history.
- Finite empirical optimization does not establish coverage of rare population
  histories. Small samples may substantially underestimate the required cover.
- These results support trajectory covering as a temporal-diversity extent.
  They do not establish it as lushness or identify harm with fewer covers.

## Reproduction and scope

`python -m omega_v2.validation.path_covering_v0 --workers 6`

Runtime: 2.84 seconds. Finite coordinates: 756; complete
finite-support coordinates: 97; continuous empirical fits: 12.
Native laws, frame maps, all finite probabilities, witnesses, simulation seeds,
training/evaluation paths and distance matrices are saved in [raw evidence](path_covering_v0/).
The continuous-time support can require infinite covers; no finite-dimension
or whole-support claim follows from this finite-resolution study.

[Protocol](path_covering_protocol_v0.md).
[Candidate assessment](sol_path_covering_assessment_2026-10-05.md).

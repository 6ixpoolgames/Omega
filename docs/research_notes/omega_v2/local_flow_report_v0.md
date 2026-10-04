# Local flow and continuation response v0

3 October 2026 · exploratory classical adapter

## What changed

This independently implemented six-register model builds on Opus's flow-probe form, not its unavailable code. It retains K(t)=exp(tQ), the complete joint transition law, and compares separate projections of it. No scalar lushness score or preferred architecture is imposed. Thirty-three small parameter cases and six actual lags are evaluated by finite matrices.

## One local rate family

Each reservoir mechanism flips one register. With target predicate f of other registers, the rate is k exp((-Delta E + mu d)/2), where d=+1 towards f and -1 away. An optional gate multiplies both forward and reverse rates by another register's value. Predicates never depend on the flipped register, so the forward/reverse ratio is exp(-Delta E+mu d). Energy and chemical work are in thermal units.

Every site has an undriven noise mechanism, rate 0.02 at site 0 and 0.1 elsewhere before the energy factor. Directed mechanisms have prefactor 1 and drives 0,2,4,8. All channel truth tables, gates and rates are in the evidence. Geometry is the declared coupling network; clock, sensor and relay are descriptions of that wiring, not scoring labels. Changing wiring changes the physical model. No equal construction or equal burn claim is made.

Zero drive gives detailed balance with exp(-E). The separate passive-pair control has E=2 when sites 0 and 1 disagree. Other energy tables are zero. Reservoir channels stay distinct when computing entropy production, so opposite driven mechanisms are not hidden by summing their rates first. The bath's microscopic records are not represented: this is an open-system adapter with maintained reservoirs, not the complete quantum field or a finite-fuel generativity experiment. Local updates do not establish a relativistic light cone.

## Three distinct questions

- Held information: I(X_i(0); X_F(t)), using the actual joint initial law and K(t).
- Extra prediction: I(X_i(0); X_rest(t) | X_rest(0)). A perfect existing copy can make this zero.
- Flip response: sum_x w_i(x) TV(K(t)(x)|F, K(t)(x xor 2^i)|F). Here w_i is the normalized actual flux of the native undriven flip mechanism under the initial law; its event rate is also retained. The paired reference skips that flip. This is a counterfactual response contrast, not an additional sampled branch, an accessible decoder, or a positive/negative value assignment.

These are computed for every site and every subset, including the whole and empty frame. No minimum-frame winner or average over frame sizes is used to replace the arrays. The generator retains joint compatibility: all future marginals come from one joint law. It does not make separate interventions or optimal responses jointly realizable.

## Copy fidelity versus extra prediction

Sensor, site 0 to site 1, lag 1. CTL conditions on all other sites' present.

| Drive | Held bits | Extra prediction bits | Flip response TV | Entropy production |
|---|---:|---:|---:|---:|
| 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 2 | 0.383956 | 0.188271 | 0.668588 | 0.169594 |
| 4 | 0.728526 | 0.117632 | 0.906525 | 0.448430 |
| 8 | 0.851157 | 0.013130 | 0.957340 | 0.955159 |

## Dependence on the physical cut

Same gated-relay generator and drive 4. Only the initial cut is conditioned on gate register 5 being off or on; it subsequently evolves normally and is not clamped. The gated link is 2 to 3 in the chain 0 to 1 to 2 to 3 to 4. The table shows source-0 flip response at site 4.

| Lag | Initially off | Initially on |
|---|---:|---:|
| 0 | 0.000000 | 0.000000 |
| 0.01 | 0.000000 | 0.000001 |
| 0.1 | 0.000038 | 0.006228 |
| 1 | 0.051822 | 0.696992 |
| 10 | 0.291615 | 0.421692 |
| 100 | 0.009988 | 0.009988 |

## Equilibrium and signed flow

Passive pair: entropy production 3.05e-31; activity 0.477767; site-0 to site-1 held information 0.469051 bits; flip response 0.196167.

Signed flow is explicitly the contribution of updates within F to dI(F:F-complement)/dt, in bits per unit time. Complementary terms cancel at stationarity. We do not sum magnitudes and call that the same quantity. Nonzero individual flows and their signs stay in the file.

## Scope of the result

The three readouts can disagree without the physical model becoming inconsistent. The complete lagged law retains the relations their summaries omit. Its restart identity K(s+t)=K(s)K(t) is checked, as are detailed balance, complementary signed flow and the exact perfect-copy conditional-information case. The response magnitude can be high for destructive propagation too; it has no ethical sign. Construction, fuel depletion, explicit bath records and a lushness extent remain further work.

The relay has only five links. Only those sites and listed lags are evaluated; no fitted longer propagation range or universal gas comparison is claimed. The all-frame arrays, rather than the selected tables above, are the experimental output.

## Reproduction and evidence

    .venv/Scripts/python.exe -m omega_v2.validation.local_flow_v0

[Profiles and model declarations](local_flow_v0/profiles.json) · [Generators and kernels](local_flow_v0/kernels.npz)

Stochastic-thermodynamic reference: [Horowitz and Esposito](https://arxiv.org/abs/1402.3276). The earlier [flow-note assessment](opus_flow_note_2026-10-03.md) explains the motivation.

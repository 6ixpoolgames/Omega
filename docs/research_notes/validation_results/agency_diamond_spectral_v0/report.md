# Agency Diamond Spectral Pilot v0

Status: PASS

## Claim Boundary

Finite deterministic spectral pilot only. The transfer operator is the nominal live-policy sub-Markov matrix restricted to declared viable states. These spectra are detector coordinates, not agency, identity, value, valuerhood, phase ontology, lushness, or Omega validation.

## Decision Gate

- own_maintenance_joint_effect_strictness_passes: PASS
- spectra_computed_for_all_systems: PASS
- driven_cycle_has_complex_phase: PASS
- driven_cycle_has_no_control: PASS
- self_restoring_has_reflexive_advantage: PASS
- self_restoring_has_no_complex_phase: PASS
- complex_phase_not_sufficient_for_deformer_profile: PASS
- reflexive_profile_not_dependent_on_complex_phase: PASS

## Strictness Witness

- status: PASS
- positive case joint effect: 1
- negative case joint effect: -1
- shared own live-maintenance score: 1

## Profiles

| system | family | spectral radius | complex modes | max | phase angles |
| --- | --- | ---: | ---: | ---: | --- |
| passive_attractor | passive | 1.0 | 0 | 0.0 | none |
| driven_cycle | driven | 1.0 | 2 | 0.866025403784 | 2.094395102393, -2.094395102393 |
| open_loop_controller | open_loop | 1.0 | 0 | 0.0 | none |
| thermostat | feedback | 1.0 | 0 | 0.0 | none |
| adaptive_controller | feedback | 1.0 | 0 | 0.0 | none |
| self_restoring_controller | reflexive | 1.0 | 0 | 0.0 | none |
| cooperative_controller | joint_positive | 1.0 | 0 | 0.0 | none |
| dominant_horizon_controller | joint_negative | 1.0 | 0 | 0.0 | none |

## Public Read

Nominal live-policy spectra are useful detector coordinates, but the first finite pilot demotes complex spectral phase: a driven cycle has complex phase without control, while the self-restoring controller has reflexive maintenance without complex phase.

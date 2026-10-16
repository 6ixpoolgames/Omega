# Coupling contrast with identical initial preparation

Follow-up to path_covering_report_v0.md. Metric, rates and frames are unchanged.
This time S and D are initially independent fair bits in both physical apparatuses.
Thus initial joint distribution, component entropies and correlations match.
No initial source record has already been installed at the destination.

The source is static. In the coupled generator D moves toward S at rate1 and
away from S at rate.1; in the disconnected generator D moves toward0 at rate1
and away from0 at rate.1. Both mechanisms are reversible conditional on S.
The full state permutation (S,D)->(S,D xor S) preserves path probabilities and
whole-state mismatch, and preserves the uniform initial law. It does not preserve
the physical destination frame. The event-count law is consequently identical.

| Frame | Equal cover coordinates | Total coordinates |
|---|---:|---:|
| source | 36 | 36 |
| destination | 25 | 36 |
| whole | 36 | 36 |

| T | I(S;D), coupled | I(S;D), disconnected |
|---:|---:|---:|
| 0.5 | 0.088237 | 0 |
| 1 | 0.227107 | 0 |
| 4 | 0.544035 | 0 |

The whole-frame tie persists with matched initial preparation. Local frames
retain some distinctions lost by whole-state mismatch. The metric is invariant
under a larger class of state-symbol bijections than the physical apparatus is.
This is a specific loss of structural information, not a demand that every
physically different apparatus have a different volume.

All coordinates are certified optima for the four-observation projected law,
using exhaustive covers or MILP. Full continuous-time covering is not inferred.
Runtime: 0.70 seconds.

Reproduce: `python -m omega_v2.validation.path_covering_coupling_check_v0`.

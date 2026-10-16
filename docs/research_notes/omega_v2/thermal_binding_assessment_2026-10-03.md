# What the first thermal/binding comparison says

3 October 2026. Interpretation of the [new run](thermal_binding_report_v0.md),
with its full laws, parameters, bills and profiles retained. This is an
exploratory assessment, not adoption of a new lushness measure.

## The matching bracket changes the previous crossing

At equal stored energy, the prebuilt source-to-destination response starts
above the unbuilt response and falls below it at the next sampled cut.
With equal usable fuel, or the explicit equal-free-energy mixture, the
prebuilt response stays above at all listed cuts for lag 1. The previous
crossing therefore depends on how resources are prepared; it is not a
general construction-versus-maintenance law. A different equal-free-energy
preparation could behave differently too.

This does not make the earlier mechanism fictitious. Converting fuel into
a link, or adding uncertainty over fuel stock, changes physical continuation.
The appropriate conclusion is to retain those distinctions in the comparison.

## Proximity accounts for most of one apparent assembly advantage

At mobility 0.1, cut 0 and lag 1, a native flip at the central site changes
the joint future law of the other four sites by the following mean
total-variation distances:

| Initial arrangement | Response |
|---|---:|
| Dispersed | 0.183674 |
| Contact, unbound | 0.425052 |
| Assembled | 0.427439 |

In this coordinate, bringing particles together supplies nearly all the
increase; bonding them adds little. The contact and dispersed preparations
match particle inventory, independent internal-bit content, stored energy,
fuel and thermodynamic free energy. The bonded preparation has the same
stored energy but lower free energy by ln 3. Position and bond state remain
actual physical differences, not changes of labels.

At mobility 1, the same comparison reverses:

| Initial arrangement | Response |
|---|---:|
| Dispersed | 0.554492 |
| Contact, unbound | 0.515054 |
| Assembled | 0.494692 |

The dispersed particles can carry and exchange disturbances through the
space. Bound groups also move, at the declared rate mobility/group size.
No extra exchange channel or speed bonus was reserved for the bound state.
This is a counterexample to requiring assembly to improve this response
coordinate in every regime, not a verdict on the overall lushness of gas.

## The full response profile is mixed

Even in the slow-motion example above, the selected response advantage is
not dominance across frames. At cut 0 the central native flip is the sole
reaction channel present in both the assembled and dispersed preparations.
Of the 64 declared frame responses at lag 1, assembled is greater in 24,
dispersed is greater in 38, and two tie within 1e-9. With faster motion the
counts are 12, 50 and two. These are counts of comparison coordinates,
not weights assigned to frames, and not votes for a winner.

At cut 1 all 35 reaction channels have positive event rates in both laws.
Both directions of inequality still occur. Rate profiles remain separate:
a large conditional response to a rare event is not the same as a frequent
event with that response. The [coordinate comparison evidence](thermal_binding_v0/comparison_summary.json)
can be regenerated without simulation:

    .venv/Scripts/python.exe -m omega_v2.validation.thermal_binding_analysis_v0

This is incomparability under the measured response coordinates only. It
does not establish incomparability under an unimplemented complete
realization relation or the intended encompassing lushness aggregation.

## Equilibrium still has consequential dynamics

In the original fuel apparatus, exact equilibrium has activity 0.429883,
source-to-destination response 0.001231 and incremental source prediction
0.051873 bits at lag 1, despite zero present I(S;D). In the mobile model,
the central-flip response at equilibrium is 0.371304 for slow motion and
0.537344 for fast motion. Neither stationarity nor detailed balance makes
the continuation inactive.

There is also information formation from initially independent signals:
in the original apparatus, unbuilt I(S;D) rises from zero to 0.279718 bits
by cut 1. The copying law is specified there, so this is a consequence of
that law, not independent discovery of a generative mechanism.

## Why the setup remains promising, and the gap it exposes

Assembly and dispersion are now preparations within one finite physical
law. The comparison permits thermal activity, transport, binding, reversal
and shared fuel to contribute without a required winner. It can distinguish
a geometry effect from a bond effect and an initial advantage from a later
one. Those are useful capabilities for testing candidate extents.

The new model mainly tests transport and persistence of contact. Its
assemblies do not catalyse a wider chemical repertoire; their distinct
composite operation is coherent group translation. It therefore does not
yet answer whether recursive construction creates additional subsequent
construction opportunities that compensate for constraints on motion.
That is a specific next physical mechanism to explore, not a reason to
award the current assemblies a missing generativity bonus.

Retain this run as a baseline that future mechanisms must actually change.
Do not remove the gas's mobile channels, quotient its noise, or tune the
readout to recover an assembly victory. The remaining mathematical work is
still to make an extent and its frame aggregation sensitive to the relevant
joint residual structure, and let that candidate fail if it is inadequate.

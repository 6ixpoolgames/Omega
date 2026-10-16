# Native bond failures in the reversible 2D substrate

2026-10-04.

Completed 384 source contexts, 24,576 residual trajectories and 2,255,578 events in 76.63 seconds with ten workers. The chemical generator is unchanged from the preceding pilot. No lushness score, new chemical rule or irreversible damage state was introduced.

[Protocol and sampling](lattice_damage_protocol_v0.md); [manifest](lattice_damage_v0/manifest.json); [complete compact results](lattice_damage_v0/summary.json). Each context's compressed archive includes the full physical trajectories, spatial marginal profiles, selected failure and initial states.

## What was compared

At t=5 of each prior trajectory, sample a thermal bond break in proportion to its native rate. Run 32 independent continuations with the event taken and 32 with it skipped, at lags 0,0.5,2,5. Both arms remain subject to all native reactions thereafter. Original-bond restoration, alternate connectivity, downstream construction and spatial laws are observed separately.

384/384 contexts had a nonzero thermal failure rate. Zero-hazard contexts are retained in the source population. Event-conditioned averages weight source states by their total failure hazard once; the sampled edge was already selected conditionally by its relative hazard.

The pooled rows below describe this equal-configuration experimental mixture, not a prior over possible worlds. Bridge and template strata differ in other physical properties and are not matched interventions on topology alone. Individual configuration summaries remain available.

## What this run resolves

The recovery notions separate: by lag5 the original bond was restored at least once with probability 0.455, present with probability 0.397, and its endpoints connected by some path with probability 0.574 (versus 0.866 in the skipped arm). The first two differ because restored bonds can fail again; alternate paths explain some connection without the original bond.

For sampled bridge failures, other-bond stock has a small positive mean shift (+0.145; conditional simulation SE 0.048) while endpoint connection falls by 0.375. That combination matters: extra bonds elsewhere need not restore the lost relation. Splitting a rigid component can change mobility and encounters, but this run has not isolated that as the cause of the positive shift.

Near-field distribution changes are clear. Far-field changes are small and mostly comparable to sampling uncertainty; this run does not establish a persistent long-range effect.

Only five selected failures removed a currently working catalytic template. Enumerating the source cuts finds such failures available in 60/384 contexts, carrying 0.893% of total native thermal failure flux in the empirical configuration mixture. The native panel therefore under-samples that rare question. The template row is suggestive only, not a general catalytic-bottleneck result. A template can also acquire a new target later; 'no current target' does not mean permanently non-catalytic.

## Recovery is not one event

Broken arm, lag5. Probabilities are conditional on the sampled native failure.

| Failure role | Source contexts | Original bond ever restored | Original bond present | Restored then lost at least once | Endpoints connected now | Alternate path now |
|---|---:|---:|---:|---:|---:|---:|
| All | 384 | 0.455 | 0.397 | 0.083 | 0.574 | 0.386 |
| Bridge | 283 | 0.341 | 0.293 | 0.061 | 0.462 | 0.257 |
| Initially alternate path | 101 | 0.755 | 0.670 | 0.141 | 0.867 | 0.723 |
| Currently assists another formation | 5 | 0.332 | 0.281 | 0.069 | 0.405 | 0.308 |
| No current target | 379 | 0.457 | 0.399 | 0.083 | 0.576 | 0.387 |

An alternate bond path can exist while the original bond is missing; it does not guarantee the same catalytic function. First restoration also does not guarantee continued restoration. No permanence statement follows from a finite observation horizon.

## Changes outside the original bond

Lag5 means, broken minus skipped. Negative values indicate a lower quantity in the broken arm, not a general ethical sign.

| Role | Other bonds | Remaining fuel | Other catalytic formations by lag5 | Other catalytic formation hazard at lag5 |
|---|---:|---:|---:|---:|
| All | +0.0745 | -0.2542 | -0.0289 | -0.0133 |
| Bridge | +0.1450 | -0.2430 | -0.0251 | -0.0064 |
| Initially alternate path | -0.1097 | -0.2836 | -0.0390 | -0.0314 |
| Currently assists another formation | +0.4383 | -0.2063 | -0.5957 | -0.0829 |
| No current target | +0.0707 | -0.2547 | -0.0229 | -0.0126 |

These are effects of taking a native failure at a given sampled cut. The counterfactual skipped arm can subsequently lose the same bond. A higher count after failure can reflect greater mobility, new encounters or recycling; it is not by itself improved continuation extent.

## Spatial response and sampling noise

Every cell records empty/concealed/exposed probabilities, and every neighboring edge records a physical bond probability. The table reports a noise-corrected squared difference of mean features per observed cell or edge in the farther region (distance >=2 from the initial break sites). The subtraction removes finite-sample inflation in expectation. Negative estimates remain visible. They mean estimator fluctuation, not negative influence.

The sham compares two independent halves of the skipped arm. Its expectation is zero, but its smaller sample count makes it noisier. Approximate SE below describes variation across sampled contexts; it is not an exact confidence interval for the entire field.

| Lag | Far-cell response ± context SE | Far-cell sham | Far-edge response ± context SE | Far-edge sham |
|---:|---:|---:|---:|---:|
| 0 | +0.000000 ± 0.000000 | +0.000000 | +0.000000 ± 0.000000 | +0.000000 |
| 0.5 | +0.000447 ± 0.000177 | +0.000064 | +0.000057 ± 0.000048 | +0.000060 |
| 2 | +0.000532 ± 0.000279 | -0.000377 | +0.000117 ± 0.000081 | -0.000118 |
| 5 | +0.000289 ± 0.000281 | -0.000884 | +0.000013 ± 0.000082 | -0.000153 |

These marginal projections do not determine the joint continuation law. Original-bond/alternate-path joint probabilities and all raw trajectories are retained alongside them. The fixed spatial coordinates define an observational probe, not a free physically installed decoder.

Far response is relative to the model: rigid-cluster mobility can change immediately throughout a component when a bridge breaks, and fuel is well mixed. These are existing coarse assumptions. The response is not a measured physical signal speed or evidence that influence crossed a newly discovered channel.

## Regime-resolved means

Each row uses 12 source histories and 32 continuations per arm. Full conditional Monte Carlo errors are in the JSON; uncertainty in the source histories and the sampled failure edge is additional.

| N | Density | Strength | b | Start | P(original restored by5) | P(original present at5) | Delta other bonds | Delta other catalytic formations |
|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 16 | 0.250 | 1 | 0 | dispersed | 0.322 | 0.274 | +0.098 | +0.000 |
| 16 | 0.250 | 1 | 0 | seeded | 0.300 | 0.253 | +0.180 | +0.000 |
| 16 | 0.250 | 1 | 2 | dispersed | 0.375 | 0.300 | +0.047 | -0.127 |
| 16 | 0.250 | 1 | 2 | seeded | 0.459 | 0.389 | +0.056 | -0.189 |
| 16 | 0.250 | 3 | 0 | dispersed | 0.437 | 0.404 | -0.110 | +0.000 |
| 16 | 0.250 | 3 | 0 | seeded | 0.469 | 0.442 | +0.137 | +0.000 |
| 16 | 0.250 | 3 | 2 | dispersed | 0.486 | 0.444 | +0.019 | -0.064 |
| 16 | 0.250 | 3 | 2 | seeded | 0.675 | 0.630 | -0.102 | -0.131 |
| 36 | 0.250 | 1 | 0 | dispersed | 0.437 | 0.360 | +0.628 | +0.000 |
| 36 | 0.250 | 1 | 0 | seeded | 0.313 | 0.265 | +0.279 | +0.000 |
| 36 | 0.250 | 1 | 2 | dispersed | 0.348 | 0.295 | +0.082 | -0.072 |
| 36 | 0.250 | 1 | 2 | seeded | 0.401 | 0.334 | +0.284 | -0.184 |
| 36 | 0.250 | 3 | 0 | dispersed | 0.479 | 0.436 | +0.147 | +0.000 |
| 36 | 0.250 | 3 | 0 | seeded | 0.379 | 0.368 | +0.124 | +0.000 |
| 36 | 0.250 | 3 | 2 | dispersed | 0.615 | 0.598 | +0.110 | +0.006 |
| 36 | 0.250 | 3 | 2 | seeded | 0.477 | 0.447 | -0.131 | +0.080 |
| 16 | 0.444 | 1 | 0 | dispersed | 0.431 | 0.358 | +0.303 | +0.000 |
| 16 | 0.444 | 1 | 0 | seeded | 0.504 | 0.408 | +0.118 | +0.000 |
| 16 | 0.444 | 1 | 2 | dispersed | 0.361 | 0.317 | +0.068 | +0.189 |
| 16 | 0.444 | 1 | 2 | seeded | 0.368 | 0.297 | +0.019 | -0.060 |
| 16 | 0.444 | 3 | 0 | dispersed | 0.552 | 0.520 | +0.116 | +0.000 |
| 16 | 0.444 | 3 | 0 | seeded | 0.477 | 0.433 | +0.294 | +0.000 |
| 16 | 0.444 | 3 | 2 | dispersed | 0.630 | 0.589 | +0.078 | -0.020 |
| 16 | 0.444 | 3 | 2 | seeded | 0.654 | 0.616 | +0.126 | -0.100 |
| 36 | 0.444 | 1 | 0 | dispersed | 0.372 | 0.317 | +0.125 | +0.000 |
| 36 | 0.444 | 1 | 0 | seeded | 0.450 | 0.386 | -0.112 | +0.000 |
| 36 | 0.444 | 1 | 2 | dispersed | 0.453 | 0.373 | -0.079 | -0.030 |
| 36 | 0.444 | 1 | 2 | seeded | 0.500 | 0.408 | -0.327 | -0.134 |
| 36 | 0.444 | 3 | 0 | dispersed | 0.431 | 0.403 | -0.102 | +0.000 |
| 36 | 0.444 | 3 | 0 | seeded | 0.604 | 0.559 | -0.054 | +0.000 |
| 36 | 0.444 | 3 | 2 | dispersed | 0.753 | 0.708 | +0.024 | -0.041 |
| 36 | 0.444 | 3 | 2 | seeded | 0.724 | 0.675 | +0.180 | +0.106 |

## Scope and checks

Ten focused tests across the physical model and failure observer pass, including first-hit versus occupancy, thermal energy/fuel accounting, alternate connectivity, zero native hazard, exact unbiasedness of the squared-response estimator and the preceding reversibility/symmetry checks. Lint passes. The new reader does not change the physical generator.

All failures are reversible in this model. Fuel exhaustion is not absorbing. A native thermal break takes energy from the implicit bath, with no free fuel refund. The results concern bounded recovery and residual physical effects, not permanent destruction, universal robustness or an ethical ordering. A meaningful next refinement should follow an identified mechanism or missing resolution rather than a preferred sign.

## Next targeted sample

The cheapest informative continuation is a separately labeled panel conditioned on currently working-template failures, using the 60 eligible source contexts and their native rates. Keep its actual rarity alongside the conditional result. This changes sampling, not chemistry, and avoids adding mechanisms merely to make bottlenecks easier to observe. That targeted panel has not been run here.

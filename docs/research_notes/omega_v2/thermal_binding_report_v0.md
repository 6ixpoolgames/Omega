# Thermal baseline and mobile binding — exploratory run v0

3 October 2026. One existing fuel/coupling law and two mobility settings of a common 800-state particle model. Exact finite matrix dynamics; no fitted score, noise removal or required gas/structure winner.

## Existing apparatus: equilibrium and matching brackets

The earlier B=4, assembly=1, damage=0.05 apparatus now runs from its equilibrium law as well as correlated and independently prepared signals. All 32 frames, seven reactions and both response lags (1,5) are retained at cuts 0,1,5,20,100. Incremental prediction is I(X_i;X_rest(future)|X_rest(present)); it is well defined for joint fuel/register jumps, but is not a guarantee of physical control.

Stationarity concerns the distribution, not an absence of events. Equilibrium retains activity and lagged response. This remains an open system with an implicit constant-temperature bath, not a closed-universe experiment. The fixed apparatus is not relabelled as a gas.

The equal-free-energy preparation mixes prebuilt states with three and four fuel packets until D(p||π) equals that of the unbuilt four-packet preparation. It is one explicit match, not a unique matching rule. Its extra preparation uncertainty and energy remain in the law. Equal usable fuel instead compares prebuilt and unbuilt states both carrying three packets.

Prebuilt four-packet probability in the free-energy match: 0.38072814.

| Matching condition | Cut | Unbuilt response | Prebuilt response | Prebuilt − unbuilt |
|---|---:|---:|---:|---:|
| stored energy | 0 | 0.576549 | 0.632233 | +0.055684 |
| stored energy | 1 | 0.511659 | 0.490969 | -0.020690 |
| stored energy | 5 | 0.171888 | 0.164445 | -0.007442 |
| usable fuel | 0 | 0.271182 | 0.632233 | +0.361052 |
| usable fuel | 1 | 0.243628 | 0.490969 | +0.247341 |
| usable fuel | 5 | 0.076364 | 0.164445 | +0.088081 |
| free energy | 0 | 0.576549 | 0.695919 | +0.119370 |
| free energy | 1 | 0.511659 | 0.566467 | +0.054808 |
| free energy | 5 | 0.171888 | 0.211802 | +0.039915 |

The table uses the native source-flip response at D at lag 1. A crossing changing under a matching rule identifies sensitivity to that physical preparation; it does not divide real mechanisms from mere accounting.

| Preparation | Cut | Present I(S;D), bits | Response | Incremental prediction, bits | Activity |
|---|---:|---:|---:|---:|---:|
| equilibrium | 0 | 0.000000 | 0.001231 | 0.051873 | 0.429883 |
| equilibrium | 1 | 0.000000 | 0.001231 | 0.051873 | 0.429883 |
| equilibrium | 20 | 0.000000 | 0.001231 | 0.051873 | 0.429883 |
| unbuilt_correlated | 0 | 1.000000 | 0.576549 | 0.000000 | 4.146767 |
| unbuilt_correlated | 1 | 0.609330 | 0.511659 | 0.077271 | 2.623857 |
| unbuilt_correlated | 20 | 0.000337 | 0.005034 | 0.087669 | 0.750829 |
| unbuilt_independent | 0 | 0.000000 | 0.627680 | 0.687777 | 7.841295 |
| unbuilt_independent | 1 | 0.279718 | 0.290001 | 0.107200 | 3.081854 |
| unbuilt_independent | 20 | 0.000078 | 0.003550 | 0.080216 | 0.658966 |

Randomizing the initial three signals lowers their correlation resource while preserving their individual fair marginals, geometry and fuel. Its free-energy cost is visible: the independently prepared unbuilt state has 2 ln 2 less D(p||π) than the correlated state. This is a separate physical preparation, not a free quotient of differences.

## One common mobile substrate

Three identical particles occupy five sites on a reflecting line. Each carries a binary internal state; empty/0/1 are the local site observations. There are no source, receiver or organism roles in the rules. Adjacent occupied sites exchange unequal internal states at rate 1, whether bonded or unbound. Native internal flips have rate 0.05. These collisions remain available to the dispersed preparation.

Each adjacent pair may form or lose a bond. With μ=4, E=μ(F+number of bonds), and B=3 fuel/spent packets, the equilibrium weights are binomial(B,F) exp(−E). Thermal formation/breakdown rates are 0.02 exp(∓μ/2). Fuel-assisted formation consumes a packet at rate 0.25 F; reverse disassembly restores one at rate 0.25(B−F). The fuel pool is explicitly well mixed rather than spatially resolved.

Every unbound particle or bonded connected component can translate one site into available space. A component of n particles has translation rate mobility/n in each allowed direction. Internal states and bonds move with it. This coarse motion rule and reflecting boundaries are declared assumptions, not derived molecular dynamics. Both mobility values, 0.1 and 1, use identical laws for all preparations. No bound-specific exchange-speed bonus is included.

Four initial preparations are used:

- Dispersed: occupied sites {0,2,4}, no bonds, three fuel packets.
- Contact, unbound: occupied sites {1,2,3}, no bonds, three fuel packets.
- Assembled: occupied sites {1,2,3}, both internal bonds, one fuel packet.
- Equilibrium: the actual stationary distribution over the same states.

The first three all have independent fair internal bits, three particles and stored energy 12. Contact versus dispersed also matches free energy exactly. The assembled preparation has ln 3 less D(p||π), due to the fuel-inventory degeneracy; this unmatched resource remains explicit. Geometry and bonds subsequently evolve normally. Initial positions are physical preparations, not labels erased by averaging.

Each of the 32 site subsets is observed with and without the shared fuel pool, giving 64 declared frames. A frame sees internal bonds whose two endpoints it contains. Boundary-crossing-bond and edge-only readers are not included; this is not the set of all physically possible frames. The full frame identifies every represented state. Present source axes comprise all five site variables, four bond bits and fuel, not a designated beneficiary.

## Mobile comparison

Illustration: a native flip at site 2, observed in the joint frame of the other four sites at lag 1. Response is conditional on that flip occurring; its actual rate is retained. Present site information includes occupancy as well as internal state. Full profiles, including all joint frames and reaction types, remain in the evidence.

| Mobility | Preparation | Cut | Mean bonds | Mean fuel | Response | Flip rate | Incremental prediction at site 2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.1 | dispersed | 0 | 0.000000 | 3.000000 | 0.183674 | 0.050000 | 0.120922 |
| 0.1 | contact_unbound | 0 | 0.000000 | 3.000000 | 0.425052 | 0.050000 | 0.228535 |
| 0.1 | assembled | 0 | 2.000000 | 1.000000 | 0.427439 | 0.050000 | 0.231671 |
| 0.1 | equilibrium | 0 | 0.021701 | 0.053959 | 0.371304 | 0.030074 | 0.112631 |
| 0.1 | dispersed | 1 | 0.091063 | 2.904229 | 0.227233 | 0.041768 | 0.113163 |
| 0.1 | contact_unbound | 1 | 0.766716 | 2.166212 | 0.426690 | 0.048886 | 0.222552 |
| 0.1 | assembled | 1 | 1.255828 | 1.515502 | 0.426428 | 0.049164 | 0.225224 |
| 0.1 | equilibrium | 1 | 0.021701 | 0.053959 | 0.371304 | 0.030074 | 0.112631 |
| 0.1 | dispersed | 20 | 0.436894 | 1.230234 | 0.384824 | 0.030717 | 0.117925 |
| 0.1 | contact_unbound | 20 | 0.357766 | 0.964428 | 0.388590 | 0.033836 | 0.131936 |
| 0.1 | assembled | 20 | 0.326933 | 0.882473 | 0.387774 | 0.033832 | 0.131700 |
| 0.1 | equilibrium | 20 | 0.021701 | 0.053959 | 0.371304 | 0.030074 | 0.112631 |
| 1.0 | dispersed | 0 | 0.000000 | 3.000000 | 0.554492 | 0.050000 | 0.355980 |
| 1.0 | contact_unbound | 0 | 0.000000 | 3.000000 | 0.515054 | 0.050000 | 0.299512 |
| 1.0 | assembled | 0 | 2.000000 | 1.000000 | 0.494692 | 0.050000 | 0.275731 |
| 1.0 | equilibrium | 0 | 0.021701 | 0.053959 | 0.537344 | 0.030074 | 0.194932 |
| 1.0 | dispersed | 1 | 0.376785 | 2.599279 | 0.530996 | 0.027749 | 0.174426 |
| 1.0 | contact_unbound | 1 | 0.617666 | 2.325515 | 0.523553 | 0.038119 | 0.231602 |
| 1.0 | assembled | 1 | 1.224379 | 1.548271 | 0.501544 | 0.044193 | 0.249478 |
| 1.0 | equilibrium | 1 | 0.021701 | 0.053959 | 0.537344 | 0.030074 | 0.194932 |
| 1.0 | dispersed | 20 | 0.389164 | 1.022550 | 0.526346 | 0.031708 | 0.196659 |
| 1.0 | contact_unbound | 20 | 0.378561 | 0.996965 | 0.526742 | 0.031651 | 0.196598 |
| 1.0 | assembled | 20 | 0.343546 | 0.911725 | 0.528028 | 0.031465 | 0.196403 |
| 1.0 | equilibrium | 20 | 0.021701 | 0.053959 | 0.537344 | 0.030074 | 0.194932 |

## Scope and evidence

This is a bounded reactive lattice-gas comparison, not an empirical verdict on molecular gas or open-ended generativity. Assembly creates mobile composites within a fixed primitive law; the full law already predicts their possible formation. Native noise, collisions, reverse reactions and the thermal tail all remain. A high response can transmit destructive consequences as well as constructive ones, so the profile carries no assigned ethical sign.

All comparisons concern the retained finite-time laws. A common equilibrium does not erase transient differences, and equilibrium can retain conditional dynamics. These runs do not assert that lushness must vanish at equilibrium, that gas must lose, or that a successful response metric alone completes lushness.

Runtime: 22.40 seconds with one numerical worker. Maximum detailed-balance residual: 3.47e-18. Maximum fuel-balance residual: 1.95e-14. Maximum mobile bond-balance residual: 7.11e-15.

    .venv/Scripts/python.exe -m omega_v2.validation.thermal_binding_v0

[All profiles, laws and parameters](thermal_binding_v0/profiles.json) · [Thermal kernels](thermal_binding_v0/thermal_kernels.npz) · [Slow-motion kernels](thermal_binding_v0/mobile_0.1_kernels.npz) · [Fast-motion kernels](thermal_binding_v0/mobile_1.0_kernels.npz)

[Preceding fuel/coupling run](fuel_flow_report_v0.md)

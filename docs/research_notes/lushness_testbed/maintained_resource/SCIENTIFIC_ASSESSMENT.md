# Maintained locked-resource comparison

The comparison completed from the frozen v1 protocol after six focused tests
and a hard-capped engineering smoke passed. It used the full 16-state physical
count state, including resource, apparatus/precursor, and charged/spent carrier.
There was one recurrent class of 16 states in both the capable and paid-path
ablated laws. The organized and unorganized roots have equal energy (2.5) and
share one generator in the capable law.

At the primary cadence 0.25, the complete finite-history entropy profiles were:

| Horizon | Capable, organized | Capable, unorganized | Paid path ablated, matched | Capable minus ablated |
|---:|---:|---:|---:|---:|
| 1 | 0.587806 | 0.323325 | 0.569733 | 0.018074 |
| 4 | 2.455656 | 1.331469 | 2.180775 | 0.274881 |
| 16 | 10.497313 | 5.914053 | 7.576007 | 2.921306 |
| 64 | 39.960528 | 29.109022 | 23.800621 | 16.159906 |

The same-law organized-root and unorganized-root stationary entropy rates are
identical at each cadence: 0.622120, 0.554748, and 0.486442 bits/time at
cadences 0.125, 0.25, and 0.5. Their finite profiles differ because their roots
differ. The separate between-law capable-minus-ablated stationary rate
differences are +0.260024, +0.228729, and +0.196984 bits/time at those
cadences. The preregistered sign criterion therefore passes at all three
cadences. Rates are secondary to the finite-horizon profiles.

The paid route was used (stationary event flux 0.007729/time); downstream-use
flux was 0.025331/time in the capable law versus 0.007475/time in the ablation.
However, the apparatus was functioning only 0.7643 of the time in the capable
law versus 0.8696 in the ablation, while maintenance-channel activity was
0.006149 versus 0.003403/time. At T=64, downstream-use first passage from the
organized capable root was 0.5144, from the same-law unorganized root 0.2083,
and from the matched ablation root 0.0812.

The boundary prescriptions matched, but accepted throughput and work did not.
Accepted resource inflow was 0.005809/time in the capable law and 0.006166 in
the ablation; accepted charged-carrier recharge was 0.009429 versus 0.005217.
Net boundary work input was 0.010832 versus 0.000338 energy/time, with equal
stationary bath-heat flow by the first-law ledger. The result therefore includes
a larger accepted external energy input in the capable law. These differences
are measured consequences of state occupancy under the common ideal boundary,
not equal-input comparisons. The signed net stored-carrier depletion flow,
combining paid access and reversible maintenance channels, was 0.009687 versus
approximately zero energy/time; it should not be read as gross forward fuel
spend because reverse transitions restore the carrier.

This is a bounded access/throughput mechanism toy. The downstream resource
reaction does not generate apparatus precursor or charged carrier, so increased
resource use does not sustain the enabler. Lower apparatus availability in the
capable law reinforces that limitation. The result does not show positive
feedback, autonomous maintenance, open-ended compounding, or established
chemistry. Coupling resource use to apparatus/precursor or carrier regeneration
remains a distinct future model question; it was not retrofitted after seeing
these outcomes.

The exact frozen output, including all profiles, fluxes, costs, and hashes, is
under `results/local_runs/lushness_testbed/maintained_resource/science-20261013T181133Z-4a5788/`.
Its PROFILE records a 0.632 s runtime, 115,679,232-byte peak job memory, 121,604
output bytes, and no cap hit (120 s, 1 GiB, 256 MiB caps). Frozen input hash:
`33241eddb839ea0a652a13879543aa31e7265c0f4d56613d91fdfb876484af1e`.

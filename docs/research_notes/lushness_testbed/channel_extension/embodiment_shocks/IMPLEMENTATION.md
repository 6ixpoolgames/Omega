# Embodied actuation and matched shocks: implemented contracts

2026-10-13. This amendment supersedes the zero-basal primary prescription in
EMBODIMENT_AND_SHOCKS_SPEC_r1.md. The zero-basal law remains a sensitivity case.
The prospective batch is defined by PREREGISTRATION.json and its hashed case files.

## Physical modules

ActuationSpec has independent `mode` and `basal_rate` fields. Default legacy/zero
exactly recovers previous kernels. Embodied commanded switches multiply both
directions by a/M, retaining native fuel/heat stoichiometry. A separate symmetric
gate-relaxation module flips a gate at basal_rate without policy instructions,
fuel consumption or energy change. Gate energy is zero in this adapter. Basal
relaxation occurs in the matched legacy control too. This is a declared thermal
gate model, not an assertion that every actuator has this law.

Positive basal relaxation permits a common post-collapse residual class. It does
not keep a ghost controller acting: commanded rates vanish at zero active apparatus.
At zero basal rate gates retain their physical settings, allowing residual classes
to differ. Both outcomes are computed, not imposed by the comparison algorithm.
Separate sensing cycles, controller memory and individual lineages remain open.

ShockSpec declares enabled/mode/hazard/p. Independent shocks damage one unit at
a time. Correlated shocks share ONE Poisson arrival across both compartments,
with binomial pre-event selection of A and W units; ν=h/p. Selected A become W,
selected W become D, and no selected A advances twice in the same event. Both arms
match conditional damage and energy first moments. Unchanged outcomes create no
state transition or additional entropy label.

Shock work is its signed state energy change; ordinary bath heat for this external
channel is zero. `shock_energy_transfer` retains the boundary ledger. The generic
compiler `drive_work` includes all external work; report `chemical_drive_work =
drive_work - shock_energy_transfer` separately. This convention represents external
disturbance energy export/input, not a thermal detailed-balance channel.

## Readouts and computation

The full physical generator feeds exact propagation and the native sampler.
Readouts include shock event/hit flux, pre-active function loss, closure flux,
stationary exposure, first recovery and retained function. Independent arrivals
use flux-weighted event statistics; correlated arrivals include the omitted
identity outcome when reporting per-clock risk. Reserve comparisons use a common
hypothetical p=.5 damage probe under each winning state distribution. This probe
does not add physical events to the scoring law. No entropy-family share is claimed.

Thirty-six tables are retained. Cache aliases require exact equality of sparse
Q and all flow ledgers; an equal Q alone is insufficient for identical mechanism
readouts. Embodied inactive instructions are inoperative, leaving six unique
models in this search class. Alias rows retain their tables and reference model.
No aliases are counted as independent physical alternatives.

All-trapped diagnostic roots have empty fuel and energy -4 in this batch, unlike
the matched E8 preparation roots. Their breadth/recovery differences are conditional
mechanism queries, not free executable removal or restoration interventions.

## Engineering evidence and scope

Smoke run `channel-smoke-worn_reversible-20261013T145239Z-129e0d` completed in
0.979s at112.48MiB under120s/1GiB/256MiB. Hash:
`aa6bdefa3dd0d5a6826f811333cb38eee80ebfa2246f79eb2a68dccd98bb1617`.

Fixed-controller3+1 preflight
`channel-preflight-worn_reversible-20261013T145312Z-2d483c` completed in9.979s
at482.90MiB under600s/1GiB/256MiB. Hash:
`b049b1b52f1d7952dad4028185172a2d6300632a58fe9e082164ec1f6e737e89`.
Build .64s, exact analysis5.17s, full legacy query surveys2.94s; estimated36-table
runtime315.14s before alias reduction. Later stationary/deadline shock readouts
add small query overhead and were validated in tiny integration tests before launch.

Focused checks include legacy invariance, symmetric embodied switch ratios,
policy-independent post-collapse basal dynamics, cross-compartment shock events,
matched first moments, material/energy accounting, finite independent limit,
shock arrival weighting, exact/sampled endpoint agreement, and exact alias reuse.
The focused suite has66 passing tests after the sampler and alias regression checks.
This is not a repository-wide green claim.

Source/config and artifacts are hashed, execution uses copied source under caps,
and reports retain all failed predictions. Raw states/class vectors stay ignored.
Source/config/report publication remains separate; no push or cleanup is automatic.

## Future modules

The same module-plus-ledger-plus-readout contract supports independent controller
memory/sensing, external-drive failure, capacity growth, physical spatial baselines
and criticality surveys. Their disabled modes must reproduce the preceding law;
each needs engineering feasibility and a separately frozen scientific comparison.
This upgrade does not establish valuerhood, criticality or open-ended generativity.

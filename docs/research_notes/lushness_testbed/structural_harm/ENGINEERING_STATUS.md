# Structural harm engineering gate

The new repair-hardware module is implemented as a separate adapter over the
existing growth modules. Legacy growth kernels remain untouched. Five focused
tests verify matched immediate fault impairment/hazard, paired repair slowdown,
irreversible hardware loss with retained basal recovery, mass/energy accounting,
parameter validation and refusal to truncate at a state cap. Combined hardware,
maintained-resource and reserve-controller checks: 25 passed. New files pass Ruff.

The locked-resource regression now checks exact equality of every non-paid-path
event in capable and ablated laws, including basal thermal resource dynamics.

Frozen-source smoke `smoke-20261013T204651Z-d304a5` completed in 2.158 seconds,
peaking at 139,251,712 bytes (132.80 MiB), under hard caps of 120 seconds,
1 GiB and 32 MiB output. All three 1+1 consequence arms (576 states each)
passed generator, transition, propagated mass and energy checks. The same smoke
also compiled and sparsely propagated the proposed 3+1 hardware-loss world
(3,840 states). No optimization rankings were inspected.

Input hash: `a1c4c0e2b8cf5051c787491323d3d8a4983b06316428a7b01026a93393c8b625`.
Compact results and profile remain under
`results/local_runs/lushness_testbed/structural_harm/smoke-20261013T204651Z-d304a5/`.
The earlier small-only smoke is retained as engineering provenance.

A 3+1 dense kernel alone is 117,964,800 bytes; matrix-exponential workspace and
other arrays require additional memory. Sparse propagation success does not
certify the full entropy solver fits. The next execution gate is a single capped
fixed-policy exact-entropy feasibility job, followed by freezing candidate policies,
roots, executable predictions and the scientific batch budget. The draft protocol
is not a completed scientific preregistration or a result about reserve behavior.

Follow-up: all twelve scientific cases completed. See [scientific assessment](SCIENTIFIC_ASSESSMENT.md) and [automated results](report/RESULTS.md).

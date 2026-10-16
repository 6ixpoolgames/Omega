# Interaction-selected histories: exact probe results

2026-10-08. Full authorized panel completed on the existing finite quantum
testbed. Protocol: interaction_selected_history_protocol_v0.md. Code:
omega_v2/finite/interaction_selected_history.py; runner:
python -m omega_v2.validation.interaction_selected_history_v0.

## Finding

Physical interaction structure can identify a useful record axis in a simple
nondemolition regime. It does not guarantee a unique classical history family
for general competing dynamics. The full history decoherence object obeys
reconstruction and representation controls. Spectral extent remains conditional
on the history family, even after a physically natural family has been found.

This is progress on deriving readout structure from physics, not derivation of
canonical coherent extent. No gas comparison or value/generativity ranking.

## Law and identification criterion

The finite world is S plus m explicit environment qubits. Use the standard
controlled-rotation interaction H=g A_S sum_j Y_Ej, A=n.sigma, with hbar=1 and
pulse duration1. Each coupling acts on S and one E. The local tensor structure,
interaction and preparation are declared physical adapter assumptions. No
projection collapse is inserted into evolution.

The program solves [a.sigma tensor I,H]=0 as a real linear nullspace problem.
Sequential cases require conservation under each actual pulse generator;
simultaneous cases use the summed generator. This identifies conserved local
observables, a sufficient nondemolition criterion. It is not a theorem that all
pointer states are exact conserved observables, and dimension0 does not exclude
approximate or time-dependent preferred records.

- All 36 nonzero-coupling single-axis cases select a one-dimensional axis,
  aligned with the actual coupling (up to outcome-sign exchange).
- All 9 zero-coupling cases have dimension3: every local axis is conserved,
  so none is uniquely selected. The analytical history axis in these controls
  is explicitly not claimed to have been selected by zero dynamics.
- Parallel interactions with two environmental registers retain dimension1.
- For all 9 tested nonzero X/Z competition cases the common local dimension
  is0. For the three zero-competitor controls it is1.
- Consistent coordinate rotation/register renaming leaves physical answers
  invariant. Rotating the physical coupling from Z to X while holding S=0 and
  the output Z reader fixed changes output breadth1->2, correctly distinguishing
  physical reorientation from coordinate relabeling.

## Recording, redundancy, and revival

S starts as a balanced superposition of A eigenstates; environments start0.
Conditional environment states have overlap c=cos(2g)^m. The program obtains
this from full unitary evolution and checks it analytically. Source coherence
relative to its initial off-diagonal value is |c|. Environmental trace distance
between the two conditional states is sqrt(1-|c|^2), reported as an ideal
distinguishability diagnostic, not an extra score or a physically simulated
optimal apparatus. No decoherence threshold deletes a difference.

After coupling, a specified signal recombiner/readout has probabilities
((1+c)/2,(1-c)/2). This readout is declared, not claimed uniquely determined
by the conserved interaction observable. D resolves A after coupling and this
final signal output; all environmental degrees remain in its branch vectors.

| Copies m, g=pi/8 | Relative source coherence | Environmental trace distance | Spectral history breadth | Signal output breadth |
|---:|---:|---:|---:|---:|
| 1 | .707107 | .707107 | 3.033274 | 1.516637 |
| 2 | .500000 | .866025 | 3.509531 | 1.754765 |
| 3 | .353553 | .935414 | 3.752501 | 1.876250 |

At g=pi/4 the record states are orthogonal, trace distance1, signal breadth2,
and spectral history breadth4 for all copy counts. At g=pi/2, the conditional
environmental states differ only by phase, source coherence returns to1,
trace distance0, signal breadth1 and spectral history breadth2. This is a
finite unitary revival, not irreversible decoherence. The conserved axis remains
identified: an identifiable axis alone does not prove a record currently exists.

Three physical axis orientations, five actions, and three copy counts give45
aligned profiles. Angular covariance was checked without selecting a favorable
coordinate representation. Diagonal fine-history breadth remains4 throughout
this family, including the no-interaction control.

## Competing interactions

H_Z=(pi/8) Z_S Y_EZ and H_X=r(pi/8) X_S Y_EX with r=0,.25,1,4. Initial S=+,
E_Z=E_X=0. Run sequential ZX, sequential XZ and simultaneous H_Z+H_X.
Sequential pulses last1 each (total2); the simultaneous case lasts1 with both
terms active. These are different physical timing protocols, not a fair winner
comparison at matched duration. The integrated action of each term is the same.

Example r=1:

| Physical law | Common conserved-axis dimension | Actual Z-output breadth | Actual X-output breadth | ZZ-history spectrum breadth | XX-history spectrum breadth |
|---|---:|---:|---:|---:|---:|
| Sequential ZX | 0 | 2 | 1.516637 | 3.033274 | 1.516637 |
| Sequential XZ | 0 | 2 | 1.516637 | 2 | 1.516637 |
| Simultaneous | 0 | 2 | 1.496512 | 2.347376 | 1.314574 |

ZZ/XX mean mathematical histories resolving that observable at the two declared
cuts. They are diagnostics, not physical extra measurements. Their interference
is retained and their final output laws agree with the untouched unitary process.
The paired profiles are not summed or selected by highest score.

There is no single exactly conserved local source axis in these competing
cases. This does not show there is no physically meaningful noncommutative
observable algebra, adaptive history family, or approximate pointer regime.

## Representation, refinement and composition

At g=pi/8,m=1,axis angle.37:

| History description of unchanged physical process | Spectral breadth | Signal output breadth |
|---|---:|---:|
| Original native-axis history family | 3.033274 | 1.516637 |
| Additional native-axis checkpoint | 3.033274 | 1.516637 |
| Additional orthogonal-axis checkpoint, no physical measurement | 2.598788 | 1.516637 |

For BOTH refinements, summing the finer D blocks recovers the original D to
<1.4e-16. The latter scalar change is a finer analytical question, not an actual
physical contraction. An intrinsic extent cannot silently count it as one.
Repeated refinement within the conserved native-axis family passed here; this
supports an operationally restricted profile, not unrestricted invariance.

Passed controls: consistent unitary description changes, register permutation
and axis tracking, time-step subdivision with fixed physical cuts, identity
checkpoint, inert blank ancilla, coherent coarsening, independent product
multiplicativity, and fresh projection from the exact sufficient current state.
Maximum listed error is1.78e-15 (product extents). Re-rooting uses the actual
coherent state, never the diagonally mixed checkpoint state.

Single-time observational entropy uses full Hilbert-trace cell volumes.
At the original case its effective volume is3.033274. Appending an inert
unresolved blank ancilla doubles this to6.066549 while D, spectral breadth
and output law are unchanged. This confirms its ambient-volume meaning;
it is not a defect in the established formula. Calling it root-reachable
extent would require a separate justified reference measure.

## Record retention and full-present dependency

Re-ran earlier two-round controls unchanged: retained first record -> complete
final-record breadth4; coherently uncomputed ->1; transferred into explicit E
->4 complete but2 locally. These are final-record results, not proof that
entire coherent-history extent becomes1 after uncomputation.

Supplement added after the first sweep: fix H=(pi/4)Z tensor Y and all source
operations, but prepare E in0 versus a Y eigenstate. Conserved source axis is
the same. E=0 gives trace distance1 between its conditional records; the Y
eigenstate gives distance0 and only induces a coherent source phase rotation.
Both have signal output breadth2; spectral history breadths are4 versus2.
This demonstrates why the full present, including environmental preparation,
matters. Neither conserved-axis selection nor one output entropy exhausts that
physical difference. It does not prove they must have unequal final lushness.

## Assessment and next decision

We now have an implemented bridge from a declared local interaction law to
conserved source alternatives and a quantitative assessment of their actual
recording. This supports using physically supplied observable structure instead
of arbitrary history labels. It does not select a universal maximal partition.

Keep a profile indexed by actual interaction/record structure, time and stated
resolution, with D carrying coherent refinements. Promote no tested scalar to
full coherent extent. The most useful next mathematical task is to specify how
to retain and compose noncommuting local observable structures when no common
record axis exists. Meanwhile the single-axis regime supplies a calibration
case where native refinements work. No new chemistry or large simulation is
needed to make that distinction.

## Validation and artifacts

45 aligned+12 competing cases, orientation/representation/product controls,
three retention controls, two supplementary environmental preparations.
Exact dense state spaces at most16 dimensional. Main run about0.13seconds.
24 combined focused tests passed; final numerical change to the supplementary
trace-distance evaluation was rechecked with all15 tests in the new module.
Focused lint clean. No sampling error. Raw results ignored locally at
results/local_runs/interaction_selected_history_v0/results.json.
No commit/push requested/performed. Two small-agent tasks supplied an algebra
check and focused tests; parent implemented and verified numerical results.

Physical background: [Zurek's decoherence/einselection review](https://arxiv.org/abs/quant-ph/0105127),
[Hartle's closed-system histories framework](https://arxiv.org/abs/gr-qc/9304006).
Numerical findings above are our finite-circuit results, not new general theorems.

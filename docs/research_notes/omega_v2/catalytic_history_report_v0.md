# Catalytic production history — exploratory run v0

4 October 2026. Same three physical laws and seeded preparation as the preceding catalytic run. This extension observes the history without changing the dynamics. It uses 'resource profile' for the separate consumption, return and activity accounts.

## Result

A catalytic production lineage can continue after its original bond dissolves. Surviving descendants sometimes catalyze further construction. Individual survival therefore misses a real continuation of production. Nevertheless, stronger catalysis does not yield a clear overall persistence gain in this model: it also speeds destruction, including reversals assisted by descendants. The continuing lineage mostly offsets the shorter survival of its original bond.

This is evidence about a finite mechanism that can facilitate lushness. Neither reach, lineage survival, construction count nor an integrated lifetime is being adopted as lushness. The weighted continuation field remains the comparison object.

## What is followed

The physical model is unchanged: four identical particles on five sites, internal-state noise, reversible bonds, motion, three fuel packets and an implicit heat bath. The barrier reductions b=0,1,2 accelerate both directions of a neighboring bond reaction when an aligned bond supplies the catalytic pathway. All start with a single bond at sites 0–1, two fuel packets and independent fair internal bits. Across b these preparations have identical energy, free energy and initial physical law. Details and full physical kernels are in the [preceding report](catalytic_binding_report_v0.md).

The new observer maintains these historical relations:

- The original bond follows its bonded component when it moves. A change of position is not its death.
- A newly formed bond is a descendant when the actual firing was a catalytic pathway supplied by the original bond or an existing descendant. Descendants also move with their components.
- Dissolution removes that particular bond's mark. Independent reassembly at the same place does not restore ancestry. A descendant can catalyze reassembly there, creating another descendant rather than resurrecting the original bond.
- The observer records whether a descendant has ever been produced and whether a descendant has subsequently catalyzed a formation. Current survival and these historical events remain separate.

These marks affect no rates, resources or physical observations. They are an exact finite observer of selected history properties, not new particles or extra physical branches. Summing over the observer's histories recovers the original physical generator and residual distributions. The entire physical process, including unmarked spontaneous construction, continues after all marks have disappeared.

Ancestry here means participation in a declared catalytic production pathway. The background formation pathway remains possible; an observed catalytic parent is not proof that the product could never have formed without it. Attribution depends on the model's explicit reaction mechanisms, not only on its aggregate state-transition generator. This also is not full biological inheritance: no template-copying mechanism, heritable recipe variation or adaptive selection process was added.

## Original survival versus continuing production

Probabilities are unconditional across all runs from the seeded preparation. 'Lineage present' means at least one original or descendant bond is present; it counts that event once, regardless of how many descendants exist. This chosen survival event is a diagnostic, not a definition of the full field.

| b | Cut | Original present | Descendants present after original loss | Original or descendant present | Any descendant ever produced |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 0.62400577 | 0.00000000 | 0.62400577 | 0.00000000 |
| 0 | 5 | 0.06778571 | 0.00000000 | 0.06778571 | 0.00000000 |
| 0 | 20 | 0.00000936 | 0.00000000 | 0.00000936 | 0.00000000 |
| 1 | 1 | 0.56636404 | 0.05333951 | 0.61970355 | 0.20111592 |
| 1 | 5 | 0.04157187 | 0.02767302 | 0.06924489 | 0.29051272 |
| 1 | 20 | 0.00000156 | 0.00000946 | 0.00001101 | 0.29407367 |
| 2 | 1 | 0.46158051 | 0.14720090 | 0.60878141 | 0.43768198 |
| 2 | 5 | 0.02211127 | 0.04667505 | 0.06878631 | 0.52018516 |
| 2 | 20 | 0.00000021 | 0.00001134 | 0.00001155 | 0.52167072 |

At b=2 and cut 5, looking only for the original bond gives 2.21% survival. Including descendants gives 6.88%, with 4.67% of all runs retaining descendants after the original has gone. The b=0 original-only baseline is already 6.78%. Thus the lineage substantially changes the interpretation of the strong-catalysis history without establishing a substantial persistence advantage over the baseline.

No descendants at b=0 follows from the absence of catalytic pathways. It does not mean there is no independent construction, organization or consequence in those runs. Likewise, extinction of these production marks does not imply erasure of every causal consequence: effects carried through fuel, internal states and other reaction paths are outside this ancestry observer and remain in the physical law.

## Do successors continue after the original is gone?

Condition on the cut-5 event 'original absent, descendants present', then evolve under the unchanged physical law. The next-formation probability concerns a descendant assisting at least one formation during the following five time units. It is computed by killing only that event in a diagnostic copy, not by altering the actual dynamics. The conditioning probability is shown to keep rare surviving histories from representing the whole population.

| b | Conditioning probability | P(next formation within 5, conditional) | Joint probability of both events | P(lineage still present 5 later, conditional) |
|---:|---:|---:|---:|---:|
| 1 | 0.027673 | 0.291930 | 0.008079 | 0.057347 |
| 2 | 0.046675 | 0.498570 | 0.023271 | 0.058860 |

This is a concrete continuation beyond an individual carrier: successors can contribute further construction after the original is destroyed. The conditional chance of such construction is substantial, but most selected lineages are no longer present five time units later. Production and persistence still differ.

## Turnover and integrated persistence

The following are expected event counts and expected time with at least one marked bond, truncated at time 50. They are separate descriptive quantities, not an aggregate objective or the completed infinite-history comparison. The lineage-time quantity can also be read as the expected original-or-descendant lifetime capped at 50, because ancestry cannot restart after its last marked bond is lost.

| b | Original-bond time | Original-or-descendant time | Extra time after original loss | Original-assisted formations | Descendant-assisted formations | Descendant-assisted reversals |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1.941096 | 1.941096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1 | 1.647779 | 1.941429 | 0.293650 | 0.368290 | 0.132155 | 0.150337 |
| 2 | 1.309626 | 1.916945 | 0.607319 | 0.956021 | 0.924191 | 0.980728 |

The b=1 lineage time nearly ties the baseline; b=2 is about 1.24% lower. This near cancellation is an observed finite comparison, not an established conservation theorem. Descendants can accelerate reversals as well as formation. Retaining only their constructive events would misdescribe their consequences. The ordinary physical resource profiles are retained for every cut, including both fuel consumption and reverse credits; catalytic event counts remain subsets rather than additional resource charges.

## Relation to the full-history question

At a late cut, 'this chain of production happened' and 'some of its products remain' can have very different probabilities. A present configuration or cumulative assembly count cannot reconstruct those relations. Following actual production across movement and replacement reveals a distinction that the earlier fixed-edge monitor did not track.

The observer nevertheless introduces no hidden physical power of ancestry: histories ending at the same complete physical state have the same future physical law. Its generator explicitly satisfies this condition. Historical organization belongs in the record of development; any influence on future physical events must be carried by the current physical configuration. The observer is a limited projection of history, not a completed lushness volume or a substitute for the full weighted process.

The present mechanisms provide catalytic succession without a demonstrated persistence advantage. A further physical extension would have to explain renewal or inheritance through actual reaction structure and resource use, rather than rewarding descendants for their label. The current shared fuel pool also remains a nonlocal coupling; this is not a clean spatial-range experiment.

## Checks and evidence

Run time: 6.93 seconds, one numerical worker. The physical model has 1,792 states. Its reachable observer has 2,560 states at b=0 and 12,864 at b=1 or 2. All noise and probability are retained; observer-state count is not a count of additional physical possibilities.

Six focused tests across the catalytic model and history observer passed. They check physical marginal preservation, probability and occupation mass, birth/loss accounting, movement, independent reassembly, native reversibility and the absent-pathway control. No exhaustive scientific validation is claimed.

- lumping_error: 7.11e-15.
- physical_marginal_error: 2.15e-16.
- mass_error: 1.33e-14.
- occupation_mass_error: 5.61e-13.
- root_accounting_error: 7.88e-15.
- descendant_accounting_error: 1.6e-14.
- resource_accounting_error: 1.88e-13.

Reproduce:

    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_history_v0
    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_history_analysis_v0

[Results, definitions, parameters and source hashes](catalytic_history_v0/results.json)

[b=0 history law](catalytic_history_v0/barrier_0_histories.npz) · [b=1 history law](catalytic_history_v0/barrier_1_histories.npz) · [b=2 history law](catalytic_history_v0/barrier_2_histories.npz)

The NPZ evidence retains the reachable history states, native channel-resolved transitions, sparse generator, initial law, residual laws, occupation integrals, conditional follow-ups and resource/event rates. These suffice to reproduce the finite histories' probabilities without sampled trajectories. The underlying physical rates are unchanged from the preceding run.

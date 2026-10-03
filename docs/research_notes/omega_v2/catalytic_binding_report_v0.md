# Catalytic continuation, propagation and recovery — exploratory run v0

4 October 2026. Three exact 1,792-state classical laws. Four physical preparations and equilibrium under each law; cuts 0,1,5,20; response lags 1,5; 74 declared frames and 43 reaction channels. No outcome was required to win.

## Finding

Composition now changes subsequent construction: an aligned bonded pair supplies an additional reversible pathway for a neighboring bond reaction, and the resulting bond can assist another. This mechanism is specified in the physics. Its existence is an implementation witness, not a discovered law of generativity. The run asks what that mechanism actually does to subsequent assembly, spatial response and recovery with noise, mobility, costs and reversals retained.

Stronger assistance greatly raises the probability of having formed a four-particle chain at least once, but changes its later occupancy much less. Most added construction is reversed. A native internal flip can now affect future bond geometry; selected distant responses grow while other responses shrink. More frequent first restoration after breakage does not imply better later retention. These are distinct deformations of one residual process, not a scalar ranking.

## Common physical model

Four identical particles occupy five reflecting-line sites. A site is empty, 0 or 1; the internal bit moves with its particle. No organism, constructor or beneficiary labels enter the rates. Native internal flips have rate 0.05; adjacent unequal bits exchange at rate 1 whether bonded or unbound. A bonded component of size n translates at rate 1/n when space permits. The dense 'dispersed' preparation below is two separated pairs, not a dilute molecular gas.

The earlier reversible bond/fuel law is retained: B=3 fuel/spent packets, E=4(F+number of bonds), thermal formation/breakdown rates 0.02 exp(∓2), fuel-assisted formation 0.25F, and reverse disassembly 0.25(3−F). Equilibrium is π(x) proportional to binomial(3,F) exp(−E). Bonds are energetically costly in this model; this assumption is not universal chemistry. The shared fuel pool is well mixed and the heat bath implicit.

A present bond whose two endpoint bits agree supplies an additional pathway for the adjacent bond reaction. Its rate is (exp(b)−1) times the original fuel-assisted rate. One catalyst therefore makes the total rate exp(b) times the background; two catalysts contribute parallel pathways. The catalyst and its internal bits are unchanged in that reaction. BOTH formation and reversal are accelerated by the same factor, preserving detailed balance, energies and π. Native flips can open or close this catalytic condition.

The barrier reductions b=0,1,2 are physical kinetic parameters in thermal units, not lushness multipliers. Each law is shared by all preparations. Changing b compares different kinetics, not a cost-free intervention available to an agent. No primitive transition is invented during a run: composition changes which existing mechanisms are available at the current state.

| Preparation | Occupied sites | Initial bonds | Fuel | D(p||π), nats |
|---|---|---|---:|---:|
| dispersed | 0,1,3,4 | none | 3 | 13.707487 |
| contact_unbound | 0,1,2,3 | none | 3 | 13.707487 |
| seeded | 0,1,2,3 | 0–1 | 2 | 12.608875 |
| assembled | 0,1,2,3 | 0–1,1–2,2–3 | 0 | 13.707487 |

All four have independent fair internal bits and stored energy 12. Contact-unbound, dispersed and fully assembled match free energy too. The seeded preparation has ln 3 less free energy, from fuel-stock degeneracy; no seed-versus-unbound advantage is treated as a fully matched comparison. The fuel-free assembled preparation can disassemble and regain fuel. Zero fuel is not a terminal state.

## Construction, persistence and bills

Seeded preparation at cut 5. First occurrence is computed with an absorbing diagnostic copy; the actual residual law continues through breakdown and reversal. Gross assembly counts are debits, reverse counts are credits; their difference is net fuel depletion. Catalytic counts in the evidence are subsets of these bills and must not be added a second time.

| b | P(chain occurred by 5) | P(chain present at 5) | Mean bonds at 5 | Fuel assembly debits | Reverse credits |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.157043 | 0.009877 | 0.948013 | 3.114384 | 2.382981 |
| 1 | 0.285755 | 0.010323 | 0.949904 | 4.199637 | 3.452750 |
| 2 | 0.456755 | 0.010514 | 0.950439 | 7.225925 | 6.469607 |

The matched, fully assembled preparation also loses its initial chain faster with stronger catalysis:

| b | P(chain present at cut 1) | Mean bonds at cut 1 | Mean bonds at cut 5 |
|---:|---:|---:|---:|
| 0 | 0.096666 | 1.580896 | 0.883367 |
| 1 | 0.046228 | 1.427934 | 0.905619 |
| 2 | 0.037788 | 1.383033 | 0.918175 |

A path monitor records one local cascade: the 0–1 bond assists formation of 1–2, then that still-present 1–2 bond assists formation of 2–3. Losing or moving the intermediate bond resets the unfinished monitor. This observes one spatially anchored sequence, not every possible construction lineage or an identity tracked after movement. Once observed, the monitor retains that historical fact while the physical process keeps evolving.

| b | Seeded: P(sequence by 5) | Seeded: P(sequence by 20) | Initially unbound: P(sequence by 20) |
|---:|---:|---:|---:|
| 0 | 0.000000 | 0.000000 | 0.000000 |
| 1 | 0.041813 | 0.057065 | 0.037402 |
| 2 | 0.186855 | 0.244847 | 0.181337 |

Zero at b=0 follows from the absence of the monitored catalytic pathways. The monitor's physical marginal was checked against the unmonitored dynamics. These probabilities establish finite, reversible reuse in this specified model; they are not evidence for unbounded generativity.

## Consequence across physical frames

For native reaction c at cut law p, contexts x are weighted by p(x)r_c(x)/Σp(x)r_c(x). Response at lag τ is the average total-variation distance between the future frame laws starting from x and from the reaction's target. The reaction rate Σp(x)r_c(x) is reported separately. Absent reactions have an explicit false event_present flag; their zero array entries are not measured zero effects.

This is a state-resolved counterfactual diagnostic, not a free intervention, an attainable decoder, or a signed benefit. The full event law remains alongside it. No average or vote over frames defines a winner. Frames comprise the previous 64 site-subset/fuel views plus each bond alone/with fuel and the joint bond field alone/with fuel. They do not exhaust every possible physical observer or cost of reading.

The table follows a native bit flip at site 0 from the seeded preparation at cut 0. Each target is a physical site's full empty/0/1 state. Response can therefore include altered occupancy, not merely delivery of a readable bit. All five source sites, all other reactions and joint frames remain in the raw profiles.

Site separation indexes the spatial profile, not a strict causal distance: the shared well-mixed fuel stock also couples spatially separated reactions. This probe cannot isolate transmission along neighboring bonds from transmission through that common resource. Spatially resolving fuel would be a further physical extension, not a correction factor to this readout.

| b | Lag | Site 0 | Site 1 | Site 2 | Site 3 | Site 4 | Joint bond field |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 0.459817 | 0.290930 | 0.111689 | 0.034138 | 0.008264 | 0.000000 |
| 0 | 5 | 0.142144 | 0.146816 | 0.126801 | 0.107419 | 0.083350 | 0.000000 |
| 1 | 1 | 0.459407 | 0.289706 | 0.123879 | 0.037278 | 0.009522 | 0.077303 |
| 1 | 5 | 0.141595 | 0.146196 | 0.127715 | 0.108356 | 0.084027 | 0.004084 |
| 2 | 1 | 0.459099 | 0.288474 | 0.131062 | 0.041798 | 0.014484 | 0.119477 |
| 2 | 5 | 0.141292 | 0.145815 | 0.127573 | 0.109172 | 0.085009 | 0.006792 |

At b=0, the geometric process does not depend on internal bits; the bit-to-bond response vanishes up to numerical error. Turning assistance on creates that physical dependence. Its nonzero response confirms the specified coupling rather than independently discovering it. The magnitude, delay and competing propagation changes are the probe's output. There are only five sites; no asymptotic decay length is inferred.

At b=2, cut 0 and lag 1, seeded versus dispersed gives greater site-4 response (0.014484 versus 0.008928), but lower joint response at the other four sites (0.358317 versus 0.400038). Farther propagation on one coordinate does not establish larger total access. In the exactly resource-matched assembled/contact-unbound comparison, the all-frame profiles also cross.

## Native breakage and restoration

Start from the seeded law at cut 5 and condition on an actual thermal breakdown of the bond at physical edge 0. Its event rate and flux-conditioned pre/post laws are retained. Evolve both the post-break law and a skipped-event reference under the same autonomous dynamics. This is not a clamped controller. The breakdown releases bond energy to the implicit bath. Rates are hazards, not finite-interval probabilities.

Conditioning produces a different damage ensemble at each b. Comparisons below concern each law's own native failures, not the isolated effect of b on one identical post-damage distribution. Restoring an edge means the local bond is present again, possibly between different particles; it does not prove recovery of the complete earlier access structure.

| b | Time since break | P(first local restoration) | P(local bond present now) | TV(taken, skipped full residual laws) |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0.200418 | 0.131454 | 0.575952 |
| 0 | 5 | 0.525064 | 0.125982 | 0.337798 |
| 0 | 20 | 0.756424 | 0.052488 | 0.153522 |
| 1 | 1 | 0.216200 | 0.135717 | 0.557497 |
| 1 | 5 | 0.541596 | 0.124965 | 0.339511 |
| 1 | 20 | 0.758293 | 0.051866 | 0.154056 |
| 2 | 1 | 0.247527 | 0.141133 | 0.539275 |
| 2 | 5 | 0.566664 | 0.124355 | 0.340366 |
| 2 | 20 | 0.764346 | 0.051510 | 0.154389 |

Stronger assistance raises first-return probability here, but late bond occupancy is slightly lower. A return is not permanence: every formed bond retains a positive thermal breakdown hazard. Full residual laws and all reaction/frame responses after breakage remain available rather than being replaced with a binary 'recovered' score.

## Scope, checks and evidence

The common equilibrium distribution is unchanged by assistance. Equilibrium still has native events and lagged response, including a small bit-to-bond response when catalysis is on. Zero net equilibrium currents do not imply zero consequence. This is a bath-coupled finite classical substrate, not a closed universe, quantum branching calculation, gas defeat, lushness extent or ethical verdict.

The next unresolved issue is how to compare these joint residual deformations without allowing gross turnover, a privileged destination or a selected recovery target to stand in for the entire field. This run improves the substrate on which the adopted aggregation can be investigated; it does not finish or replace that aggregation.

Numerical run: 38.16 seconds with one numerical worker. Three new focused tests cover channel reversibility, catalyst preservation, physical marginal preservation of the path monitor, fuel/bond accounting, reflection/bit inversion and preparation matching. Together with the existing spatial/fuel/local-flow checks, 12 tests passed. Lint passed. These are implementation checks, not independent empirical evidence.

Maximum run residuals:

- fuel_balance: 3.91e-14.
- bond_balance: 2.75e-14.
- probability_mass: 1.39e-14.
- detailed_balance: 2.12e-22.
- kernel_rows: 5.33e-15.

Reproduce:

    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_binding_v0
    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_binding_analysis_v0

[Profiles, actual laws, bills, monitor results and source hashes](catalytic_binding_v0/profiles.json) · [Comparison counts](catalytic_binding_v0/comparison_summary.json)

[No-assistance kernels](catalytic_binding_v0/barrier_0_kernels.npz) · [b=1 kernels](catalytic_binding_v0/barrier_1_kernels.npz) · [b=2 kernels](catalytic_binding_v0/barrier_2_kernels.npz)

NPZ files retain states, channel rates/targets, reward rates, sparse Q, equilibrium and exact numerical transition kernels at both lags. No simulated sample trajectories or fitted parameters are substituted for these laws.

[Previous thermal/mobile comparison](thermal_binding_report_v0.md)

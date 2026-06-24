# Recovery Profiles for Finite Observation Channels

## A Machine-Checked Calculus of Exact, Approximate, Robust, and Joint Recovery

S. Poole  
June 2026

## Abstract

Let a finite source be transmitted through a channel, reduced to an observation, and decoded against a declared target. The most informative primitive for this setting is not a single accuracy or information score, but the source-indexed success profile

```text
r_delta(x) = Pr[delta(o(Y)) = d(x) | X = x].
```

This paper develops a finite recovery calculus organized around that profile. It places exact recovery, threshold recovery, decoder-class restrictions, randomized decoding, prior-relative performance, robustness over channel ambiguity, deterministic observation coarsening, target post-processing, and marginal versus joint recovery on one explicit specification surface.

A Lean 4 development checks the central laws. Support-exact recovery is precisely the threshold-one boundary of graded recovery. Target-distinct sources sharing observed probability mass impose a quantitative ceiling on deterministic worst-case recovery. Deterministic observation refinement preserves recoverability, so recovery already absent from a finer observation cannot be recreated by further deterministic coarsening. Recovery of a fine target implies recovery of every deterministic post-processing of that target. Finite strictness examples separate deterministic from randomized recovery, channel-wise from robust recovery, prior-relative from worst-case guarantees, and marginal from joint recovery.

The contribution is a compact machine-checked synthesis with explicit quantifier structure and canonical counterexamples. It is intended as a foundational component for later work on learned representations, monitoring, abstraction, and decision-making under partial observation.

Keywords: finite channels; recovery profiles; statistical experiments; observation coarsening; robust decision theory; zero-error recovery; Lean 4

## 1. Introduction

Suppose a finite source passes through a channel, an observer retains only a summary of the output, and a decoder attempts to reconstruct a declared target. What, precisely, does it mean to say that the target is recoverable?

The answer depends on more structure than a scalar score records. One must specify the target, the retained observation, the permitted decoder class, the source quantifier, and whether a single witness must work across uncertainty about the channel. One must also distinguish a marginal target from a joint target and zero-error recovery from high-confidence recovery. Changing any one of these ingredients changes the mathematical statement.

This issue appears in comparison of statistical experiments, sufficient statistics, communication through noisy or coarsened channels, learned representations, diagnostic probes, monitoring systems, and abstractions used for planning or verification. The same observation can be highly informative on average while failing completely on a particular source class. A decoder may exist separately for each model in an ambiguity set while no common decoder works for all of them. High prior-weighted success may conceal a worst-case failure. Separate marginal guarantees may leave the joint target unresolved.

A simple example illustrates the point. Consider a uniform 100-class target whose retained observation distinguishes 98 classes and merges the final two. The normalized mutual information is approximately 0.997, and the optimal average deterministic accuracy is 0.99. Yet every deterministic decoder fails with probability one on at least one merged class, so its best worst-case source recovery is zero. None of these numbers is incorrect; they answer different questions.

Given a finite channel `C`, target `d`, observation `o`, and decoder `delta`, we take the source-indexed success profile

```text
r_delta(x) = Pr[delta(o(Y)) = d(x) | X = x]
```

as the primary object. Exact, approximate, robust, prior-relative, randomized, marginal, and joint recovery are then stated as different predicates or functionals on this profile, with quantifier order explicit.

### Contributions

1. **A source-indexed recovery calculus.** We define a finite specification surface for deterministic, class-restricted, randomized, robust, prior-relative, marginal, and joint recovery.
2. **A machine-checked theorem spine.** Lean 4 proofs establish the threshold-one zero-error boundary, the observed-support criterion, a quantitative confusion bound, monotonicity under observation refinement, permanence under deterministic coarsening, and monotonicity under deterministic target post-processing.
3. **A strictness map.** Canonical finite witnesses separate high aggregate information from source-wise recovery, high-confidence from zero-error recovery, per-model from robust recovery, prior-relative from worst-case success, and marginal from joint recovery.
4. **A reusable formal artifact.** The definitions, theorems, examples, and a small finite evaluator are packaged as a mechanized component for later work on representations, monitors, and finite decision problems.

## 2. Aggregate Information Does Not Determine Source-Wise Recovery

Let `N >= 3`, let `X` be uniform on `{1, ..., N}`, and let the target be `D = X`. The channel reveals `X` exactly, but the retained observation merges classes `N-1` and `N` while leaving all other classes distinct. Then

```text
I(D; O) = log_2 N - 2/N,
I(D; O)/H(D) = 1 - 2/(N log_2 N) -> 1.
```

The optimal average deterministic accuracy is `(N-1)/N`, but every deterministic decoder has worst-case source success `0`. The optimal randomized worst-case success is `1/2`.

The proof is immediate: the observation is deterministic and loses exactly one bit of target entropy on a merged label that occurs with probability `2/N`. A deterministic decoder must assign the merged label to one of the two classes, so it fails with probability one on the other merged source. A randomized decoder splitting the merged label uniformly achieves `1/2` on both merged sources, and no randomized decoder can exceed `1/2` on both because the two output probabilities sum to one.

The example shows that a highly informative representation under an aggregate metric need not satisfy a source-wise recovery obligation.

## 3. Recovery Specifications

Let `X`, `Y`, `D`, and `O` be finite sets. A channel is a row-stochastic map

```text
C : X x Y -> [0,1],     sum_y C(y | x) = 1.
```

A declared target is a function `d : X -> D`. An observation map `o : Y -> O` records what the verifier, monitor, or representation retains. A deterministic decoder is `delta : O -> D`.

For a deterministic decoder `delta`, define the per-source success profile

```text
r_delta(x) = sum_y C(y | x) * 1{delta(o(y)) = d(x)}.
```

The failure mass is `f_delta(x) = 1 - r_delta(x)`. The vector `r_delta` is the primary object. Average accuracy, worst-case success, and exact recovery are all functionals or predicates on that vector.

A fixed decoder satisfies source-wise threshold `tau` when

```text
forall x in X, r_delta(x) >= tau.
```

Recovery exists at threshold `tau` if some decoder satisfies this condition. For an allowed decoder class `Delta`, recovery exists in `Delta` if the witness decoder must belong to `Delta`.

### Zero error, randomization, ambiguity, priors, and joints

A decoder is support-exact if every positive-probability output decodes correctly:

```text
C(y | x) > 0 => delta(o(y)) = d(x).
```

A randomized decoder is a channel from observations to target labels. For an ambiguity set `Gamma` of channels, robust recovery requires one decoder to satisfy the threshold for every `C in Gamma` and every source. This differs from allowing a different decoder for each channel.

For a prior `mu` on `X`, prior-relative success is

```text
E_mu[r_delta] = sum_x mu(x) r_delta(x).
```

For targets `d1` and `d2`, the joint target is `x -> (d1(x), d2(x))`.

## 4. Machine-Checked Core Laws

The theorem spine is checked in Lean 4 over exact rational finite channels.

### Profile mass laws

For every deterministic decoder and source,

```text
0 <= r_delta(x) <= 1,
0 <= f_delta(x) <= 1,
r_delta(x) + f_delta(x) = 1.
```

Hence `r_delta(x) = 1` iff `f_delta(x) = 0`.

### Support-exact recovery is threshold-one recovery

A deterministic decoder is support-exact iff

```text
forall x in X, r_delta(x) = 1.
```

Therefore support-exact recovery exists iff recovery exists at threshold `1`.

The proof uses nonnegativity: support exactness makes every positive-mass output contribute to the success sum, so row normalization gives success one. Conversely, success one gives zero failure mass, and no positive-mass output can be decoded incorrectly.

### Observed-support criterion

For target label `e`, define its observed positive support

```text
S_e = { o(y) : exists x, d(x)=e and C(y | x)>0 }.
```

Support-exact recovery exists iff `S_e` and `S_e'` are disjoint for every pair of distinct target labels `e != e'`. This is the one-shot, target-relative zero-error condition.

### Quantitative confusion bound

Suppose `d(x0) != d(x1)` and there are outputs `y0`, `y1` with

```text
o(y0) = o(y1),
C(y0 | x0) >= epsilon,
C(y1 | x1) >= epsilon.
```

Then no deterministic decoder can satisfy source-wise threshold `tau > 1 - epsilon`.

The decoder assigns one target value to the shared observation. If it assigns `d(x0)`, then the mass at `y1` is necessarily an error for `x1`; otherwise the mass at `y0` is an error for `x0`. One of the two sources has failure mass at least `epsilon`.

### Observation refinement and irreversible coarsening

Let `o_f : Y -> O_f` be a fine observation and `o_c : Y -> O_c` a deterministic coarsening, so `o_c = g o o_f` for some `g : O_f -> O_c`. For every coarse decoder `delta_c`, the lifted fine decoder `delta_f = delta_c o g` has exactly the same source-wise profile. Thus every deterministic threshold available from the coarse observation is available from the fine observation.

Contrapositively, if no decoder on the fine observation reaches threshold `tau`, then no decoder on any deterministic coarsening reaches threshold `tau`. The Lean development also proves decoder-class-restricted, robust, and randomized variants under corresponding closure conditions.

This is representational irreversibility under a closed observation interface, not a claim that physical systems cannot acquire new sensors or side information.

### Target post-processing

A deterministic map `h : D -> E` produces a coarser target `h o d`. If `delta` predicts `d`, then `h o delta` predicts the coarser target. For every source,

```text
r_{h o delta}^{h o d}(x) >= r_delta^d(x).
```

Consequently, threshold recovery and support-exact recovery transfer from a fine target to every deterministic post-processing. Joint-to-marginal recovery is an instance using coordinate projection.

## 5. Recovery Regimes and Strict Separations

The calculus is useful because it prevents nearby but inequivalent recovery claims from collapsing into one another. Each of the following has a finite exact witness in the mechanized development.

| Conflated claims | Canonical witness | Correct conclusion |
|---|---|---|
| High-confidence implies zero-error | Full-support binary channel with profile `(99/100, 99/100)` | Zero error is threshold one and requires support separation. |
| Positive support determines graded recovery | Two full-support channels with correct masses `9/10` and `3/5` | Probability mass, not support alone, controls threshold recovery. |
| Deterministic and randomized equivalence | One-label binary observation | Decoder class matters; randomization raises maximin recovery from `0` to `1/2`. |
| Per-model decoder implies robust decoder | Identity and bit-flip channels | `forall C exists delta_C` does not imply `exists delta forall C`. |
| High expected score implies worst-case guarantee | Skewed prior with constant observation | Bayes and minimax claims use different source quantifiers. |
| Marginals imply joint | Separate coordinate observations | Joint recovery needs a common panel or explicit coupling assumptions. |
| Aggregate information implies source-wise recovery | The `N`-class merge | Aggregate information does not certify the minimum of the source profile. |

## 6. Relation to Standard Theory

Blackwell's order asks when one statistical experiment is at least as informative as another for every decision problem. Le Cam's deficiency theory extends this comparison to approximate simulation of experiments. The deterministic observation coarsenings studied here are a restricted garbling relation. Our lifting theorem is target-relative and source-profile-valued rather than a complete comparison of experiments.

Support-exact recovery is a one-shot target-relative zero-error condition. The observed-support theorem can also be read as a finite sufficiency statement: the target must be constant on every observation fiber reached with positive probability.

Prior-relative and source-wise threshold claims correspond to different decision criteria. Robust recovery adds another quantifier: a single witness must satisfy every channel in a declared ambiguity set. The calculus does not select one criterion as universally correct; it records which criterion has actually been established.

Predictive usable-information and probing work make informativeness relative to constrained predictor families. This paper differs in taking the source-indexed profile as primary and representing zero-error, robust, prior-relative, and joint quantifiers in the same mechanized calculus.

The contribution is not a new channel-capacity theorem or a replacement for Blackwell or Le Cam comparison. It is a compact mechanized synthesis: the profile, witness class, source quantifier, uncertainty quantifier, and target granularity remain explicit across several standard regimes, and nearby false converses are retained as checked finite counterexamples.

## 7. Mechanization

The theorem spine was formalized in Lean 4 using exact rational finite channels and mathlib. Exact rational arithmetic removes numerical tolerance from proof statements. The principal formal modules cover:

- finite channel normalization and source-profile mass laws;
- deterministic and class-restricted threshold recovery;
- observed-support exactness;
- deterministic observation refinement and coarsening permanence;
- target post-processing;
- quantitative confusion bounds;
- randomized, robust, prior-relative, and joint extensions;
- finite strictness examples.

The development is self-contained at the level of this paper and does not require project-specific terminology.

## 8. Limitations and Open Problems

- **Finite one-shot setting.** The calculus treats finite source and output spaces and one-shot decoding. It does not establish asymptotic rates, block-code capacity, or continuous-state results.
- **Deterministic observation coarsening.** The current refinement theorem covers deterministic post-processing. Stochastic garblings would connect the calculus more directly to Blackwell and Le Cam comparison.
- **Randomized robust optimization.** The formal layer embeds deterministic decoders into randomized decoders and proves strict examples, but it does not yet solve unrestricted randomized robust recovery as a mechanized linear program.
- **Joint recovery and coupling.** The same-panel union bound is safe but often loose. Tighter guarantees require explicit assumptions about couplings, conditional independence, shared resources, or observation structure.
- **Target validity is external.** The calculus can show that a target is or is not recoverable from a declared observation. It cannot prove that the target is semantically correct, ethically appropriate, or empirically natural.
- **No empirical claim.** The examples are exact finite stress tests. They establish logical separations, not prevalence in deployed systems.
- **Dynamics are excluded.** Policy-conditioned continuation and reach-avoid guarantees belong in a separate continuation-integrity paper.

## 9. Conclusion

Finite target recovery is naturally profile-valued. A channel, observation, and decoder induce a source-indexed vector of success probabilities, and familiar scalar criteria select different projections or quantifiers over that vector. Keeping the profile explicit makes several distinctions unavoidable:

- aggregate information need not determine source-wise recovery;
- high-confidence recovery need not imply zero error;
- separate per-channel witnesses need not yield one robust witness;
- prior-relative success need not yield a worst-case guarantee;
- marginal recovery need not determine joint recovery;
- deterministic coarsening cannot restore a recovery guarantee already absent from a finer observation.

The resulting calculus is deliberately modest. Its role is to provide a stable finite foundation: a declared target, observation, witness class, and quantifier structure determine a precise recovery proposition, and that proposition can be checked without substituting a nearby metric.

## Lean theorem map

| Formal component | Representative checked statements | Paper role |
|---|---|---|
| Finite channel | `success_nonneg`, `failureMass_nonneg`, `success_add_failureMass`, `success_le_one` | Profile mass laws |
| Deterministic recovery | `recoveryAt_mono_threshold`, `recoveryInAt_mono_threshold`, `supportExactRecovery_iff_recoveryAt_one` | Threshold and zero-error boundary |
| Exact support recovery | `exactRecoveryExists_iff_observedSupportDisjoint` | Observed-support criterion |
| Observation refinement | `lifted_decoder_success_eq`, `recoveryAt_mono_observation_refinement`, `supportExact_mono_observation_refinement` | Fine/coarse transport |
| Coarsening permanence | `recoveryAt_failure_persists_under_coarsening` and restricted, robust, randomized variants | Data-processing contrapositive |
| Target post-processing | `success_le_targetPostprocess`, `recoveryAt_targetPostprocess`, `exactRecovery_targetPostprocess` | Fine-to-coarse target monotonicity |
| Confusion bound | `wrong_observation_mass_le_failureMass`, `shared_observation_mass_blocks_recoveryAt` | Quantitative obstruction |
| Randomized recovery | deterministic embedding; threshold monotonicity; one-label strictness witness | Decoder-class axis |
| Robust recovery | singleton reduction; threshold and ambiguity monotonicity; identity/flip strictness witness | One decoder across ambiguity |
| Prior-relative recovery | worst-case implies expected threshold; point-mass reduction | Bayes projection |
| Joint recovery | joint-to-marginal post-processing; same-panel paired-decoder lower bound | Marginal/joint relation |

## Recovery specification checklist

| Question | Required declaration |
|---|---|
| What must be recovered? | Target map `d : X -> D`. |
| What is retained? | Observation map `o : Y -> O`. |
| What witness power is allowed? | Deterministic, randomized, or otherwise restricted decoder class. |
| Which sources must succeed? | Source-wise threshold, prior-weighted expectation, or another explicit aggregation. |
| Which models must share a witness? | One channel, per-channel witnesses, or one robust witness over an ambiguity set. |
| Is the target marginal or joint? | Full target and any deterministic post-processing used in the claim. |
| Is the observation fine or coarsened? | Explicit factorization relation and decoder-class closure under lifting. |

## References

See the LaTeX version of this paper for the full bibliography. The main reference clusters are Blackwell comparison of experiments, Shannon zero-error information theory, statistical decision theory, abstract interpretation, model checking, usable information, and Lean/mathlib.

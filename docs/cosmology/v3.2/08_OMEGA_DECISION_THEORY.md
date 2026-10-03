# 08 — Omega Decision Theory

## Decision architecture

Omega Decision Theory (ODT) organizes decisions around the gap between the complete consequential object and the model available to an agent. It makes three things separately inspectable: the justification for an action, the comparison among options, and the resolution of whatever conflict remains.

```text
ODT0 — License: does the physical argument support the declared continuation requirements?
ODT1 — Compare: use the comparisons actually supported, including incomparability.
ODT2 — Arbitrate: apply an explicit rule where action is still necessary.
```

ODT is not presently a replacement for expected utility theory, causal decision theory, or theories of logical counterfactuals. A concrete ODT implementation may still need their answers. Its distinctive focus is preserving justified continuation conditions through modelling and choice. In particular, it takes no position on Newcomb-type problems; the decision-theoretic assumptions needed to address them have not been supplied.

## The decision frame

Before assessing an action, specify the affected systems, their registered requirements, the available interventions and their realization witnesses, plausible contingencies, resources, and horizons. Record what is known, what is estimated, and which concrete features the model omits.

The frame is revisable. Discovering another affected valuer, a hidden dependence, or a missing repair route can change the licensed set. That revision is part of decision quality, not an inconvenience to be suppressed once optimization has started.

GE motivates consideration for possible value under uncertainty (Part 07). A decision frame records how that commitment is being applied. Inclusion in the frame does not automatically require preserving every registered process. Delay and inaction are assessed alongside intervention, including threats to shared continuation and the need for defense. Justifying a requirement and demonstrating that an action satisfies it are distinct tasks.

## ODT0: justification that survives contact with the world

Licensing asks whether an action preserves the justified corridor and whether the supporting argument applies to the concrete system.

Suppose an abstract model says a damaged process can always be repaired. That claim is useful only if the abstract repair has a realizable physical counterpart under the stated resources and contingencies. A model can invent a recovery route by dropping a dependency, merging distinct agents, treating a merely possible intervention as available, or reporting conditional reliability without the probability of preparing the apparatus. The realization witnesses of Part 02 are exactly the evidence ODT0 asks for.

One sufficient pattern is a simulation relation linking abstract states and actions to concrete ones, with verified preservation of the required continuation properties. The proof obligation depends on whether the claim is existential, robust, probabilistic, or adversarial. **Existential reachability is weaker than robust recovery.** A path in an optimistic abstraction cannot establish robust recovery in reality.

ODT0 has two different negative outputs:

- **demonstrated violation:** the action breaches a requirement;
- **insufficient justification:** the argument that it does not has not been made.

These are kept distinct. Under urgency a registered fallback may be needed. The framework does not turn missing evidence into a theorem of either safety or catastrophe.

## ODT1: retain justified incomparability

Among licensed options, compare what the evidence and the normative commitments actually support. A partial order can express dominance without pretending that every tradeoff has a common unit.

Suppose two legitimate aims remain. An option that improves both over another dominates it. One that improves the first while weakening the second may be incomparable (Part 11, Example 9). Lushness is intended as a possible adjudicator of such comparisons through their joint continuation structure. Establishing that role requires a justified relation to value-capable possibility; naming a structural score does not resolve the conflict.

When support, probability, recovery, and horizon matter differently, keep them visible. A large support carrying almost no probability and a concentrated high-probability gain need not receive the same assessment.

## ODT2: explicit arbitration

Action sometimes requires choosing from a finite frontier of incomparable options. Arbitration can use a negotiated priority, a voting rule, a fairness criterion, a lottery, or a registered score. The authority and rationale for the rule are recorded.

If every candidate breaches some requirement, an emergency rule may compare violations. That is a decision under conflict, not a retroactive declaration that all requirements were met. Recording the breach supports later repair and institutional learning.

Finite maximization is easy once a score is supplied. The hard work is whether the score is legitimate and whether its inputs faithfully describe the world.

## Low-probability claims and large stakes

ODT does not automatically solve Pascal-style problems. A claim involving a tiny probability and an enormous consequence must still specify the outcome, its evidential support, the probability model, the scope of aggregation, and any double counting.

The architecture exposes where an argument's force comes from. An unbounded utility, an invented branch count, or a model that treats incompatible scenarios as simultaneously additive can dominate a calculation for reasons unrelated to the physical object. Keeping support, weight, and consequence structure separate makes those failures easier to diagnose.

The diagnostic rare-event bound (Part 12, §I) gives L_cov ≤ βp for one bounded-feature construction. It shows sensitivity to occurrence weight under a declared normalization. It does not bound every candidate comparison, remove calibration choices, or justify ignoring a rare catastrophe. A comparison must keep the physical event weight alongside its conditional consequence.

## Exact maximization as a research comparison

The unrestricted branch of Part 07 evaluates

```text
F_θ(a) = L_θ(G_a)
```

over all physically admissible actions a in a finite model, where G_a is the full modelled continuation object after a, and θ specifies a candidate comparison. It adds no independent ethical corridor. Practical ODT keeps its stated commitments while this stronger proposal is examined. **[proposed]**

For the same exact objective and action set A, restricting to a nonempty subset A_R cannot improve the attainable maximum **[established; Part 12, §J]**:

```text
max_{a ∈ A_R} F_θ(a) ≤ max_{a ∈ A} F_θ(a).
```

A protection can nevertheless be compatible with the optimum, or help a bounded evaluator pursue the target under error. If establishing a rule changes others' behaviour, adopting that rule is an action with a different continuation, and it must be modelled as one.

Keep three kinds of variation apart: physical circumstances φ, comparison parameters θ, and information or approximation limits η. Map where preferred policies change, including ties and calibration-dependent boundaries. **Neither parameter-space volume nor "frequent victories" counts as robustness** without a defended measure on the parameter space and a meaningful parameterization. Candidate accounts of the value–valuer relation should supply comparisons independently of the score being assessed, so that agreement is informative rather than built in.

The project is not committed to permanent anti-optimization, and its truth does not depend on promising a capability advantage.

## What the decision prototype did and did not establish

The [public finite prototype](../../research_notes/omega_v2/lushness_decision_report_v0.md)
compared declared future-requirement families with matched controls and
explicit guards. In the reported achievement comparison, the joint candidate
achieved 5/6 against 35/36 for direct optimization with the same guards.
The revised-plan stratum retained a zero result. Those failures are evidence
against treating the current requirement family as an adequate proxy for
unknown future valuation, not evidence that the new atlas has already repaired it.

The target is an actual decision theory grounded in the field comparison.
The current ODT0–ODT2 architecture is an operational scaffold while that
comparison is developed. A richer physical description alone does not close
the decision-theoretic commitments about intervention, policy choice or
logical dependence.

In particular, identity as a physical trajectory does not by itself choose a
Newcomb counterfactual. Conditioning on a policy correlated with a prediction
and intervening on a later action while holding its causes fixed are different
comparison rules. A policy-level or updateless version may be investigated;
its rule must be stated rather than inferred from identity vocabulary.

## Why this matters for alignment

An increasingly capable agent can optimize the wrong representation more effectively. ODT asks it to preserve the relation between its representation and the continuation it is meant to govern: affected valuers remain represented, recovery claims remain realizable, joint feasibility is not assumed from individual feasibility, and correction remains possible.

The derived organization graph gives this concrete targets. A plan can be checked for what it does to construction and maintenance edges (does it destroy or build enabling conditions?), to control and information edges (does it capture processes it does not construct?), and to joint feasibility (does it make others' requirements jointly unsatisfiable?). For most reward functions in a broad class of environments, optimal policies tend to keep options open and acquire control over them; work on power-seeking makes that tendency precise in its stated settings [established; R53], and empowerment is a related measure of control [R55]. ODT's contribution is to measure such plans against the whole object rather than against the planner's own compression of it.

This is a useful research and governance target before any universal value measure exists. It can be implemented as modelling obligations, audit questions, and decision records. Success should be judged by whether those obligations catch consequential mistakes, not by whether a system produces more elaborate justifications.

Further reading: process models [R15, R19]; viability [R23]; power-seeking and empowerment [R53, R55].

---

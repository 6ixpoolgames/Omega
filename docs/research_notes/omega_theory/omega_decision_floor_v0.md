# Omega Decision Floor v0

Status: research note / formal specification / thin Lean scaffold
Scope: presentation-sound decision licensing under declared continuation constraints
Claim boundary: not a complete decision theory, not value, not agency, not identity, not moral standing, not probability-aware risk handling, not Omega validation

## One-Screen Summary

ODT0 is the decision-theoretic consumer of the current map-integrity stack. It
does not rank actions. It licenses or refuses justification routes.

An action is licensed at a decision site only when:

```text
G1. The justifying fact routes through a certified presentation or route,
    and the fact reflects: abstract truth implies concrete truth.

G2. Under worst-case resolution of nondeterminism, every concrete successor
    remains inside the declared corridor.

G3. Any identification of decision processes used in the justification is
    certified as consequence-inseparable for the declared contexts.
```

Public compression:

```text
First certify the map.
Then preserve the corridor.
Then decide.
```

The floor is intentionally one-sided. It may refuse or withhold license from a
good action when the register lacks a certified route. It should not license an
action using a fabricated abstract fact.

## Decision Structure

A finite possibilistic decision structure is:

```text
D = (X, A, T, K, R)

X : finite state set
A : finite action set
T : subset of X x A x X
K : declared constraint set
R : declared register of targets, facts, presentations, and quotient candidates
```

The Lean scaffold generalizes over finite/infinite carriers, but ODT0 is meant
as a finite possibilistic floor. Stochastic and risk-aware variants are later
layers.

The decision site is a state where available actions induce different declared
continuation surfaces. No agent, self, valuer, or identity claim is assumed.

## Corridor

The intended corridor is the controlled viability kernel of the declared
constraint set:

```text
Corr(D) = greatest S subset K such that
          every x in S admits an action a with T(x,a) nonempty
          and all y in T(x,a) remain in S.
```

ODT0 uses demonic nondeterminism: all successors count. An action passes Gate
G2 only when:

```text
forall y, T(x,a,y) -> Corr(y).
```

The Lean file deliberately treats `Corr` as an already-certified predicate.
That avoids duplicating the fixed-point layer inside the decision scaffold.
Instantiating `Corr` with an actual controlled viability kernel is the next
robust-continuation bridge, not part of the thin ODT0 wrapper.

Corridor permanence requires the usual finite/demonic assumption: outside the
greatest controlled invariant set, no memoryless worst-case policy can guarantee
indefinite preservation of `K`. Stronger planning models should restate this
with their own policy class.

## Register

The register contains only declared and retained decision-useful surfaces:

```text
Targets:
  declared goal / constraint predicates.

Phi:
  declared consequence contexts and fact language.

Q:
  declared presentations or certified routes.

N:
  declared quotient / decision-process identification candidates.
```

Registry-first discipline matters. Nothing outside the register participates in
licensing. If the register lacks a certified route, the honest output is
`UNDETERMINED`, not `LICENSED`.

## Certified Justification

A certified justification has two facts and one direction:

```text
abstractFact : fact asserted on a registered presentation
concreteFact : fact needed in the concrete decision structure
reflects     : abstractFact -> concreteFact
```

Reflection is the load-bearing clause. Preservation in the opposite direction
is useful for completeness, but not enough for decision use. A license cannot
rest on an abstract fact unless that fact reflects to the concrete structure.

Lean file:

```text
formal/lean/OmegaProper/Decision/License.lean
```

Main names:

```text
CertifiedJustification
CertifiedJustification.concrete_holds
no_reflected_fact_of_abstract_true_concrete_false
```

This is the formal shape of "no license from phantoms" for declared reflected
facts.

## Licensing Relation

ODT0's thin Lean relation is:

```text
LicenseVia D Corr Available quotientOK x a
```

with fields:

```text
justification:
  a certified justification.

route_available:
  the justification is present in the current register.

enabled:
  the concrete action has at least one successor.

corridor_safe:
  every concrete successor lies in Corr.

quotients_certified:
  the quotient/identification side condition holds.
```

This is intentionally a certificate object, not a statement that the action is
optimal, uniquely recommended, morally right, agentic, or value-preserving.

## Plan License

Local licenses do not automatically glue into a global plan. ODT0 therefore
uses a transported-successor plan license:

```text
PlanLicense D Corr Available quotientOK x [a1, a2, ...]
```

The cons rule says:

```text
LicenseVia D Corr Available quotientOK x a
and for every successor y of x under a,
PlanLicense D Corr Available quotientOK y rest.
```

This is the conservative anti-slicing rule. The tail is checked on every
post-action successor surface, not on a stale initial surface.

Lean names:

```text
PlanLicense
PlanLicense.head_license
PlanLicense.successor_tail
PlanLicense.head_successor_in_corridor
planLicense_cons
```

Contextual branch obstruction and no-global-section behavior remain richer
future work. ODT0 only records sequential stability under explicit transported
successor checks.

## Quotient Discipline

Process or decision-node identification is licensed only when the candidate
nodes are inseparable by the declared contexts:

```text
Inseparable Phi Separates p p'
  := forall c, Phi(c) -> not Separates(c,p,p')
```

Adding contexts makes inseparability harder to satisfy. This is the FDT/Newcomb
repair in floor form: "same for decision purposes" means certified
consequence-inseparability, not same code, same output, same correlation, or
same proxy class.

Lean names:

```text
Inseparable
inseparable_of_contexts_subset
inseparable_expanded_implies_old
```

Example:

```text
formal/lean/OmegaProper/Decision/Examples.lean
```

The example proves a quotient can be valid under an old context register and
revoked by adding a separating context.

## Theorem Spine

### T1. Justification Soundness

If a certified abstract fact holds, the concrete fact holds.

```text
CertifiedJustification.concrete_holds
LicenseVia.concrete_justification
```

Contrapositive reading: a true abstract fact with false concrete content cannot
be reflected. Any presentation that would use such a fact for licensing fails
Gate G1.

### T2. Quotient Soundness

If an admissible declared context separates two process candidates, they cannot
be identified under `Inseparable`.

This is immediate from the definition. The retained example shows register
expansion can revoke a previously valid identification.

### T3. Sequential Stability

A licensed head action plus licensed tails on every concrete successor yields a
licensed plan certificate.

```text
planLicense_cons
PlanLicense.successor_tail
PlanLicense.head_successor_in_corridor
```

The important point is not that local licenses always glue. The point is that
ODT0's plan license makes the gluing obligation explicit.

### T4. Hidden Future Inadmissibility

The intended lifted construction is:

```text
X_hat = X x register-status
T_hat = T restricted to licensed moves
K_hat = states where some licensed action remains available
```

Then "this action predictably forces all future choice through unsound
presentation or empty license" becomes an ordinary corridor-exit claim in the
lifted system.

This remains document-level in v0. It should be formalized when the robust
continuation kernel bridge is opened.

### T5. Safety Asymmetry

Sound direction:

```text
LICENSED ->
  the cited justifying fact holds concretely
  and every concrete successor remains in Corr.
```

Incompleteness is intended. A concretely fine action can remain
`UNDETERMINED` if no certified route exists in the register.

### T6. Register Monotonicity

With the context register fixed, adding certified routes is monotone:

```text
licenseVia_mono_routes
```

Adding consequence contexts is anti-monotone for quotient identifications:
inseparability under the expanded register implies inseparability under the old
register, but not conversely.

Important correction: adding `Phi` can also revoke presentation certifications
and any license depending on them. Only route addition at fixed `Phi` is
license-monotone.

## Verdicts

The intended implementation verdicts are:

```text
LICENSED:
  all gates pass through the declared register.

REJECTED(gate, witness):
  a gate fails with a retained witness.

UNDETERMINED(missing):
  no certified route exists in the register.

NO-LICENSED-ACTION:
  no action, including declared inaction if present, is licensed.

LOCALLY-LICENSED, GLOBALLY-OBSTRUCTED:
  local licenses exist, but transported surfaces or contextual branches fail
  to glue.
```

The current Lean pass formalizes the core license and plan-certificate spine,
not the full verdict datatype.

## Worked Micro-Examples

### Phantom Licensing Refused

If:

```text
abstractFact = True
concreteFact = False
```

then:

```text
not (abstractFact -> concreteFact)
```

So the route cannot be a `CertifiedJustification`. This is the thin wrapper
around the lower phantom-reachability and reflection discipline.

### Register Expansion Revokes Identification

The example file has two contexts:

```text
old:
  does not separate p and q.

new:
  separates p and q.
```

Under the old register, `p` and `q` are inseparable. Under the expanded
register, they are not. This is the quotient side of ODT0's governance story.

### Plan Slicing

ODT0 refuses stale-surface slicing by definition. A plan certificate for
`a :: rest` requires a tail certificate for every concrete successor of `a`.
If step two only works on the old surface, no `PlanLicense` is produced.

## Existing Repo Map

```text
Certified fact reflection
  -> presentation/reflection/loss-aware stack

Corridor predicate
  -> controlled viability kernel / robust continuation bridge

Quotient inseparability
  -> consequence-separation and sound-quotient stack

Plan transported surfaces
  -> path coherence and contextual future-field obstruction stack

Register monotonicity
  -> governance/audit surface for changing declarations
```

## Open Problems

```text
stochastic corridor:
  risk-aware G2 without smuggling a risk attitude.

stacked presentations:
  reflection composition for q' after q.

defeater logic:
  richer than universal-over-contexts.

plan gluing:
  contextual no-global-section obstruction.

lifted future admissibility:
  formalize the register-status corridor.

ODT1 dominance:
  partial-order dominance over admissible future valuations.

ODT2 arbitration:
  value-bearing tie-breaks, explicitly labeled as value input.

ODT3 tiling:
  successor decision sites remain ODT-compliant under self-modification.
```

## Non-Claims

ODT0 does not define or detect:

```text
value
agency
identity
selfhood
valuerhood
moral standing
Omega
optimal action
unique best action
empirical model validity
probabilistic risk attitude
```

It only says when a declared decision justification is allowed to consume a
certified map and a declared corridor.

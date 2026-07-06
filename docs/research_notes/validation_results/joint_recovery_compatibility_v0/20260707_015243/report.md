# Joint Recovery Compatibility v0 Report

Status: PASS
Verdict: separated
Protocol: `docs/research_notes/omega_theory/joint_recovery_compatibility_protocol_v0.md`

## Candidate Pair

- Left: `compatible_joint_recovery`
- Right: `interfering_joint_recovery`
- Marginal scalar controls equal: True
- Full vector census equal: True
- Pure span equivalent: True
- Span rank separates: False
- Individual recovery profiles equal: True
- Joint recovery separates: True

## Recovery Profiles

- Left joint recovered facts: ['A_recovery_fact', 'B_recovery_fact']
- Right joint recovered facts: ['A_recovery_fact']
- Left joint recovery succeeds: True
- Right joint recovery succeeds: False
- Right missing facts: ['B_recovery_fact']

## Negative Controls

- Same individual and same joint recovery determine this profile: True
- Individual-profile difference is not credited as joint-only: True
- Negative controls pass: True

## Claim Boundary

This is a finite recovery-grounded compatibility report. It does not prove value, standing, agency, plurality theory, moral aggregation, patienthood, population optimum, or Omega validation.

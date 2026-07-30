# Canonical Process Monitors v0 Report

Status: PASS
Verdict: retained
Protocol: `docs/research_notes/omega_v2/canonical_process_monitors_protocol_v0.md`

## Case Results

- PM1_observation_equivariance: True
- PM2_canonical_minimization: True
- PM3_unique_lifting: True
- PM4_projection_conservation: True
- PM5_direct_emission_control: True
- PM6_property_relative_residue: True
- PM7_symmetric_copy_unresolved: True
- PM8_family_classification: True

## Canonical Property Monitor

- Compact presentation states: 5
- Redundant presentation states: 6
- Minimal state counts: 5/5
- Canonical payloads equal: True

## Passive Lift

- Reachable lifted states: 7
- Lifted edges: 10
- Unique step-lift failures: 0
- Unique path lifting: True
- Projection-conservation failures: 0

The elementary result is the formal contract. Categorically, the monitor is a finite-set functor on the concrete path category, the lift is its category of elements, and projection has the discrete-opfibration unique-lifting property.

## Property-Relative Residues

### ancestry_match

- History residue: True
- Corridor residue: True
- Left admissible action classes: ['choose_alpha']
- Right admissible action classes: ['choose_beta']

### completion

- History residue: False
- Corridor residue: False
- Left admissible action classes: ['choose_alpha', 'choose_beta']
- Right admissible action classes: ['choose_alpha', 'choose_beta']

### fixed_hazard

- History residue: False
- Corridor residue: False
- Left admissible action classes: ['choose_alpha']
- Right admissible action classes: ['choose_alpha']

- Family classification: family-dependent
- Family-core history residue: False
- Family-core corridor residue: False

## Negative Controls

- Direct emitted-label difference excluded: True
- Symmetric copy observation equal: True
- Symmetric copy monitor state equal: True
- Symmetric copy verdict: unresolved

## Evidence Classification

Unique lifting, minimization, projection conservation, direct-label exclusion, and the symmetric-copy result are instrument controls.

The per-property residue vector and family classification are the risky finite result. They remain relative to the declared property automata.

## Claim Boundary

This pilot does not prove identity, selfhood, consciousness, will, agency, valuerhood, standing, patienthood, intrinsic continuation relevance, moral license, or Omega validation.

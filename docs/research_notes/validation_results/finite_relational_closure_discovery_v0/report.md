# Finite Relational Closure Discovery v0

Status: PASS

## Headline

- Cases: 136
- Nonconstant-surplus cases: 50
- Collapse cases: 86
- Every family has positive and collapse controls: True

## Family Breakdown

| family | cases | nonconstant surplus | collapse | inconsistent seed |
| --- | ---: | ---: | ---: | ---: |
| predicate_seed_partition_sweep | 8 | 6 | 2 | 0 |
| reachability_seed_graph_sweep | 64 | 32 | 32 | 0 |
| viability_seed_graph_sweep | 64 | 12 | 52 | 0 |

## Claim Boundary

This is generated finite closure discovery over small adapter substrates. It does not predeclare expected surplus facts. It does not prove global invariance, agency, value, Omega, or empirical model validity.

## Representatives

### predicate_seed_partition_sweep

Enumerates all Boolean seed predicates over three states and asks which generated target facts and visible pairs survive every admissible presentation.

- `predicate_seed_s0`: nonconstant_surplus; admissible presentations 2; surplus target facts pred:{s1,s2}
- `predicate_seed_empty`: collapse; admissible presentations 5; surplus target facts none

### reachability_seed_graph_sweep

Enumerates loop-free directed graphs on three states, derives the can-reach-goal predicate, and computes generated-universe closure without expected surplus annotations.

- `reachability_seed_00`: nonconstant_surplus; admissible presentations 2; surplus target facts pred:{a,b}
- `reachability_seed_09`: collapse; admissible presentations 5; surplus target facts none

### viability_seed_graph_sweep

Enumerates loop-free directed graphs on three states, derives the finite viability kernel under all-safe states, and computes generated-universe closure without expected surplus annotations.

- `viability_seed_08`: nonconstant_surplus; admissible presentations 2; surplus target facts pred:{c}
- `viability_seed_00`: collapse; admissible presentations 5; surplus target facts none

# Finite Relational Closure Discovery v2

Status: PASS

## Headline

- Cases: 132
- Dynamic-surplus cases: 101
- Unclassified dynamic-profile cases: 36
- Collapse cases: 31
- Constant control collapsed: True

## Family Breakdown

| family | cases | dynamic surplus | unclassified dynamic profile | collapse |
| --- | ---: | ---: | ---: | ---: |
| step_lifting_seed_graph_sweep | 64 | 62 | 36 | 2 |
| observed_word_seed_graph_sweep | 64 | 39 | 0 | 25 |
| constant_seed_control | 4 | 0 | 0 | 4 |

## Read

Closure v2 broadens the generated fact universe from Boolean predicates and visible pairs to dynamic profiles and structural process-coherence facts. It reports seed-determined profile surplus, seed-forced structural surplus, and dynamic profile surplus not determined by seed profiles.

This is not a canonical implication basis. It is a generated finite pilot used to decide whether richer fact languages can produce nontrivial closure behavior before stronger theorem claims are attempted.

## Representatives

### step_lifting_seed_graph_sweep

Enumerates loop-free directed graphs on three states, admits presentations satisfying representative-wise step lifting, and asks which richer dynamic facts are forced.

- `step_lifting_seed_01`: unclassified_dynamic_profile_surplus; admissible presentations 2; dynamic surplus profile:safe_prefix_count:h=1, struct:path_lifting:h=1, struct:path_lifting:h=2, struct:path_lifting:h=3; unclassified dynamic profiles profile:safe_prefix_count:h=1
- `step_lifting_seed_00`: collapse; admissible presentations 5; dynamic surplus none; unclassified dynamic profiles none

### observed_word_seed_graph_sweep

Enumerates loop-free directed graphs on three states, admits presentations respecting the horizon-1 observed extendable word profile, and computes closure over reachability, viability, path-count, and observed-language profiles.

- `observed_word_seed_08`: dynamic_surplus; admissible presentations 2; dynamic surplus profile:extendable_safe_prefix_count:h=1, profile:observed_words:goal_status:h=2, profile:reach:goal, profile:safe_prefix_count:h=1, profile:safe_prefix_count:h=2, profile:viability:safe_all, struct:path_lifting:h=1, struct:path_lifting:h=2, struct:path_lifting:h=3, struct:step_lifting; unclassified dynamic profiles none
- `observed_word_seed_00`: collapse; admissible presentations 5; dynamic surplus none; unclassified dynamic profiles none

### constant_seed_control

Control family using only the constant profile as seed. It checks that richer fact generation does not by itself license dynamic closure without admissibility pressure.

- `constant_control_00`: collapse; admissible presentations 5; dynamic surplus none; unclassified dynamic profiles none

## Claim Boundary

Closure v2 is finite, generated, and adapter-relative. It does not establish global invariance, natural admissibility, agency, identity, value, valuerhood, moral standing, or Omega validation.

# Bounded continuation graph audit follow-up report v0

Date: 2026-09-29. Status: retained instrument audit.

The new controls close three coverage gaps. The current predictors pass without
changing their semantics. The expanded panel contains 27 cases and passes all
379 gates; a separate invalid-interface input checks four public entry points.

- [Contract](continuation_audit_followup_protocol_v0.md), committed at `4081c5d`
  before implementation.
- Implementation: `870e02d`.
- [Retained evidence and checks](../validation_results/continuation_equivalence_audit_v0/20260929_followup/).
- [Deliberate-fault records](../validation_results/continuation_equivalence_audit_v0/20260929_followup/mutation_audit.json).

## Results

| Addition | Correct result | Fault exposed |
| --- | --- | --- |
| Bit erased from world state, retained only in controller memory, then cleared after acting | Input 0 guesses 0; input 1 guesses 1, both certainly | Suffix caching that omits memory; acting from updated memory |
| Cheap input first, expensive input second, budget 1 | Reject the whole program with worst cost 2 | Checking only the first input for budget violations |
| Controller and declared observation maps disagree | Both graph builders and both direct predictors reject the fixture | Skipping shared-interface validation |

The memory-cache mutation passed all 63 previous focused tests during review at
`74a0bdc`. The new fixture catches it. This establishes an earlier test gap, not
an earlier production bug. All four newly retained mutations fail named gates
and exit with code 1. Their exact recipes and every failing gate are retained;
full failed-run files remain in ignored local output and are reproducible by
the mutation tests. Previous five-mutation evidence remains unchanged.

The focused continuation and frame suites now pass 69 tests. The full suite,
including the new recovery panel, passes 727 tests. Counts overlap. Focused Ruff
and whitespace checks pass. Evidence sources were committed before collection;
source-specific git status is clean in provenance.json.

## Naming and scope

Current prose calls the representation the **bounded continuation graph (BCG)**.
Historical C1 labels, APIs and JSON keys remain stable. They do not identify the
primer's conjecture C1. Earlier reports and protocols are historical records;
their old test counts and proposed next steps have not been rewritten.

The graph remains a standard bounded probabilistic quotient. These additions
establish no new semantics or speed advantage. The next research priority is
the [recovery dynamics panel](recovery_dynamics_report_v0.md). The generated
workload/speed benchmark remains unrun and is deferred as optional engineering.

Reproduce in a fresh output directory:

```powershell
python -m omega_v2.validation.continuation_equivalence_audit_v0
python -m pytest -q tests/test_continuation_equivalence_audit.py tests/test_frame_information_audit.py
```

The retained JSON encoding is unchanged; new evidence uses one complete case
per line to keep diffs compact. Historical pretty-printed artifacts are intact.

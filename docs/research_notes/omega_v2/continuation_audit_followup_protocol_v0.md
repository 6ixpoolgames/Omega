# Bounded continuation graph audit follow-up: protocol v0

Date: 2026-09-29. Status: contract committed before implementation.

This extends the public known-answer audit. Historical protocols, reports and
retained runs remain unchanged. The current documentation calls the representation
the **bounded continuation graph (BCG)**. Historical `C1`, `build_c1`, artifact
keys and command names retain their meaning for reproducibility. This graph name
does not denote the primer's generativity-universality conjecture C1.

## Registered additions

1. Erase an initially observed input bit from world state before the guess. Only
   controller memory retains it. The controller uses that memory to act, then
   clears it. Inputs 0 and 1 must yield guesses 0 and 1 with probability one in
   the full evaluator, BCG, conventional quotient and memoized predictor.
2. Add the two-input cost fixture at budget 1 to the retained panel: input cheap
   costs 1, input dear costs 2, in that order. Every predictor must reject the
   sole whole program with worst cost 2. No input is dropped.
3. Record rejection of a controller observation map incompatible with the
   shared interface for both graph builders and both direct predictors.

## Mutation requirements

The retained runner must fail when the memoized suffix cache omits memory,
when graph actions use newly updated rather than current memory, when admission
checks only the first input, or when shared-interface validation is skipped.
Mutations are applied in memory; source files and historical evidence are not
edited. Retain gate names, nonzero runner exit codes and source provenance.

The memory-cache mutant passed all 63 existing focused tests during review;
the new fixture must expose it. These are instrument checks, not independent
evidence about recovery or the theory. Use a fresh artifact directory.

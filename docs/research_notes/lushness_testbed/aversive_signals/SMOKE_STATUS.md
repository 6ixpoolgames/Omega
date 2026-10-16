# W1/W2 engineering smoke — 14 October 2026

Status: passed. Scientific protocol remains unfrozen; no kills or arm rankings
were scored. W3 signal optimization and W4 domination are not implemented.

The final frozen smoke `smoke-20261013T231633Z-c7d741` covered all eight arms,
204 physical states per arm, cadence 0.25, short-prefix entropy checks and
four-unit readout feasibility. Every arm closed generator mass and physical
energy, had a valid sampled kernel, matched exact short observed histories
within its conditioning bounds, and satisfied destination-chain entropy closure.
Residuals were below 1e-12. Signal qualification remains unscored.

- Wall time: 1.305 seconds, against a 90-second cap.
- Peak job memory: 131,002,368 bytes (124.9 MiB), against 512 MiB.
- Output including frozen sources: 456,079 bytes, against 8 MiB.
- Frozen input hash: `ef62c3b334340c74399b7025401ceb1a7e88444da8ba3bb72a60490c31efabd7`.
- Exit code zero, no cap hit.
- 16 new focused tests pass; 39 tests pass including feedback/composition checks.
- Static checks pass for every new source, runner and test file.

The first packaging attempt omitted the existing hard-cap helper from its
snapshot and stopped before launching a worker. The manifest list was corrected;
both subsequent capped smokes passed. The final run reflects the final source
and explicit engineering parameters in PROTOCOL_DRAFT.json.

Next deliverable is a scientific freeze: physical cost anchors, exact T/D
definitions and suffering index, tolerance, roots, grid, kill rules and budget.
Merged-signal bounds can leave comparisons unresolved; that is an instrument
limit rather than evidence of a tie. No physiology was chosen using kill scores.

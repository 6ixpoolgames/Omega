# Execution incident: 15 October 2026

The first M8/cost1.5/packet4/damage0.02 attempt stopped before producing results.
The cap supervisor counted output files while Python atomically renamed a
temporary bytecode-cache file. That file disappeared between the existence
check and size read, raising FileNotFoundError. The supervisor's finally block
terminated its child and closed the kill-on-close job. No RESULTS.json existed.

The remaining batch was resumed with PYTHONDONTWRITEBYTECODE=1 inherited by the
worker. This suppresses cache-file writes, not any physical transition or
scientific query. Model, worker, protocol and source hashes were unchanged;
completed laws were not rerun. The failed snapshot remains retained locally:
science-M8-c1.5-y4-d0.02-20261014T170605Z-f69f61. No successful outcome was
discarded and no parameters were selected using the partial results.

# Reproduction and measurement scope

The existing capped workflow freezes the imported numerical source and exact
configuration, verifies output hashes and preserves compact records. Old studies
are not overwritten. Run in the Omega repository's Python environment:

```
.venv/Scripts/python.exe -m pytest tests/test_exchange_controls.py -q
.venv/Scripts/python.exe scripts/run_continuation_controls.py steering-smoke --jobs 1
.venv/Scripts/python.exe scripts/run_continuation_controls.py calibration --jobs 1
.venv/Scripts/python.exe scripts/run_continuation_controls.py flow-smoke --jobs 1
.venv/Scripts/python.exe scripts/run_continuation_controls.py steering-map --jobs 1
.venv/Scripts/python.exe scripts/run_continuation_controls.py flow-map --jobs 1
.venv/Scripts/python.exe scripts/report_continuation_controls.py steering
.venv/Scripts/python.exe scripts/report_continuation_controls.py flow
.venv/Scripts/python.exe scripts/plot_continuation_controls.py
```

The two map commands can run concurrently with one worker each. A successful
calibration is required before flow execution, and smokes precede maps. Commands
use current source; historical reproduction uses the archived source bytes and
receipt configurations. Physical source, driver and workers are included in
the snapshots. Per-study cases/receipts preserve hashes; calibration, smokes
and map identities remain separate. Missing/corrupt small query checkpoints
are recomputed. No dense transition kernel is retained.

Flow calibration fits physical F+R/F−R, not entropy or an ethical outcome. It
reported a common turnover range [0.0420754460,17.5902313987] events through T256
and selected 4.4291144342 and 13.2031924106. Its independent template/native
compiler bridge error was 1.78e-15. The two zero-net fits had net residuals below
2e-12 events; actual scientific runs recheck them. Calibration took 170 seconds
and peaked around 2.28 GiB under the 3 GiB cap. This measured cost matters for
future larger calibrations; it should not be described as negligible.

Transfer source/affinity work is counted in the first law. No equal-work,
equal-total-world-event or finite-window match outside T256 is implied. A
projected D/S history remains non-Markov: use the bounds and retain unresolved
signs. Time-resolution audits cover three declared clocks, not every physical
grain. Source archives contain code only. No cleanup or publication is performed.

# Reproducing the extraction slice

Use the repository's Python environment. Commands below create capped child
processes from immutable source/configuration bundles:

```
.venv/Scripts/python.exe -m pytest tests/test_resource_transfer.py -q
.venv/Scripts/python.exe scripts/run_resource_transfer.py smoke --seconds 300
.venv/Scripts/python.exe scripts/run_resource_transfer.py survey --jobs 2 --seconds 300 --budget 3600
.venv/Scripts/python.exe scripts/report_resource_transfer.py
```

Current commands use current source. Completed cases are reused only when the
source/configuration identity and output checksum match. To reproduce historical
results, use the original source bytes in source_archives and the exact frozen
configuration from the relevant receipt. Source snapshots include the entire
imported testbed and capped worker; compact results do not depend on a saved
dense kernel. The manifest verifies imports remain in that source snapshot.

Each process tree is limited to 300 seconds, 3 GiB and 32 MiB of output. The
coordinator permits at most two workers, checks a 2 GiB retained-data budget and
4 GiB disk reserve, and stops queued work after a numerical/resource failure.
Local caches contain small verified entropy-row blocks, not physical states or
saved kernels. Missing or corrupt blocks are recomputed.

The first smoke before stationary/owned-energy readouts was also successful;
its separate source remains recoverable. The current smoke repeats the check
with those additional ledger validations. No scientific scores were replaced
under an existing source identity.

Retain specifications, source archives, configurations, receipts and compact
signed maps. Large reconstructable outputs remain under the ignored
results/local_runs/lushness_testbed/resource_transfer folder. No cleanup,
commit, push or Drive upload is performed by these commands.

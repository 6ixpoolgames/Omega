"""Resume unchanged recorded physics, with Windows progress-write retries.

This wrapper changes coordinator I/O only. It does not enter a worker snapshot,
modify a physical or numerical model, or alter existing cache identities.
"""
from time import sleep

import run_domination_stage_a as batch

original_atomic_json = batch.atomic_json


def retry_atomic_json(path, value):
    for attempt in range(12):
        try:
            return original_atomic_json(path, value)
        except PermissionError:
            if attempt == 11:
                raise
            sleep(.05*(attempt+1))


if __name__ == '__main__':
    batch.atomic_json = retry_atomic_json
    raise SystemExit(batch.execute(batch.make_plan()['cases'], 'survey', jobs=6,
                                   budget_seconds=18000, output_budget=1024*1024**2))

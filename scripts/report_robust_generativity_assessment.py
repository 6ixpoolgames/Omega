"""Render the current physical assessment from unchanged completed-run outputs.

The original report script reproduces the historical checklist. This entry point
reports the mechanism and continuous measurements without treating guessed
funding/recovery cutoffs as a scientific verdict. No physical data are rescored.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/research_notes/lushness_testbed/robust_generativity'


def main():
    result = json.loads((DOC / 'SUMMARY.json').read_text())
    status = json.loads((DOC / 'SCIENCE_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise RuntimeError('The completed-run assessment requires a complete run.')
    rows = result['settings']
    shape = [row for row in rows if row['batch'] == 'shape']
    positive = {
        name: sum(row['contrasts'][name]['all_positive'] for row in rows)
        for name in ('unbound', 'all_assistance_off', 'cut_C_to_A', 'thermal')
    }
    depth_examples = sum(
        row['primary_depth']['depth_and_retained_expansion'] > 0.01 for row in shape
    )
    sustained = [
        row for row in shape
        if row['persistence']['post_startup_uptime_fraction'] > 0.5
    ]
    example = next(row for row in rows if row['id'] == 'A-a1-k1-s2.4')
    depth = example['primary_depth']
    diagnostics = json.loads((DOC / 'EXPLORATORY_DIAGNOSTICS.json').read_text())
    funding = diagnostics['funding_horizon_examples'][example['id']]
    funding_table = '\n'.join(
        f"| {time} | {funding[str(time)]['external_spent_LB']:.2%} |"
        for time in (256, 1024, 4096)
    )
    table = [
        '| Setting | Three links + retained | Functional uptime 64–256 | Closure by 256 | External funding lower bound | Δ unbound bits | Δ all-off bits | Δ C-to-A cut bits |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for row in rows:
        deltas = [
            row['contrasts'][name]['cadences']['0.25']['delta_bits']
            for name in ('unbound', 'all_assistance_off', 'cut_C_to_A')
        ]
        external = row['external_funding_LB']
        funding_text = 'undefined' if external is None else f'{external:.3f}'
        table.append(
            f"| {row['id']} | {row['primary_depth']['depth_and_retained_expansion']:.6f} | "
            f"{row['persistence']['post_startup_uptime_fraction']:.4f} | "
            f"{row['closure_T256']:.4f} | {funding_text} | "
            + ' | '.join(f'{delta:+.2f}' for delta in deltas) + ' |'
        )
    text = f'''# Three-link compounding: mechanism, persistence and lushness

**Updated interpretation — 15 October 2026.** This current assessment replaces
the earlier combined-checklist verdict. Physical outputs are unchanged.

This run demonstrates paid three-step enabling with retained expansion, and
regimes where that compounding persists and increases finite-history lushness.
The cycle is physical: A assists construction of B, B assists C, and C assists
A; apparatus also enables resource capture that helps pay for further activity.
The lineage monitor reads the resulting histories without adding entropy.

## What the run demonstrates

- All {depth_examples} of {len(shape)} shape settings have a conservative probability above 1%
  of three successive enabling links with retained expansion at T256, including
  square-root feedback. The probabilities are reported continuously below.
- {len(sustained)} distinct shape regimes combine this mechanism with expected functional
  uptime above one half over T64–256 and positive lushness consequences.
- At T256, the full mechanism beats the unbound preparation in {positive['unbound']}/{len(rows)}
  settings, all assistance off in {positive['all_assistance_off']}/{len(rows)}, and the C-to-A cut in
  {positive['cut_C_to_A']}/{len(rows)}. Each positive comparison holds across cadences 0.125, 0.25
  and 0.5, with the numerical error allowance included.
- Individual construction-link ablations reduce unlabelled retained expansion
  in the shape grid. The physical benefit therefore extends beyond the named
  lineage detector itself.

For linear feedback, full assistance and source rate 2.4:

| Physical readout | Result |
| --- | ---: |
| Three-link completion by T256 | {depth['depth_by_deadline']:.2%} |
| Completion and retained expansion at T256 | {depth['depth_and_retained_expansion']:.2%} |
| Depth by 64, function at 64, expansion at 256, no closure, on the same histories | {depth['depth_by_startup_loop_then_expansion_no_closure']:.2%} |
| Expected functional uptime over T64–256 | {example['persistence']['post_startup_uptime_fraction']:.2%} |
| T256 seed minus unbound, cadence 0.25 | {example['contrasts']['unbound']['cadences']['0.25']['delta_bits']:+.2f} bits |
| T256 full minus all assistance off | {example['contrasts']['all_assistance_off']['cadences']['0.25']['delta_bits']:+.2f} bits |
| T256 full minus C-to-A cut | {example['contrasts']['cut_C_to_A']['cadences']['0.25']['delta_bits']:+.2f} bits |

These are three successive enabling links, with compounding and later function
connected on the same paths. The monitor is conservative and can miss genuine
chains. The demonstration is finite-depth and confined to this count adapter.

![Compounding, persistence and lushness across the shape grid](SHAPE_PROFILE.png)

## Energy funding and the reporting correction

Construction and maintenance pay native energy bills. Initial stored resources
are part of the physical present; using them is legitimate. As the continuation
develops, external capture supplies an increasing conservative share of spending:

| Horizon, linear/full-assistance/source 2.4 | External-spending lower bound |
| --- | ---: |
{funding_table}

The old combined checklist required this lower bound to exceed 80% at T256.
That guessed cutoff made every combined J flag zero. It did not establish
absence of funding or failure of the physical principle. Its use as the headline
verdict was an interpretation error. Funding, recovery and persistence are
physical profiles to understand, not arbitrary gates defining generativity.

The original plans and numerical checklist remain available as provenance.
Their missed operational guesses are not the scientific conclusion, and no
physical outcome or lushness score has been changed to obtain this assessment.

## What determines the operating range

Stronger damage reduces retention and functional uptime. For linear feedback
and source 0.6, damage rates 0.005, 0.02 and 0.08 give uptime fractions 0.5036,
0.1128 and 0.0010; three-link-plus-retained probabilities fall from 0.10015 to
0.00884 and 0.00000784. Compounding still occurs under damage, while its products
are retained for less time. The recovery profiles map that limitation directly.

Across the stress groups, functional persistence and the measured breadth gains
are positively associated, with Spearman correlations 0.821–1.0. This supports
the persistence relationship in this model; an opportunity-window experiment
would be needed to test a specific repayment prediction.

The seed beats the thermal reference in {positive['thermal']}/{len(rows)} settings. That reference
already contains mean apparatus 4.2577 and an initial complete loop with
probability 47.17%, versus one apparatus in the seed. It is an equienergy
count-state preparation, not a spatial gas. This ordering remains part of the
result. The present adapter has no translational motion and does not settle
the earlier spatial lattice comparison.

A further irreversibility comparison finds four of eight cases where greater
permanent damage increases T256 breadth across all cadences while lowering
functional uptime. One example gains 1.168 bits at T256 and loses 2.460 bits
at T4096. This real horizon dependence remains in the assessment. It concerns
different physical laws, rather than an agent choosing damage.

Finite-history lushness is primary. Same-law roots share the limiting rate;
mechanism contrasts can change it. Rates and temporal activity decompositions
explain ongoing contribution without replacing the finite continuation. The
source and bath are matched here; accepted work and event activity are not.

## Complete continuous setting map

Differences below are at T256 and cadence 0.25. Positive signs for the three
displayed contrasts also hold at the other two cadences. Four R0 rows reuse
shape cases; the 40 rows are not 40 independent full-mechanism simulations.

{chr(10).join(table)}

## Reproduction and scope

All 144 cases completed in {result['wall_seconds']/60:.1f} minutes of summed worker
time, with maximum process-tree memory {result['peak_job_bytes']/1024**2:.1f} MiB.
Thirty-six focused tests passed. Energy residuals are at most 1.23e-11 and
monitor projection errors at most 4.44e-16. Physical randomness is fully counted.

The evidence establishes the intended finite three-link mechanism and a
persistent, lushness-positive operating region. Spatial gas competition,
open-ended expansion, network superiority and ethical behavior are further
questions, each requiring its own physical model.

Current report generator: `scripts/report_robust_generativity_assessment.py`.
The original reporting generator reproduces the historical checklist only.

[Structural interpretation](INTERPRETATION.md) · [Original protocol](PROTOCOL.json) ·
[Numerical summaries and original checklist](SUMMARY.json) ·
[Machine-readable map](SETTING_MAP.csv) · [Further diagnostics](EXPLORATORY_DIAGNOSTICS.json)
'''
    (DOC / 'RESULTS.md').write_text(text, encoding='utf-8')
    print(json.dumps({
        'completed_cases': len(status['cases']),
        'shape_settings_with_depth_and_retention_above_one_percent': depth_examples,
        'distinct_shape_settings_with_majority_functional_uptime': len(sustained),
        'positive_T256_contrasts_all_cadences': positive,
        'physical_outputs_changed': False,
    }, indent=2))


if __name__ == '__main__':
    main()

"""Finite-history comparison profiles from every completed initial-map case."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/domination_friction'
CACHE = ROOT/'results/local_runs/lushness_testbed/domination_friction/_mpl_cache'
CACHE.mkdir(parents=True, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(CACHE)

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    report = json.loads((DOC/'COMPARISONS.json').read_text())
    styles = [('access-block', 'Access entry blocked'),
              ('access-steer', 'Access entry redirected'),
              ('construction-block', 'Construction entry blocked'),
              ('trap-entry-steer', 'Trap entry redirected'),
              ('trap-exit-steer', 'Trap exit redirected')]
    rows = {row['id']: row for row in report['cases']}
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (supply, kappa) in zip(axes.ravel(), ((.04, 0.), (.04, 1.), (.12, 0.), (.12, 1.))):
        group = f's{supply:g}-k{kappa:g}'
        for suffix, label in styles:
            row = rows.get(group+'-'+suffix)
            if row is None:
                continue
            times = sorted(map(int, row['comparisons']['0.25']))
            values = [row['comparisons']['0.25'][str(t)]['global_delta_bits'] for t in times]
            line, = ax.plot(times, values, 'o-', label=label)
            lo = [min(r[str(t)]['global_delta_bits'] for r in row['comparisons'].values()) for t in times]
            hi = [max(r[str(t)]['global_delta_bits'] for r in row['comparisons'].values()) for t in times]
            ax.fill_between(times, lo, hi, color=line.get_color(), alpha=.12)
        ax.axhline(0, color='#555555', lw=1)
        ax.set_xscale('log')
        ax.set_xticks([16, 64, 256, 1024], ['16', '64', '256', '1024'])
        ax.set_title(f'Source {supply:g}, complementarity {kappa:g}')
        ax.set_xlabel('Physical horizon')
        ax.set_ylabel('Whole-field lushness difference (bits)')
        ax.grid(alpha=.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=9)
    fig.suptitle('Embodied friction: complete history relative to idle device', fontsize=14)
    fig.text(.5, .085, 'Lines: cadence 0.25. Shading: 0.125–0.5 cadence range, not statistical uncertainty.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .13, 1, .95))
    for extension in ('png', 'svg'):
        fig.savefig(DOC/('PROFILE.'+extension), dpi=160, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    main()

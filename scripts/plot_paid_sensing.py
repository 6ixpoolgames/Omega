"""Export conditional-root averages and the declared target temporal profile."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/paid_sensing'
cache = ROOT/'results/local_runs/lushness_testbed/plot_cache'
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(cache))

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    r = json.loads((DOC/'SUMMARY.json').read_text(encoding='utf-8'))
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4), layout='constrained')
    groups = r['pooled']
    positions = np.arange(len(groups))
    for shift, pair, label, color in ((-.18, 'I0-R0', 'No extra motor coupling', '#868990'),
                                     (.18, 'IX-RX', 'Bit drives movement', '#217b91')):
        axes[0].bar(positions+shift, [g['pairs'][pair]['mean_delta_bits'] for g in groups],
                    width=.36, label=label, color=color)
    labels = [f"{g['parameters']['movement_cost']:g} / {g['parameters']['contrast']:g} / {g['sensor']['refresh_rate']:g}"
              for g in groups]
    axes[0].set_xticks(positions, labels, rotation=40, ha='right', fontsize=8)
    axes[0].set_xlabel('Movement bill / supply contrast / read rate')
    axes[0].set_ylabel('Informative − random history entropy (bits)')
    axes[0].set_title('Paid informative versus random writing', fontsize=10)
    axes[0].legend(fontsize=8)
    corridor = [v for v in r['target_corridor'] if v['horizon'] == 64]
    dt = [v['cadence'] for v in corridor]
    axes[1].plot(dt, [v['mean_delta_bits'] for v in corridor], 'o-', color='#217b91', label='Resolved IX − RX')
    axes[1].fill_between(dt, [v['mean_hidden_lower'] for v in corridor],
                         [v['mean_hidden_upper'] for v in corridor], color='#b4773b', alpha=.2,
                         label='Hidden-bit conditioning bounds')
    axes[1].set_xlabel('Sampling cadence (native time units)')
    axes[1].set_ylabel('Conditional two-root mean difference (bits)')
    axes[1].set_title('Target: cheap movement, unequal supply\nSlow paid sensing', fontsize=10)
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.axhline(0, color='#777777', linewidth=.8)
        ax.grid(axis='y', alpha=.15)
    fig.suptitle('Paid sensing · T64\nA benefit over random actuation does not establish actuation beats remaining uncoupled', fontsize=11)
    fig.savefig(DOC/'PAID_INFORMATION.png', dpi=160)
    fig.savefig(DOC/'PAID_INFORMATION.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()

"""Static scientific plot of the complete registered T64 upkeep grid."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'results/local_runs/lushness_testbed/aversive_signals/_mpl_cache'))
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

DOC = ROOT/'docs/research_notes/lushness_testbed/aversive_signals'


def main():
    summary = json.loads((DOC/'REGISTER_CONTROL_SUMMARY.json').read_text(encoding='utf-8'))
    parents = sorted({row['parent'] for row in summary['primary']})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.1), sharey=True)
    for ax, parent in zip(axes, parents):
        for cadence, color in ((.125, '#be651b'), (.25, '#145f9d'), (.5, '#35794f')):
            rows = sorted([row for row in summary['comparisons'] if row['parent'] == parent
                and row['horizon'] == 64 and row['cadence'] == cadence and row['grain'] == 'resolved'
                and row['pair'] == 'B_R-B'], key=lambda row: row['upkeep_ratio'])
            ax.plot([row['upkeep_ratio'] for row in rows], [row['difference_lower'] for row in rows],
                    marker='o', markersize=4, color=color, linewidth=2 if cadence == .25 else 1.2,
                    label=f'cadence {cadence:g}')
        ax.axhline(0, color='#424242', linewidth=.8)
        ax.axvspan(1, 2, color='#dddddd', alpha=.35)
        ax.set_xscale('symlog', linthresh=.05)
        ax.set_xticks([0, .05, .25, 1, 2, 4], ['0', '.05', '.25', '1', '2', '4'])
        ax.set_title(parent)
        ax.set_xlabel('Active-register upkeep / basal metabolic power')
        ax.grid(alpha=.18)
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_ylabel('Neutral flicker minus inactive register (bits)')
    fig.suptitle('Paid neutral flicker has a cost-dependent breadth advantage', fontsize=12)
    fig.text(.5, .025, 'T64; charging is paid even at zero upkeep. Lines connect tested points; shaded band is a crossing bracket.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .06, 1, .94))
    fig.savefig(DOC/'REGISTER_CONTROL_UPKEEP.png', dpi=180)
    fig.savefig(DOC/'REGISTER_CONTROL_UPKEEP.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()

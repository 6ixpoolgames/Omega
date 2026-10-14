"""Export scientific comparisons of breadth with independently tracked function."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/exploration'
cache = ROOT/'results/local_runs/lushness_testbed/plot_cache'
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(cache))

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    result = json.loads((DOC/'SUMMARY.json').read_text(encoding='utf-8'))
    primary = [c for c in result['comparisons'] if c['horizon'] == 64 and c['cadence'] == .25]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout='constrained', sharey=True)
    for pair, color, marker, label in (
            ('B_R-B', '#9757a6', 'o', 'Independent bit − unvarying bit'),
            ('B_X-B_R', '#b65b2a', 'x', 'Blind bit-driven movement − uncoupled bit'),
            ('S_A-B_R', '#22758b', '^', 'Stock-aware movement − uncoupled bit')):
        data = [c for c in primary if c['pair'] == pair]
        for ax, field in zip(axes, ('food_capture', 'lifetime')):
            ax.scatter([c['physical_delta'][field] for c in data], [c['delta_bits'] for c in data],
                       label=label, color=color, marker=marker, alpha=.8, s=42)
    for ax in axes:
        ax.axhline(0, color='#888888', linewidth=.8)
        ax.axvline(0, color='#888888', linewidth=.8)
        ax.grid(alpha=.2)
    axes[0].set_xlabel('Change in captured food (energy units)')
    axes[1].set_xlabel('Change in expected lifetime (time units)')
    axes[0].set_ylabel('Change in complete history entropy (bits)')
    axes[0].legend(loc='upper left', fontsize=7)
    fig.suptitle('Costed exploration · T64, cadence0.25\nBoth initial stocks, supply allocations, costs and coupling strengths', fontsize=11)
    fig.savefig(DOC/'BREADTH_AND_FUNCTION.png', dpi=160)
    fig.savefig(DOC/'BREADTH_AND_FUNCTION.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()

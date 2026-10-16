"""Standalone scientific figure of the exact and asymptotic pair profiles."""
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/temporal_profile'


def main():
    result = json.loads((DOC/'SUMMARY.json').read_text(encoding='utf-8'))
    figure, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True, layout='constrained')
    for column, parent in enumerate(('W1-00', 'W1-08')):
        for row, pair in enumerate((['A', 'B'], ['B_R', 'B'])):
            item = next(c for c in result['comparisons'] if c['parent'] == parent and c['pair'] == pair and c['horizon'] == 64)
            ax = axes[row, column]
            ax.plot([v['cadence'] for v in item['profile']], [v['delta_bits'] for v in item['profile']],
                    'o-', color='#176b90', label='Exact sampled history')
            ax.plot([v['cadence'] for v in item['profile']], [v['estimated_delta_bits'] for v in item['profile']],
                    '--', color='#b96828', label='Two-term asymptotic estimate')
            ax.axhline(0, color='#777777', linewidth=.8)
            for bracket in item['crossing_brackets']:
                cadences = [v['cadence'] for v in bracket['refined']]
                ax.axvline(sum(cadences)/2, color='#666666', linestyle=':', linewidth=1)
            ax.set_xscale('log', base=2)
            ax.grid(alpha=.2)
            ax.set_title(f"{parent}: {' − '.join(pair)}")
            ax.set_ylabel('History entropy difference (bits)')
            if row == 1:
                ax.set_xlabel('Sampling cadence (native time units)')
    axes[0, 0].legend(fontsize=8)
    figure.suptitle('Temporal profile audit · T = 64\nNumerical resolution grid; no physical cutoff selected', fontsize=12)
    figure.savefig(DOC/'TEMPORAL_PROFILE.png', dpi=160)
    figure.savefig(DOC/'TEMPORAL_PROFILE.svg')
    plt.close(figure)


if __name__ == '__main__':
    main()

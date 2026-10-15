"""Scientific figure: exact queried horizon scores, with offset diagnostics."""
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/same_law_gas'
LAW = 'N6-L7-b3-m0.25-native'


def main():
    original = json.loads((DOC/'laws'/(LAW+'.json')).read_text())
    extension = json.loads((DOC/'tails'/(LAW+'.json')).read_text())
    colors = {'thermal': '#236fa1', 'unbound': '#b43b38', 'arrangement': '#288267'}
    labels = {'thermal': 'Thermal mixture', 'unbound': 'Initially unbound', 'arrangement': 'Arrangement only'}
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.8), sharey=True)
    for ax, dt in zip(axes, (.125, .25, .5)):
        for ref, color in colors.items():
            pairs = {r['horizon']: r['delta_bits'] for r in original['contrasts']
                     if r['cadence'] == dt and r['reference'] == ref}
            tails = [r for r in extension['rows'] if r['cadence'] == dt and r['reference'] == ref]
            pairs.update({r['horizon']: r['delta_bits'] for r in tails})
            points = sorted(pairs)
            ax.plot(points, [pairs[t] for t in points], '-o', color=color, linewidth=1.8,
                    markersize=4, label=labels[ref])
            ax.axhline(tails[-1]['delta_offset'], color=color, linestyle=':', linewidth=1., alpha=.75)
        ax.axhline(0, color='#344150', linewidth=1.)
        ax.axvline(64, color='#8995a1', linestyle='--', linewidth=.8)
        ax.set_xscale('log', base=4)
        ax.set_xticks([16, 64, 256, 1024, 4096], labels=['16', '64', '256', '1024', '4096'])
        ax.set_xlabel('Physical horizon')
        ax.set_title(f'Cadence {dt:g}')
        ax.grid(axis='y', color='#e5e9ed', linewidth=.7)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Seed − reference history entropy (bits)')
    axes[0].legend(frameon=False, fontsize=9, loc='lower left')
    fig.suptitle('A seed advantage can reverse as the horizon grows', fontsize=15, y=.98)
    fig.text(.5, .9, 'Six monomers / seven sites · beta 3 · mobility 0.25 · one law for every preparation',
             ha='center', fontsize=10, color='#44515e')
    fig.text(.5, .025, 'Points are exact sampled-history queries; connecting lines guide the eye. Dotted lines show preparation offsets.',
             ha='center', fontsize=9, color='#44515e')
    fig.tight_layout(rect=[.015, .055, .99, .875])
    fig.savefig(DOC/'horizon_profile.png', dpi=160)
    fig.savefig(DOC/'horizon_profile.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()

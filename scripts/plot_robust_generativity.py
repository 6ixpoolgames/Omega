"""Standalone scientific figures from the complete frozen result map."""
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullLocator

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/robust_generativity'


def main():
    result = json.loads((DOC/'SUMMARY.json').read_text())
    rows = result['settings']
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    colors = ['#2368a0', '#be5b19', '#2d8557', '#854b9e']
    for color, (alpha, strength) in zip(colors, ((.5, .1), (.5, 1.), (1., .1), (1., 1.))):
        family = sorted([r for r in rows if r['batch'] == 'shape' and r['alpha'] == alpha
                         and r['strength'] == strength], key=lambda r: r['supply'])
        x = [r['supply'] for r in family]
        label = f'feedback exponent {alpha:g}, assistance ×{strength:g}'
        axes[0, 0].plot(x, [r['primary_depth']['depth_and_retained_expansion'] for r in family],
                        'o-', color=color, label=label)
        axes[0, 1].plot(x, [r['persistence']['post_startup_uptime_fraction'] for r in family], 'o-', color=color)
        for ax, name in ((axes[1, 0], 'unbound'), (axes[1, 1], 'all_assistance_off')):
            values = [[v['delta_bits'] for v in r['contrasts'][name]['cadences'].values()] for r in family]
            y = [r['contrasts'][name]['cadences']['0.25']['delta_bits'] for r in family]
            ax.plot(x, y, 'o-', color=color)
            ax.fill_between(x, [min(v) for v in values], [max(v) for v in values], color=color, alpha=.12)
    for ax in axes[1]:
        ax.axhline(0, color='#555555', lw=1)
    titles = ['Three-link certificate AND retained expansion at T256',
              'Unconditional functional uptime, T64–256',
              'Same-law seed minus unbound preparation',
              'Full cycle minus all assistance off']
    ylabels = ['Probability', 'Expected fraction of window', 'Finite-history difference (bits)',
               'Finite-history difference (bits)']
    for ax, title, ylabel in zip(axes.ravel(), titles, ylabels):
        ax.set_title(title, fontsize=11); ax.set_ylabel(ylabel)
        ax.set_xscale('log'); ax.set_xticks([.15, .6, 2.4], ['0.15', '0.6', '2.4'])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlabel('Offered source rate'); ax.grid(alpha=.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, fontsize=9)
    fig.suptitle('Three-link compounding: physical persistence and lushness consequences', fontsize=13)
    fig.text(.5, .07, 'Breadth curves: cadence 0.25. Shading: range across 0.125, 0.25, 0.5; not statistical uncertainty.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .1, 1, .95))
    for extension in ('png', 'svg'):
        fig.savefig(DOC/('SHAPE_PROFILE.'+extension), dpi=160, facecolor='white')
    plt.close(fig)
    names = ['C', 'C funded', 'R', 'L thermal', 'L unbound', 'L mechanism', 'J mechanism', 'Strong J mechanism']
    matrix = np.array([[r['markers']['C'], r['markers']['C_funded'], r['markers']['R'],
        r['contrasts']['thermal']['all_positive'], r['contrasts']['unbound']['all_positive'],
        r['contrasts']['all_assistance_off']['all_positive'] and r['contrasts']['cut_C_to_A']['all_positive'],
        r['J_mechanism'], r['strong_J_mechanism']] for r in rows], dtype=float)
    from matplotlib.colors import ListedColormap
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.imshow(matrix, aspect='auto', cmap=ListedColormap(['#eeeeee', '#2c8864']), vmin=0, vmax=1)
    ax.set_xticks(range(len(names)), names, rotation=35, ha='right', fontsize=9)
    ax.set_yticks(range(len(rows)), [r['id'] for r in rows], fontsize=8)
    ax.axhline(11.5, color='#222222', lw=1.5)
    ax.set_title('Historical checklist diagnostics — not the scientific verdict', fontsize=12)
    fig.text(.5, .015, 'Green: original cutoff met. Grey: cutoff not met. J columns inherit the guessed 80% funding gate.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .035, 1, 1))
    for extension in ('png', 'svg'):
        fig.savefig(DOC/('JOINT_CRITERIA.'+extension), dpi=150, facecolor='white')
    plt.close(fig)
    print('Saved SHAPE_PROFILE and JOINT_CRITERIA as PNG/SVG')


if __name__ == '__main__':
    main()

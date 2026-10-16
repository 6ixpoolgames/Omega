"""Scientific frontier and retained expansion plots from complete saved maps."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/renewal'
cache = ROOT/'results/local_runs/lushness_testbed/plot_cache'
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(cache))

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    r = json.loads((DOC/'SUMMARY.json').read_text(encoding='utf-8'))
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), layout='constrained')
    for ax, cap, wear, title in ((axes[0, 0], 1, .02, 'Capacity 1 · low thermal turnover'),
                                  (axes[0, 1], 1, .08, 'Capacity 1 · high thermal turnover'),
                                  (axes[1, 0], 2, .02, 'Capacity 2 · bounded construction feedback')):
        for t, color in ((16, '#888888'), (64, '#217e97'), (256, '#bf7b2a'), (1024, '#508052')):
            values = sorted((v for v in r['frontier'] if v['capacity'] == cap and v['wear'] == wear
                             and v['kind'] == 'primary' and v['cadence'] == .25 and v['horizon'] == t),
                            key=lambda v: v['supply'])
            ax.plot([v['supply'] for v in values], [v['delta_bits'] for v in values], 'o-',
                    label=f'T = {t}', color=color)
        ax.axhline(0, color='#777777', linewidth=.8)
        ax.set_xscale('log', base=2)
        ax.set_xlabel('Total packet offer rate')
        ax.set_ylabel('Informed actuation − uncoupled variation (bits)')
        ax.set_title(title, fontsize=11)
        ax.grid(alpha=.2)
    axes[0, 0].legend(fontsize=8)
    ax = axes[1, 1]
    for suffix, label, color in (('', 'Construction assistance γ = 2', '#217e97'),
                               ('-gamma0', 'Kinetic ablation γ = 0', '#bf7b2a')):
        x = [.3, .6, 1.2]
        y = [r['laws'][f'C2-s{s:g}-w0.02'+suffix]['stationary']['IX']['expanded_deadline'] for s in x]
        ax.plot(x, y, 'o-', label=label, color=color)
    ax.set_title('Higher entropy rate, less retained two-unit expansion', fontsize=11)
    ax.set_xlabel('Total packet offer rate')
    ax.set_ylabel('Stationary probability of two apparatus units')
    ax.grid(alpha=.2)
    ax.legend(fontsize=8)
    fig.suptitle('Paid renewal frontier · cadence 0.25\nConditional two-root means; high turnover accelerates both thermal assembly and disassembly', fontsize=12)
    fig.savefig(DOC/'RENEWAL_FRONTIER.png', dpi=160)
    fig.savefig(DOC/'RENEWAL_FRONTIER.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()

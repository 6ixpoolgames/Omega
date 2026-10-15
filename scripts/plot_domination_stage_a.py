"""Scientific suppression profiles; subject bands are bounds, not error bars."""
import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'
CACHE = ROOT/'results/local_runs/lushness_testbed/domination_stage_a/_mpl_cache'
CACHE.mkdir(parents=True, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(CACHE)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    with (DOC/'COMPARISON_MAP.csv').open(encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['slice'] == 'A1' and
                r['supply'] == '0.12' and r['kappa'] == '1' and
                r['cadence'] == '0.25' and r['horizon'] == '256.0']
    names = list(dict.fromkeys(r['target'] for r in rows))
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=False)
    for ax, target in zip(axes.ravel(), names):
        for mode, style in (('blocking', '-'), ('steering', '--')):
            curve = sorted([r for r in rows if r['target'] == target and r['mode'] == mode],
                           key=lambda r: float(r['phi']))
            x = [float(r['sigma']) for r in curve]
            ax.plot(x, [float(r['global_delta']) for r in curve], style,
                    color='#222222', lw=2, label='Whole '+mode)
            for subject, color in (('D', '#bf6510'), ('S', '#2874a6')):
                lo = [float(r[subject+'_difference_lower']) for r in curve]
                hi = [float(r[subject+'_difference_upper']) for r in curve]
                ax.plot(x, lo, style, color=color, alpha=.7, lw=1)
                ax.plot(x, hi, style, color=color, alpha=.7, lw=1)
                ax.fill_between(x, lo, hi, color=color, alpha=.1,
                                label=subject+' bounds '+mode)
        ax.axhline(0, color='#666666', lw=.7)
        ax.set_title(target.replace('_', ' '))
        ax.set_xlabel('Suppressed / idle subject events')
        ax.set_ylabel('History difference (bits)')
        ax.grid(alpha=.15)
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=9)
    fig.suptitle('Constraint geometry: whole field and personal histories', fontsize=15)
    fig.text(.5, .105, 'T256, cadence 0.25, supply 0.12, κ=1, bill one. Bands are conditioning intervals.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .15, 1, .95))
    for ext in ('png', 'svg'):
        path = DOC/('SUPPRESSION_PROFILE.'+ext)
        fig.savefig(path, dpi=150, facecolor='white')
        if ext == 'svg':
            path.write_text('\n'.join(x.rstrip() for x in path.read_text().splitlines())+'\n')
    plt.close(fig)


if __name__ == '__main__':
    main()

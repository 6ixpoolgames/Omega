"""Compact scientific figure of physical returns alongside breadth."""
import csv
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/resource_transfer'
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results/local_runs/lushness_testbed/resource_transfer/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    with (DOC/'COMPARISONS.csv').open(encoding='utf-8') as f:
        rows=[r for r in csv.DictReader(f) if r['mode']=='extract' and float(r['cadence'])==.25
              and float(r['horizon'])==256]
    fig,axes=plt.subplots(1,3,figsize=(12,3.8),layout='constrained')
    for strength,color in ((.2,'#217a6a'),(2.,'#596ac0')):
        points=sorted([r for r in rows if float(r['assistance'])==strength],key=lambda r:float(r['cost']))
        x=[float(r['cost']) for r in points]
        for ax,field in zip(axes,('D_paid_bank_delta','D_owned_energy_delta','whole_delta')):
            ax.plot(x,[float(r[field]) for r in points],'-o',color=color,label=f'assistance {strength:g}')
    for ax in axes:
        ax.axhline(0,color='#555',linewidth=.8)
        ax.set_xlabel('Handling bill per forward transfer')
        ax.set_xticks([.25,.5,.75])
    axes[0].set_title('D paid-bank account')
    axes[0].set_ylabel('Difference from matched passive arm (energy)')
    axes[1].set_title('D owned energy at deadline')
    axes[1].set_ylabel('Difference (energy)')
    axes[2].set_title('Whole-field history breadth')
    axes[2].set_ylabel('Difference (bits)')
    axes[2].legend(frameon=False)
    fig.suptitle('Extraction: material returns and breadth are separate\nT256, cadence 0.25; lines connect tested bills')
    fig.savefig(DOC/'BUDGET_AND_BREADTH.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()

"""Scientific figures for movement-only steering and matched exchange."""
import csv
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results/local_runs/lushness_testbed/continuation_controls_flow/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=ROOT/'docs/research_notes/lushness_testbed/continuation_controls'
def read(path):
    with path.open(encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
    path=BASE/'steering/COMPARISONS.csv'
    if path.exists():
        rows=read(path);fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for ax,horizon in zip(axes,(256,1024)):
            for mode,strength,style,color in (('steering',.55,'--','#217a6a'),('steering',.95,'-','#217a6a'),('blocking',.95,'-','#596ac0')):
                group=sorted([r for r in rows if r['mode']==mode and float(r['strength'])==strength and float(r['cadence'])==.25 and float(r['horizon'])==horizon],key=lambda r:float(r['yield']))
                ax.plot([float(r['yield']) for r in group],[float(r['whole_delta']) for r in group],style+'o',color=color,label=f'{mode}, {strength:g}')
            ax.axhline(0,color='#555',linewidth=.8);ax.set_title(f'T{horizon}')
            ax.set_xlabel('Pocket capture multiplier');ax.set_ylabel('Whole-history difference from idle (bits)')
        axes[0].legend(frameon=False,fontsize=8)
        fig.suptitle('Movement-only outside-to-trap control\nCadence 0.25; lines connect tested yields')
        fig.savefig(BASE/'steering/STEERING.png',dpi=160);plt.close(fig)
    path=BASE/'flow/COMPARISONS.csv'
    if path.exists():
        rows=[r for r in read(path) if float(r['cadence'])==.25 and float(r['horizon'])==256]
        fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for fraction,color in ((.25,'#217a6a'),(.75,'#596ac0')):
            group=sorted([r for r in rows if float(r['fraction'])==fraction],key=lambda r:float(r['net_at_T256']))
            axes[0].plot([float(r['net_at_T256']) for r in group],[float(r['whole_delta']) for r in group],'-o',color=color,label=f"gross {float(group[0]['gross_at_T256']):.2f}" if group else f'fraction {fraction}')
        axes[0].axhline(0,color='#555',linewidth=.8);axes[0].axvline(0,color='#999',linewidth=.6)
        axes[0].set_xlabel('Net transfer events: positive toward D')
        axes[0].set_ylabel('Whole bits relative to matched-gross zero net')
        axes[0].set_title('Direction at fixed exchange volume');axes[0].legend(frameon=False)
        p=BASE/'flow/ZERO_NET_TURNOVER.csv'
        if p.exists():
            zero=[r for r in read(p) if float(r['cadence'])==.25]
            zero.sort(key=lambda r:float(r['horizon']))
            axes[1].plot([float(r['horizon']) for r in zero],[float(r['whole_delta']) for r in zero],'-o',color='#b54338')
        axes[1].axhline(0,color='#555',linewidth=.8)
        axes[1].set_xlabel('Horizon (zero net matched at T256 only)')
        axes[1].set_ylabel('Whole bits: higher minus lower exchange volume')
        axes[1].set_title('Turnover at net zero')
        fig.suptitle('Matched transfer controls — cadence 0.25\nWork and total world activity are reported separately, not matched')
        fig.savefig(BASE/'flow/FLOW.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()

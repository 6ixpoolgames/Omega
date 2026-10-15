"""Compact figures from measured comparisons only."""
import csv
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results/local_runs/.matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DOC=ROOT/'docs/research_notes/lushness_testbed/domination_b1'


def main():
    with (DOC/'FOLLOWUP_MAP.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    fig, axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    environments=['s0.04-k0','s0.12-k0','s0.12-k1']
    colors={'ordinary':'#217a6a','blocking':'#b54338','sham':'#596ac0'}
    for j,arm in enumerate(colors):
        selected=[next(r for r in rows if r['environment']==env and r['arm']==arm
                       and r['reference']=='idle' and float(r['cadence'])==.25 and float(r['horizon'])==256)
                  for env in environments]
        xs=[i+(j-1)*.22 for i in range(3)]
        axes[0].bar(xs,[float(r['global_delta']) for r in selected],width=.2,color=colors[arm],label=arm)
        for x,r in zip(xs,selected):
            lo,hi=(float(r['D_difference_'+k]) for k in ('lower','upper'))
            axes[1].plot([x,x],[lo,hi],color=colors[arm],linewidth=3)
            axes[1].plot([x,x],[lo,hi],'_',color=colors[arm],markersize=6)
    for ax in axes:
        ax.axhline(0,color='#444',linewidth=.8)
        ax.set_xticks(range(3),['s=.04, κ=0','s=.12, κ=0','s=.12, κ=1'])
        ax.set_ylabel('Difference from idle (bits)')
    axes[0].set_title('Whole-field history')
    axes[1].set_title('D marginal-history bounds')
    axes[0].legend(frameon=False)
    fig.suptitle('Physical role and activity controls — T256, cadence 0.25')
    fig.savefig(DOC/'FOLLOWUP_CONTROLS.png',dpi=170)
    plt.close(fig)
    path=DOC/'DISCOVERY_MAP.csv'
    if not path.exists():return
    with path.open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    c5=sorted([r for r in rows if r['target']=='access_entry' and float(r['cost'])==.1
               and float(r['phi'])==.95 and float(r['cadence'])==.25],key=lambda r:float(r['horizon']))
    if len(c5)==4:
        fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
        times=[float(r['horizon']) for r in c5]
        for subject,color in [('D','#217a6a'),('S','#596ac0')]:
            lo=[float(r[subject+'_difference_lower']) for r in c5]
            hi=[float(r[subject+'_difference_upper']) for r in c5]
            ax.fill_between(times,lo,hi,color=color,alpha=.25,label=f'{subject} conditioning bounds')
            ax.plot(times,lo,color=color,linewidth=1)
            ax.plot(times,hi,color=color,linewidth=1)
        ax.plot(times,[float(r['global_delta']) for r in c5],'-o',color='#b54338',label='Whole-field history')
        ax.axhline(0,color='#333',linewidth=.8)
        ax.set_xscale('log');ax.set_xticks(times,[f'{t:g}' for t in times])
        ax.set_xlabel('Horizon (lines guide the eye between computed points)')
        ax.set_ylabel('Difference from idle (bits)')
        ax.set_title('Paid resource exclusion: self and whole disagree\nBill 0.1, strength 0.95, cadence 0.25')
        ax.legend(frameon=False)
        fig.savefig(DOC/'C5_SUBJECTS.png',dpi=170)
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax,time in zip(axes,[256,1024]):
        for cost,color in zip([.1,.3,1],['#217a6a','#596ac0','#b54338']):
            for strength,style in [(.55,'--'),(.95,'-')]:
                selected=sorted([r for r in rows if r['target']=='trap_entry'
                    and float(r['horizon'])==time and float(r['cadence'])==.25
                    and float(r['cost'])==cost and float(r['phi'])==strength],key=lambda r:float(r['opportunity_yield']))
                ax.plot([float(r['opportunity_yield']) for r in selected],
                        [float(r['global_delta']) for r in selected],style+'o',color=color,
                        label=f'bill {cost:g}, strength {strength:g}')
        ax.axhline(0,color='#444',linewidth=.8)
        ax.set_title(f'T{time}')
        ax.set_xlabel('Pocket capture coefficient multiplier')
        ax.set_ylabel('Whole-field difference from idle (bits)')
    axes[1].legend(frameon=False,fontsize=8)
    status=json.loads((DOC/'DISCOVERY_SUMMARY.json').read_text())
    suffix='' if status['status']=='complete' else f" — partial {status['completed']}/{status['total']}"
    fig.suptitle('Trap-entry steering with a paid opportunity beyond the trap\nCadence 0.25; lines connect tested yields'+suffix,fontsize=11)
    fig.savefig(DOC/'DISCOVERY_FRONTIER.png',dpi=170)
    plt.close(fig)

if __name__=='__main__':main()

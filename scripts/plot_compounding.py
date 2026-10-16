"""Standalone scientific figure from the retained frozen results."""
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
cache=ROOT/'results/local_runs/lushness_testbed/compounding/plot-cache'
cache.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(cache))
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

DOC=Path(__file__).resolve().parents[1]/'docs/research_notes/lushness_testbed/compounding'
s=json.loads((DOC/'SUMMARY.json').read_text())
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
colors={'loop':'#176a71','no_construction_assistance':'#d58836','no_capture_assistance':'#a75568','basal':'#666666'}
labels={'loop':'Full access/construction loop','no_construction_assistance':'No construction assistance',
        'no_capture_assistance':'No capture assistance','basal':'Basal mechanisms'}
caps=[4,8,16,32]
for m in caps:
    r=json.loads((DOC/f'laws/M{m}-c2-y3-d0.005.json').read_text())
    ts=[0,16,64,256,1024]
    axes[0,0].plot(ts,[1.]+[r['physical']['loop:seed'][str(t)]['apparatus_deadline'] for t in ts[1:]],
                   marker='o',label=f'Capacity {m}')
axes[0,0].set_xscale('symlog',linthresh=1)
axes[0,0].set(xlabel='Physical horizon',ylabel='Expected retained apparatus',
              title='A one-unit seed grows and persists')
axes[0,0].legend(fontsize=8)
for mode,color in colors.items():
    v=[s['laws'][f'M{m}-c2-y3-d0.005']['stationary'][mode] for m in caps]
    axes[0,1].plot(caps,[x['apparatus_deadline'] for x in v],marker='o',color=color,label=labels[mode])
    axes[1,1].plot(caps,[x['rate'] for x in v],marker='o',color=color,label=labels[mode])
axes[0,1].set(xlabel='Finite precursor inventory',ylabel='Stationary apparatus',title='Retention survives the turnover check')
axes[0,1].legend(fontsize=7)
axes[1,1].set(xlabel='Finite precursor inventory',ylabel='History rate (bits/time)',title='An ongoing breadth contribution, cadence 0.25')
costs=[1.5,2.,2.5];packets=[2.,3.,4.]
funding=np.array([[s['laws'][f'M8-c{c:g}-y{y:g}-d0.005']['stationary']['loop']['capture_funding_fraction']
                   for y in packets] for c in costs])
im=axes[1,0].imshow(funding,vmin=0,vmax=1,cmap='viridis',origin='lower',aspect='auto')
axes[1,0].set(xticks=range(3),xticklabels=packets,yticks=range(3),yticklabels=costs,
              xlabel='Packet energy',ylabel='Construction bill',title='Resource share of all bank expenditure, capacity 8')
for i in range(3):
    for j in range(3):
        axes[1,0].text(j,i,f'{100*funding[i,j]:.1f}%',ha='center',va='center',color='white' if funding[i,j]<.8 else 'black')
fig.colorbar(im,ax=axes[1,0],label='Capture funding fraction')
fig.suptitle('Bounded resource-funded compounding\nSame offered source per comparison; low isolated damage; exact finite model',fontsize=13)
for ax in (axes[0,0],axes[0,1],axes[1,1]):
    ax.grid(alpha=.2)
fig.savefig(DOC/'COMPOUNDING_BOUNDARY.png',dpi=160)
fig.savefig(DOC/'COMPOUNDING_BOUNDARY.svg')

"""Small adapter calibration; manifest is frozen before engine execution."""
from __future__ import annotations

import sys
if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Parent must install resource caps before releasing worker')

from collections import Counter
import hashlib
import html
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from omega_v2.testbed.bng_network import (
    Reaction, Network, parse_net, enumerate_generator, transition, history_bits, ssa_endpoints,
)


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    tmp.replace(path)


def occupancy(network,state):
    return sum(n * name.count('B(') for name,n in zip(network.species,state) if 'A(' in name)


def resolved_key(network,state):
    return tuple(sum(n * bool(re.search(site+r'!\d',name)) for name,n in
                     zip(network.species,state) if 'A(' in name) for site in ('l','r'))


def sampling_check(observed,expected,n):
    margin=6*np.sqrt(expected*(1-expected)/n)+1/n
    errors=abs(observed-expected)
    return {'samples':n,'observed':observed.tolist(),'expected':expected.tolist(),
            'absolute_errors':errors.tolist(),'margins':margin.tolist(),
            'passed':bool(np.all(errors<=margin))}


def main(out):
    start=time.perf_counter()
    spec=ROOT/'docs/research_notes/lushness_testbed/calibration'
    protocol=json.loads((spec/'PROTOCOL.json').read_text())
    package=Path(importlib.util.find_spec('bionetgen').origin).parent
    engine=package/'bng-win'
    perl=shutil.which('perl') or 'C:/Program Files/Git/usr/bin/perl.exe'
    if not Path(perl).exists(): raise RuntimeError('A local Perl runtime is required')
    if importlib.metadata.version('bionetgen') != protocol['package_version']:
        raise RuntimeError('BioNetGen package differs from frozen calibration version')
    if (engine/'VERSION').read_text().strip() != protocol['engine_version']:
        raise RuntimeError('Engine differs from frozen calibration version')
    source_paths=list(spec.glob('*'))+[
        ROOT/'omega_v2/testbed/bng_network.py',ROOT/'omega_v2/testbed/__init__.py',
        ROOT/'scripts/bng_binding_worker.py',ROOT/'scripts/run_bng_binding_calibration.py',
        ROOT/'tests/test_bng_calibration.py',
        ROOT/'docs/research_notes/lushness_testbed/MEASUREMENT_r1.md']
    upstream=ROOT/'results/local_runs/lushness_testbed/upstream/BAB.bngl'
    if not upstream.exists() or digest(upstream) != protocol['upstream']['sha256']:
        raise RuntimeError('Pinned upstream source missing or hash mismatch')
    shutil.copyfile(upstream,out/'upstream_BAB.bngl')
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in source_paths if p.is_file()}
    for relative in sources:
        target=out/'source'/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
    engine_hashes={p.relative_to(engine).as_posix():digest(p) for p in engine.rglob('*') if p.is_file()}
    manifest={'schema_version':'omega-calibration-manifest/1','protocol':protocol,
        'sources':sources,'engine_hashes':engine_hashes,'perl_path':str(perl),'perl_hash':digest(Path(perl)),
        'python':sys.version,'platform':platform.platform(),
        'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
        'git_branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'raw_retention':'local, pinned for this calibration; no deletion'}
    manifest['input_hash']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    write_json(out/'manifest.json',manifest)
    write_json(out/'status.json',{'status':'running','stage':'engine_generation'})

    models={}
    engine_env=os.environ.copy()
    engine_env['BNGPATH']=engine.as_posix()
    for name in ('symmetric','resolved','homodimer'):
        folder=out/name; folder.mkdir()
        shutil.copyfile(spec/(name+'.bngl'),folder/(name+'.bngl'))
        with (folder/'generation.log').open('w') as log:
            subprocess.run([perl,(engine/'BNG2.pl').as_posix(),name+'.bngl'],cwd=folder,
                env=engine_env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25)
        net=parse_net(folder/(name+'.net'))
        states,q=enumerate_generator(net)
        models[name]=(net,states,q)

    net,states,q=models['symmetric']
    order=sorted(range(len(states)),key=lambda i:occupancy(net,states[i]))
    q=q[np.ix_(order,order)]
    hand=np.array([[-4.,4.,0.],[1.,-2.,1.],[0.,2.,-2.]])
    p1=float(np.max(abs(q-hand)))
    fine_net,fine_states,fine_q=models['resolved']
    fine_order=sorted(range(len(fine_states)),key=lambda i:resolved_key(fine_net,fine_states[i]))
    fine_q=fine_q[np.ix_(fine_order,fine_order)]
    keys=[resolved_key(fine_net,fine_states[i]) for i in fine_order]
    fine_hand=np.zeros((4,4))
    projection=np.zeros((4,3))
    for i,key in enumerate(keys):
        projection[i,sum(key)]=1
        for site in range(2):
            target=list(key); target[site]=1-target[site]
            fine_hand[i,keys.index(tuple(target))]=1. if key[site] else 2-sum(key)
        fine_hand[i,i]=-fine_hand[i].sum()
    p2=max(float(np.max(abs(fine_q-fine_hand))),float(np.max(abs(fine_q@projection-projection@q))))
    _,_,homo_q=models['homodimer']
    p3=float(np.max(abs(homo_q-np.array([[-1.,1.],[1.,-1.]]))))
    profiles=[]
    for delta in [protocol['primary_cadence']]+protocol['sensitivity_cadences']:
        steps=round(protocol['physical_horizon']/delta)
        pc,pf=transition(q,delta),transition(fine_q,delta)
        coarse=float(history_bits(pc,steps)[0]); fine=float(history_bits(pf,steps)[0])
        profiles.append({'delta':delta,'horizon':steps*delta,'coarse_bits':coarse,
                         'resolved_bits':fine,'difference_bits':fine-coarse,
                         'semigroup_error':float(np.max(abs(pc@pc-transition(q,2*delta))))})
    expected=transition(q,protocol['endpoint_horizon'])[0]
    counts=ssa_endpoints(net,protocol['endpoint_horizon'],protocol['own_ssa_samples'],protocol['own_ssa_seed'])
    own=np.zeros(3)
    for state,count in counts.items(): own[occupancy(net,state)]+=count
    own_result=sampling_check(own/protocol['own_ssa_samples'],expected,protocol['own_ssa_samples'])

    write_json(out/'status.json',{'status':'running','stage':'independent_engine_ssa'})
    external_counts=np.zeros(3)
    external=out/'upstream_ssa'; external.mkdir()
    for seed in range(protocol['upstream_ssa_seeds']['start'],protocol['upstream_ssa_seeds']['stop_exclusive']):
        prefix=external/str(seed)
        result=subprocess.run([str(engine/'bin/run_network.exe'),'-p','ssa','-h',str(seed),
            '-o',str(prefix),str(out/'symmetric/symmetric.net'),str(protocol['endpoint_horizon']),'1'],
            cwd=external,capture_output=True,text=True,timeout=10)
        if result.returncode:
            raise RuntimeError('Upstream SSA failed: '+result.stdout[-1000:]+result.stderr[-1000:])
        samples=np.loadtxt(prefix.with_suffix('.cdat'))
        end=samples[-1,1:]
        if not np.allclose(end,np.rint(end),atol=1e-10): raise AssertionError('Noninteger SSA state')
        external_counts[occupancy(net,tuple(np.rint(end).astype(int)))]+=1
    external_result=sampling_check(external_counts/protocol['upstream_ssa_samples'],expected,protocol['upstream_ssa_samples'])

    permutation=[2,0,1]
    permuted=q[np.ix_(permutation,permutation)]
    delta=protocol['primary_cadence']; steps=round(protocol['physical_horizon']/delta)
    base=history_bits(transition(q,delta),steps)[0]
    relabel_error=abs(float(history_bits(transition(permuted,delta),steps)[permutation.index(0)]-base))
    split=[]
    for r in net.reactions:
        split.extend([Reaction(r.reactants,r.products,r.coefficient/2)]*2)
    _,split_q=enumerate_generator(Network(net.species,net.initial,split))
    original_q=models['symmetric'][2]
    split_error=float(np.max(abs(split_q-original_q)))
    stationary=np.array([1.,4.,2.])/7
    balance_error=float(np.max(abs(stationary[:,None]*q-(stationary[:,None]*q).T)))
    audits={
        'P1':p1<=protocol['generator_tolerance'],
        'P2':p2<=protocol['generator_tolerance'],
        'P3':p3<=protocol['generator_tolerance'],
        'P4':own_result['passed'] and external_result['passed'],
        'P5':max(relabel_error,split_error)<=protocol['numerical_tolerance'],
        'P6':all(row['difference_bits']>0 for row in profiles),
        'closed_binding_balance':balance_error<=protocol['numerical_tolerance'],
        'semigroup':max(row['semigroup_error'] for row in profiles)<=protocol['numerical_tolerance']}
    summary={'schema_version':'omega-binding-result/1','input_hash':manifest['input_hash'],
        'status':'pass' if all(audits.values()) else 'fail','audits':audits,
        'generator_errors':{'symmetric':p1,'resolved_and_projection':p2,'homodimer':p3},
        'generators':{'symmetric':q.tolist(),'resolved':fine_q.tolist(),'homodimer':homo_q.tolist()},
        'states':{name:len(values[1]) for name,values in models.items()},
        'species':{name:values[0].species for name,values in models.items()},
        'coefficients':{name:[r.coefficient for r in values[0].reactions] for name,values in models.items()},
        'stationary_occupancy':stationary.tolist(),'detailed_balance_error':balance_error,
        'relabel_error':relabel_error,'channel_split_error':split_error,
        'breadth_profiles':profiles,'own_ssa':own_result,'upstream_ssa':external_result,
        'wall_seconds':time.perf_counter()-start,
        'scope':'closed binding adapter calibration; no fuel, controller, generativity or ethical result'}
    write_json(out/'summary.json',summary)
    np.savez_compressed(out/'operators.npz',symmetric=q,resolved=fine_q,homodimer=homo_q)
    lines=['# Binding calibration report','',f"Status: **{summary['status']}**",'',
        'One bivalent A, two B; normalized association/dissociation constants both 1.',
        'The symmetric occupancy chain has rates 4, 1 forward and 1, 2 backward.',
        'The resolved-site model has four states; its projection reproduces that chain.',
        '', '| Cadence | Coarse bits at T=4 | Resolved bits | Difference |',
        '|---|---:|---:|---:|']
    lines += [f"| {r['delta']} | {r['coarse_bits']:.9f} | {r['resolved_bits']:.9f} | {r['difference_bits']:.9f} |" for r in profiles]
    lines += ['', '## Checks','']+[f'- {key}: {value}' for key,value in audits.items()]
    lines += ['',f"Own SSA: {protocol['own_ssa_samples']} independent trials; upstream SSA: {protocol['upstream_ssa_samples']} trials.",
        'Category-wise errors and predeclared sampling bounds are in summary.json.',
        '', 'This distinguishes bookkeeping invariance from physical resolution sensitivity.',
        'It does not identify a universal grain or test an ethical policy.',
        '',f"Frozen input hash: {manifest['input_hash']}"]
    markdown='\n'.join(lines)+'\n'; (out/'report.md').write_text(markdown,encoding='utf-8')
    (out/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Binding calibration</title>'
        '<style>body{max-width:1000px;margin:2rem auto;font:16px system-ui}pre{white-space:pre-wrap}</style>'
        '<pre>'+html.escape(markdown)+'</pre>',encoding='utf-8')
    write_json(out/'status.json',{'status':summary['status'],'wall_seconds':time.perf_counter()-start})
    print(json.dumps({'status':summary['status'],'audits':audits,'wall_seconds':summary['wall_seconds']}),flush=True)
    return 0 if all(audits.values()) else 1


if __name__=='__main__':
    destination=Path(sys.argv[1]).resolve()
    try:
        raise SystemExit(main(destination))
    except Exception as error:
        write_json(destination/'status.json',{'status':'error','error':str(error)})
        traceback.print_exc(); raise SystemExit(1)

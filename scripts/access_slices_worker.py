from __future__ import annotations
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':
    raise SystemExit('Parent must install resource caps before releasing worker')
import json
from pathlib import Path
import traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    kind=sys.argv[1];out=Path(sys.argv[2])
    try:
        if kind=='assembly':
            from omega_v2.testbed.assembly_slice import run
            run(out)
        elif kind=='controlled':
            from omega_v2.testbed.controlled_slice import run
            run(out)
        elif kind in ('access_extension','extension_smoke'):
            from omega_v2.testbed.access_extension import run
            run(out,int(sys.argv[3]),smoke=kind=='extension_smoke')
        else:
            from omega_v2.testbed.controlled_slice import engine_check, generator, SPEC, energy, STATES
            import numpy as np
            p=json.loads((SPEC/'PROTOCOL.json').read_text())['parameters']
            checks=engine_check(out,p)
            q,_=generator((.5,)*4,{**p,'chemical_potential':0.})
            pi=np.exp(-np.array([energy(s) for s in STATES]));pi/=sum(pi)
            err=float(np.max(abs(pi[:,None]*q-(pi[:,None]*q).T)))
            if err>1e-11:raise AssertionError('Equilibrium check')
            (out/'smoke.json').write_text(json.dumps({'bng':checks,'closed_balance':err},indent=2))
    except Exception:
        (out/'failure.txt').write_text(traceback.format_exc());raise

if __name__=='__main__':main()

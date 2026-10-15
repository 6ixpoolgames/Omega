"""Capped finite-window transfer calibration."""
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':raise SystemExit('Caps required')
from pathlib import Path

def main(out):
    source=Path(__file__).resolve().parents[1];sys.path.insert(0,str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json
    from omega_v2.testbed.domination_friction import FrictionParameters
    from omega_v2.testbed.analysis.flow_matching import calibrate
    c=verify_bundle(out)['config']
    result=calibrate(FrictionParameters(**c['parameters']))
    result['imports_from_snapshot']=all(Path(v.__file__).resolve().is_relative_to(source)
        for k,v in sys.modules.items() if k.startswith('omega_v2') and getattr(v,'__file__',None))
    if not result['imports_from_snapshot']:raise RuntimeError('Source escaped snapshot')
    atomic_json(out/'RESULTS.json',result)

if __name__=='__main__':main(Path(sys.argv[1]))

"""Rebuild selected deterministic raw archives from retained source alone."""
from __future__ import annotations

import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def rebuild(artifact_id):
    import numpy as np
    if artifact_id.startswith('catalytic-binding-'):
        from scipy.sparse import csr_matrix
        from omega_v2.finite.catalytic_binding import CatalyticBinding
        from omega_v2.validation.catalytic_binding_v0 import LAGS
        barrier=int(artifact_id.rsplit('-',1)[1]); m=CatalyticBinding(barrier=barrier)
        q=csr_matrix(m.q)
        return dict(states=m.states,values=m.values,equilibrium=m.pi,rates=m.rates,
            targets=m.targets,reward_rates=m.rewards,Q_data=q.data,Q_indices=q.indices,
            Q_indptr=q.indptr,Q_shape=np.array(q.shape),kernel_lags=np.array(LAGS),
            K=np.stack([m.evolution(t)[0] for t in LAGS]))
    if artifact_id=='local-flow':
        from omega_v2.validation.local_flow_v0 import apparatus,LAGS,DRIVES
        arrays={}
        for kind in ('disconnected','sensor','relay','fan','gated_relay','two_clocks',
                     'ring4','parity','passive_pair'):
            for drive in (0,) if kind=='passive_pair' else DRIVES:
                name=f'{kind}_d{drive}';m=apparatus(kind,drive)
                arrays[name+'_Q']=m.q;arrays[name+'_channel_rates']=m.rates
                arrays[name+'_K']=np.stack([m.kernel(t) for t in LAGS])
        return arrays
    if artifact_id=='fuel-flow':
        from omega_v2.finite.fuel_flow import FuelFlow
        from omega_v2.validation.fuel_flow_v0 import CUTS,LAGS,RECOVERY
        arrays={};times=sorted(set(CUTS+LAGS+RECOVERY))
        for capacity in (1,4,8):
            for assembly in (.25,1):
                for damage in (.005,.05):
                    m=FuelFlow(capacity,assembly=assembly,damage=damage)
                    name=f'B{capacity}_a{assembly}_d{damage}'
                    arrays[name+'_Q']=m.q;arrays[name+'_states']=m.values
                    arrays[name+'_rates']=m.rates;arrays[name+'_targets']=m.targets
                    arrays[name+'_times']=np.array(times)
                    arrays[name+'_K']=np.stack([m.evolution(t)[0] for t in times])
                    arrays[name+'_expected_charges']=np.stack([m.evolution(t)[1] for t in times])
                    arrays[name+'_first_exhaustion']=np.stack([m.exhaustion_probability(t) for t in CUTS])
        return arrays
    if artifact_id.startswith('thermal-binding-'):
        from omega_v2.finite.fuel_flow import FuelFlow
        from omega_v2.validation.thermal_binding_v0 import CUTS,LAGS
        setting=artifact_id.removeprefix('thermal-binding-')
        if setting=='thermal':m=FuelFlow(4,assembly=1,damage=.05)
        else:
            import importlib.util
            snapshot=ROOT/'docs/implementation/artifact_reconstruction/spatial_binding_thermal_20261003.py'
            spec=importlib.util.spec_from_file_location('_retained_thermal_binding',snapshot)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            m=module.SpatialBinding(mobility=float(setting))
        times=sorted(set(CUTS+LAGS))
        return dict(Q=m.q,states=m.values,equilibrium=m.pi,rates=m.rates,targets=m.targets,
            kernel_times=np.array(times),K=np.stack([m.evolution(t)[0] for t in times]),
            expected_bill=np.stack([m.evolution(t)[1] for t in times]))
    if artifact_id.startswith('catalytic-history-'):
        from omega_v2.validation import catalytic_history_v0 as module
        arrays={}; original=np.savez_compressed
        # Retained original runner provides the complete observer/conditioning algebra.
        # Capture its payload without writing into the historical evidence directory.
        def capture(_path,**payload):arrays.update(payload)
        try:
            np.savez_compressed=capture
            module.run(int(artifact_id.rsplit('-',1)[1]))
        finally:np.savez_compressed=original
        if not arrays:raise RuntimeError('Original runner emitted no archive')
        return arrays
    raise ValueError('Unknown audited artifact ID')


def verify(arrays,path):
    import numpy as np
    checks={}
    with np.load(path,allow_pickle=False) as old:
        if set(old.files)!=set(arrays):raise AssertionError('Archive field mismatch')
        for key,new in arrays.items():
            before=old[key];new=np.asarray(new)
            if before.shape!=new.shape or before.dtype!=new.dtype:
                raise AssertionError(f'{key}: schema mismatch')
            exact=np.array_equal(before,new)
            if before.dtype.kind in 'biu' and not exact:
                raise AssertionError(f'{key}: integer/boolean reconstruction mismatch')
            if not exact and not np.allclose(before,new,rtol=1e-10,atol=1e-12,equal_nan=False):
                raise AssertionError(f'{key}: reconstruction mismatch')
            checks[key]={'shape':list(new.shape),'dtype':str(new.dtype),'exact':bool(exact),
                'max_absolute_error':0. if exact else float(np.max(np.abs(before-new),initial=0))}
    return checks


def main():
    import argparse,json
    import numpy as np
    parser=argparse.ArgumentParser()
    parser.add_argument('--artifact',required=True);parser.add_argument('--output',type=Path)
    parser.add_argument('--verify',type=Path)
    args=parser.parse_args()
    if not (args.output or args.verify):parser.error('--output or --verify required')
    arrays=rebuild(args.artifact)
    if args.verify:print(json.dumps(verify(arrays,args.verify),separators=(',',':')))
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(args.output,**arrays)
        print(str(args.output))

if __name__=='__main__':main()

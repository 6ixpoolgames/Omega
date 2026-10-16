"""Matched resource-rich preparation and active-constraint sensitivity."""
import argparse
from pathlib import Path
import run_c5_upgrade as upgrade
engine=upgrade.engine
original_sources=engine.sources
engine.sources=lambda:original_sources()+['scripts/run_c5_followups.py']

def plan(study):
    common={'entropy_backend':'uniformized','entropy_threads':2,'block_rows':96}
    if study=='supplied-pump':
        p={'charge_capacity':2,'d_energy_capacity':2,'s_energy_capacity':2,
           'd_energy_quantum':.5,'s_energy_quantum':.5,'device_role':'ordinary'}
        return [{**common,'id':mode,'parameters':p,'preparation':'D_supplied',
                 'extension':{'pump':True,'pump_mode':mode}} for mode in ('passive','extract','donate')]
    p={'charge_capacity':2,'d_energy_capacity':1,'s_energy_capacity':1,
       'd_energy_quantum':.5,'s_energy_quantum':.5,'device_role':'friction','discovery':True}
    return [{**common,'id':name,'parameters':p,'extension':{'opportunity':True,'local_source':.12},
             'policy':policy} for name,policy in (
                ('idle',{'phi':0,'cost':0}),
                ('movement-steering',{'mode':'steering','phi':.95,'cost':.5,
                    'edges':[[0,2],[1,2],[3,2]]}),
                ('blocking',{'phi':.95,'cost':.5,'edges':[[0,2],[1,2],[3,2]]}))]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',choices=['supplied-pump','opportunity-active'])
    parser.add_argument('--jobs',type=int,default=1)
    args=parser.parse_args()
    if not 1<=args.jobs<=2:raise ValueError('One or two capped workers')
    upgrade.configure(args.study)
    raise SystemExit(engine.execute(plan(args.study),'survey',args.jobs,900,7200))

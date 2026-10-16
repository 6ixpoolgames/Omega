"""Capped physical C5 corrections: paid pumping, independent access and loss."""
import argparse
from pathlib import Path
import run_domination_b1 as engine

ROOT=Path(__file__).resolve().parents[1]
previous_sources=engine.sources
engine.sources=lambda:previous_sources()+['scripts/run_c5_upgrade.py','scripts/domination_b1_worker.py']

def configure(study):
    engine.DOC=ROOT/'docs/research_notes/lushness_testbed/c5_upgrade'/study
    engine.LOCAL=ROOT/'results/local_runs/lushness_testbed'/('c5_upgrade_'+study)

def plan(study,smoke=False):
    common={'entropy_backend':'uniformized','entropy_threads':2,'block_rows':96}
    symmetric={'charge_capacity':2,'d_energy_capacity':2,'s_energy_capacity':2,
               'd_energy_quantum':.5,'s_energy_quantum':.5,'device_role':'ordinary'}
    cases=[]
    if study in ('pump','loss'):
        for loss in ((.01,.04) if study=='loss' else (0.,)):
            for mode in ('passive','extract','donate'):
                cases.append({'id':f'{mode}-loss{loss:g}','parameters':symmetric,
                    'extension':{'pump':True,'pump_mode':mode,'irreversible_loss':loss}})
    elif study=='opportunity':
        p={**symmetric,'discovery':True,'d_energy_capacity':1,'s_energy_capacity':1}
        for supply in (.02,.12,.6):
            for field in (0.,1.,3.):
                cases.append({'id':f'source{supply:g}-field{field:g}',
                    'parameters':{**p,'field_shift':field,'field_locations':[2]},
                    'extension':{'opportunity':True,'local_source':supply}})
    elif study=='audit-controls':
        p={'discovery':True,'d_energy_capacity':3,'d_energy_quantum':.5,
           'charge_capacity':2,'kappa':0}
        for name,policy,extra in (
            ('idle',{'phi':0,'cost':0},{}),
            ('blocking',{'phi':.95,'cost':.5},{}),
            ('driven-debit',{'phi':.95,'cost':.5,'mode':'driven_debit'},{}),
            ('ordinary',{'phi':0,'cost':0},{'device_role':'ordinary'}),
            ('movement-access',{'phi':.95,'cost':.5,'mode':'steering','region':[0]},{}),
            ('movement-build',{'phi':.95,'cost':.5,'mode':'steering','region':[1]},{}),
            ('movement-trap',{'phi':.95,'cost':.5,'mode':'steering','edges':[[0,2],[1,2],[3,2]]},{})):
            cases.append({'id':name,'parameters':{**p,**extra},'policy':policy})
    elif study=='cost-boundary':
        for cost in (1.,1.5):
            for mode in ('passive','extract'):
                cases.append({'id':f'{mode}-bill{cost:g}',
                    'parameters':{'d_energy_capacity':3,'d_energy_quantum':.5},
                    'transfer_policy':{'mode':mode,'cost':cost,'assistance':2.}})
    else:raise ValueError(study)
    cases=[{**common,**c} for c in cases]
    if smoke:
        case=cases[-1]
        if study in ('pump','loss'):
            case={**case,'parameters':{**case['parameters'],'d_energy_capacity':1,'s_energy_capacity':1}}
        case={**case,'id':study+'-engineering-smoke','cadences':[.25],'horizons':[16,64]}
        cases=[case]
    return cases

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',choices=['pump','opportunity','loss','audit-controls','cost-boundary'])
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--seconds',type=float,default=900)
    parser.add_argument('--budget',type=float,default=14400)
    args=parser.parse_args()
    if not 1<=args.jobs<=2:raise ValueError('Use at most two capped workers')
    configure(args.study)
    raise SystemExit(engine.execute(plan(args.study,args.smoke),'smoke' if args.smoke else 'survey',
        args.jobs,args.seconds,args.budget))

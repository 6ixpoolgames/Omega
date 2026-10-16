"""Capped numerical follow-up; no new physical ranking law."""
import run_c5_upgrade as upgrade
engine=upgrade.engine
original=engine.sources
engine.sources=lambda:original()+['scripts/run_c5_crossover_probe.py']
if __name__=='__main__':
    upgrade.configure('historical-crossover')
    raise SystemExit(engine.execute([{'id':'historical-rate-offset-probe'}],'probe',1,900,1800,
                                    worker='scripts/c5_crossover_worker.py'))

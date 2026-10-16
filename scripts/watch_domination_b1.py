"""Finite batch postprocessor: refresh verified readouts on result changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic,sleep

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/domination_b1'


def main():
    previous=None
    start=monotonic()
    while monotonic()-start<5*3600:
        files=[DOC/'SURVEY_STATUS.json',DOC/'PRIORITY-COMPANION_STATUS.json']
        signature=tuple((p.name,p.stat().st_mtime_ns) for p in files if p.exists())
        if signature and signature!=previous:
            subprocess.run([sys.executable,'scripts/report_domination_b1.py'],cwd=ROOT,check=True)
            for mode in ('survey','priority-companion'):
                if (DOC/(mode.upper()+'_STATUS.json')).exists():
                    subprocess.run([sys.executable,'scripts/validate_domination_b1.py',mode],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            subprocess.run([sys.executable,'scripts/plot_domination_b1.py'],cwd=ROOT,check=True)
            report_files=['scripts/report_domination_b1.py','scripts/validate_domination_b1.py',
                          'scripts/plot_domination_b1.py','scripts/watch_domination_b1.py']
            (DOC/'REPORT_SOURCES.json').write_text(json.dumps({
                name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in report_files},indent=2)+'\n',encoding='utf-8')
            previous=signature
            status=json.loads((DOC/'SURVEY_STATUS.json').read_text())
            if status['status']!='running':
                print(json.dumps({'postprocessor':'finished','batch_status':status['status']}),flush=True)
                return int(status['status']!='complete')
        sleep(10)
    print('Postprocessor time budget reached; durable results are unchanged.',flush=True)
    return 1

if __name__=='__main__':raise SystemExit(main())

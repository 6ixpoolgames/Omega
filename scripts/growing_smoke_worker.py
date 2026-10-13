from __future__ import annotations
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':raise SystemExit('Caps required before worker release')
from pathlib import Path
import traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
if __name__=='__main__':
    out=Path(sys.argv[1])
    try:
        from omega_v2.testbed.growing_smoke import run
        run(out)
    except Exception:
        (out/'failure.txt').write_text(traceback.format_exc());raise

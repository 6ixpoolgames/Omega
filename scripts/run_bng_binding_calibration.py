"""Hard-capped Windows engineering run. No cleanup or publication side effects."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes as w
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


def capped(command, out, seconds=120, memory=1024**3, output_cap=256*1024**2):
    if os.name != 'nt': raise RuntimeError('Windows Job Object required by this runner')
    class Basic(ctypes.Structure):
        _fields_ = [('process_time',ctypes.c_longlong),('job_time',ctypes.c_longlong),
                    ('flags',w.DWORD),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),
                    ('active',w.DWORD),('affinity',ctypes.c_size_t),('priority',w.DWORD),
                    ('scheduling',w.DWORD)]
    class IO(ctypes.Structure):
        _fields_ = [(n,ctypes.c_ulonglong) for n in
                    ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
    class Extended(ctypes.Structure):
        _fields_ = [('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),
                    ('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),
                    ('peak_job',ctypes.c_size_t)]
    k = ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR]; k.CreateJobObjectW.restype=w.HANDLE
    k.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
    k.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p]
    k.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
    k.TerminateJobObject.argtypes=[w.HANDLE,w.UINT]; k.CloseHandle.argtypes=[w.HANDLE]
    job=k.CreateJobObjectW(None,None)
    if not job: raise ctypes.WinError(ctypes.get_last_error())
    limits=Extended(); limits.basic.flags=0x200|0x2000  # job memory + kill on close
    limits.job_memory=memory
    child=None; start=time.perf_counter(); reason=None
    try:
        if not k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)):
            raise ctypes.WinError(ctypes.get_last_error())
        env=os.environ.copy()
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): env[key]='1'
        with (out/'worker.log').open('w',encoding='utf-8') as log:
            child=subprocess.Popen(command,cwd=ROOT,env=env,stdin=subprocess.PIPE,
                stdout=log,stderr=subprocess.STDOUT,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
            if not k.AssignProcessToJobObject(job,w.HANDLE(int(child._handle))):
                child.kill(); child.wait(); raise ctypes.WinError(ctypes.get_last_error())
            child.stdin.write('GO\n'); child.stdin.flush(); child.stdin.close()
            while child.poll() is None:
                if time.perf_counter()-start > seconds: reason='wall_cap'
                size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
                if size > output_cap: reason='output_cap'
                if reason:
                    k.TerminateJobObject(job,124); child.wait(); break
                time.sleep(.1)
        measured=Extended()
        ok=k.QueryInformationJobObject(job,9,ctypes.byref(measured),ctypes.sizeof(measured),None)
        return {'exit_code':child.returncode,'cap_reason':reason,
            'wall_seconds':time.perf_counter()-start,'wall_cap_seconds':seconds,
            'job_memory_cap_bytes':memory,'peak_job_bytes':measured.peak_job if ok else None,
            'output_bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}
    finally:
        if child is not None and child.poll() is None:
            k.TerminateJobObject(job,125); child.wait()
        k.CloseHandle(job)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-caps',action='store_true')
    args=parser.parse_args()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out=ROOT/'results/local_runs/lushness_testbed'/('binding-'+stamp)
    out.mkdir(parents=True)
    if args.check_caps:
        timeout=capped([sys.executable,'-c','import sys,time;sys.stdin.readline();time.sleep(10)'],out,seconds=.4)
        memory=capped([sys.executable,'-c',
            'import sys\nsys.stdin.readline()\ntry:\n x=bytearray(128*1024**2)\nexcept MemoryError:\n sys.exit(86)\nsys.exit(1)'],
            out,memory=64*1024**2,seconds=10)
        result={'timeout':timeout,'memory':memory,
                'passed':timeout['cap_reason']=='wall_cap' and memory['exit_code']==86}
        (out/'CAP_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'out':str(out),**result})); return 0 if result['passed'] else 1
    result=capped([sys.executable,'-u',str(ROOT/'scripts/bng_binding_worker.py'),str(out)],out)
    (out/'PROFILE.json').write_text(json.dumps(result,indent=2)+'\n')
    if result['exit_code'] != 0:
        (out/'execution_status.json').write_text(json.dumps({
            'status':'incomplete','exit_code':result['exit_code'],
            'cap_reason':result['cap_reason']},indent=2)+'\n')
    # Finalize only after status, profile and closed worker log are immutable.
    artifacts={'schema_version':'omega-artifacts/1','files':[
        {'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,
         'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'retention':'pinned_calibration'}
        for p in out.rglob('*') if p.is_file() and p.name!='artifacts.json']}
    (out/'artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
    print(json.dumps({'out':str(out),**result}),flush=True)
    return result['exit_code']


if __name__=='__main__': raise SystemExit(main())

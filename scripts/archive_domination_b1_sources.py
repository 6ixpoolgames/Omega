"""Retain one small code-only archive per immutable run-source hash."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'results/local_runs/lushness_testbed/domination_b1'
DOC=ROOT/'docs/research_notes/lushness_testbed/domination_b1'


def main():
    out=DOC/'source_archives'
    out.mkdir(parents=True,exist_ok=True)
    entries={}
    snapshots=[]
    for source in sorted(LOCAL.glob('batch-source-*')):
        payload={p.relative_to(source).as_posix():p.read_bytes() for p in sorted(source.rglob('*.py'))}
        digest=hashlib.sha256(b''.join(p.encode()+b'\0'+payload[p] for p in sorted(payload))).hexdigest()
        if digest != source.name.removeprefix('batch-source-'):
            raise RuntimeError('Snapshot byte identity mismatch')
        snapshots.append((digest,payload))
    for manifest_path in sorted(LOCAL.glob('*/manifest.json')):
        manifest=json.loads(manifest_path.read_text())
        source=manifest_path.parent/'source'
        payload={r['path']:(source/r['path']).read_bytes() for r in manifest['sources']}
        if any(hashlib.sha256(payload[r['path']]).hexdigest()!=r['sha256'] for r in manifest['sources']):
            raise RuntimeError('Run-source byte identity mismatch')
        digest=hashlib.sha256(b''.join(p.encode()+b'\0'+payload[p] for p in sorted(payload))).hexdigest()
        snapshots.append((digest,payload))
    for digest,payload in snapshots:
        if digest in entries:continue
        path=out/(digest+'.zip')
        if not path.exists():
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
                for name,data in sorted(payload.items()):
                    info=zipfile.ZipInfo(name,date_time=(2026,10,15,0,0,0))
                    info.compress_type=zipfile.ZIP_DEFLATED
                    archive.writestr(info,data)
        with zipfile.ZipFile(path) as archive:
            if {p:archive.read(p) for p in archive.namelist()} != payload:
                raise RuntimeError('Archived source verification failed')
        entries[digest]={'source_hash':digest,'files':len(payload),'archive':path.relative_to(DOC).as_posix(),
                        'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'contains_kernels_or_run_dumps':False}
    records=[entries[k] for k in sorted(entries)]
    (DOC/'SOURCE_ARCHIVES.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'archives':len(records),'total_bytes':sum(x['bytes'] for x in records)}))

if __name__=='__main__':main()

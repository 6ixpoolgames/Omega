"""Small, verified numerical query blocks; never physical states or kernels."""
import hashlib
import io
import json
import os
from pathlib import Path
from time import sleep
from uuid import uuid4
import numpy as np


class EntropyBlocks:
    def __init__(self, root, Q, clocks, tail_budget, version='poisson-csr-1'):
        h=hashlib.sha256()
        for value in (np.asarray(Q.shape,dtype='<i8'),Q.indptr,Q.indices,Q.data):
            h.update(value.dtype.str.encode()+b'\0'+value.tobytes())
        specification={'generator_sha256':h.hexdigest(),'cadences':list(clocks),
                       'tail_budget':tail_budget,'method':version}
        self.key=hashlib.sha256(json.dumps(specification,sort_keys=True).encode()).hexdigest()
        self.path=Path(root)/self.key
        self.path.mkdir(parents=True,exist_ok=True)
        self.specification=specification

    def load(self, lo, hi):
        path=self.path/f'{lo}-{hi}.npz'
        receipt=path.with_suffix('.json')
        if not path.exists() or not receipt.exists():return None
        try:
            data=path.read_bytes()
            record=json.loads(receipt.read_text())
            if (record['query_key']!=self.key or record['sha256']!=hashlib.sha256(data).hexdigest()
                    or record['lo']!=lo or record['hi']!=hi):return None
            with np.load(io.BytesIO(data),allow_pickle=False) as arrays:
                values=arrays['entropy']
                residual=float(arrays['mass_residual'])
            if (values.shape!=(len(self.specification['cadences']),hi-lo)
                    or not np.isfinite(values).all() or values.min() < -1e-12
                    or not 0<=residual<=1e-11):return None
            return values,residual
        except (OSError,ValueError,KeyError):
            return None

    def save(self, lo, hi, values, residual):
        buffer=io.BytesIO()
        np.savez_compressed(buffer,entropy=values,mass_residual=residual)
        data=buffer.getvalue()
        path=self.path/f'{lo}-{hi}.npz'
        record={'query_key':self.key,'lo':lo,'hi':hi,'sha256':hashlib.sha256(data).hexdigest(),
                'contains_transition_kernel':False,'specification':self.specification}
        for destination,payload in ((path,data),(path.with_suffix('.json'),json.dumps(record,sort_keys=True).encode())):
            temporary=destination.with_name(destination.name+'.'+uuid4().hex+'.tmp')
            temporary.write_bytes(payload)
            for attempt in range(8):
                try:
                    os.replace(temporary,destination)
                    break
                except PermissionError:
                    if attempt==7:raise
                    sleep(.02*(attempt+1))

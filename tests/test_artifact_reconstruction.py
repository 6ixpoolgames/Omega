import importlib.util
from pathlib import Path
import numpy as np
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/reconstruct_artifact.py'
spec=importlib.util.spec_from_file_location('rebuild_archive',SCRIPT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_local_kernels_rebuild_without_existing_raw_archive(tmp_path):
    arrays=module.rebuild('local-flow')
    assert len(arrays)==99
    assert arrays['sensor_d4_K'].shape==(6,64,64)
    archive=tmp_path/'reconstructed.npz'
    np.savez_compressed(archive,**arrays)
    checked=module.verify(arrays,archive)
    assert all(row['exact'] for row in checked.values())


def test_verification_rejects_wrong_values_and_missing_fields(tmp_path):
    path=tmp_path/'expected.npz';np.savez(path,states=np.array([1,2]),p=np.array([.25,.75]))
    with pytest.raises(AssertionError,match='integer'):
        module.verify({'states':np.array([1,3]),'p':np.array([.25,.75])},path)
    with pytest.raises(AssertionError,match='field'):
        module.verify({'states':np.array([1,2])},path)


def test_unknown_artifact_cannot_trigger_arbitrary_reconstruction():
    with pytest.raises(ValueError,match='Unknown'):
        module.rebuild('../../unregistered')

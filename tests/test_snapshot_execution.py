from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from omega_v2.testbed.workflow.manifest import freeze_bundle, semantic_keys, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen
from omega_v2.testbed.workflow.artifacts import ArtifactIndex, dry_run_eviction
import hashlib


class SnapshotExecutionTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path]:
        repo = base / "fixture-repo"
        (repo / "fixture_pkg").mkdir(parents=True)
        (repo / "scripts").mkdir()
        (repo / "fixture_pkg" / "__init__.py").write_text("", encoding="utf-8")
        live_module = repo / "fixture_pkg" / "value.py"
        live_module.write_text("VALUE = 'frozen'\n", encoding="utf-8")
        worker = repo / "worker.py"
        worker.write_text(
            "import json, pathlib, sys, time\n"
            "if sys.stdin.readline().strip() != 'GO': raise SystemExit('missing GO')\n"
            "root = pathlib.Path(__file__).resolve().parent\n"
            "sys.path.insert(0, str(root))\n"
            "from fixture_pkg import value\n"
            "if '--sleep' in sys.argv: time.sleep(5)\n"
            "out = pathlib.Path(sys.argv[1])\n"
            "out.write_text(json.dumps({'value': value.VALUE, 'module': value.__file__}))\n",
            encoding="utf-8")
        original_caps = Path(__file__).resolve().parents[1] / "scripts" / "run_bng_binding_calibration.py"
        shutil.copy2(original_caps, repo / "scripts" / original_caps.name)
        return repo, live_module

    @staticmethod
    def _files() -> list[str]:
        return ["worker.py", "fixture_pkg/__init__.py", "fixture_pkg/value.py",
                "scripts/run_bng_binding_calibration.py"]

    def test_frozen_worker_imports_snapshot_after_live_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            repo, live_module = self._fixture(base)
            out = base / "run"
            freeze_bundle(repo, out, self._files(),
                          {"world": {"rate": 1.0}})
            live_module.write_text("VALUE = 'live edit'\n", encoding="utf-8")
            destination = out / "worker-result.json"
            result = run_frozen(out, "worker.py", [str(destination)],
                                {"seconds": 5, "memory": 256 * 1024 ** 2,
                                 "output_cap": 1024 ** 2})
            self.assertEqual(result["exit_code"], 0)
            observed = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(observed["value"], "frozen")
            self.assertIn(str(out / "source"), observed["module"])
            self.assertEqual(verify_bundle(out)["input_hash"], result["input_hash"])

    def test_bundle_tampering_is_rejected_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            repo, _ = self._fixture(base)
            out = base / "run"
            freeze_bundle(repo, out, self._files(), {})
            (out / "source" / "fixture_pkg" / "value.py").write_text("VALUE = 'tampered'\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_bundle(out)

    def test_timeout_cap_is_bounded(self) -> None:
        if os.name != "nt":
            self.skipTest("the shared process-tree cap runner requires Windows Job Objects")
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            repo, _ = self._fixture(base)
            out = base / "run"
            freeze_bundle(repo, out, self._files(), {})
            result = run_frozen(out, "worker.py", [str(out / "unused.json"), "--sleep"],
                                {"seconds": 0.3, "memory": 256 * 1024 ** 2,
                                 "output_cap": 1024 ** 2})
            self.assertEqual(result["cap_reason"], "wall_cap")
            self.assertNotEqual(result["exit_code"], 0)

    def test_output_tree_inside_repo_is_allowed_and_bundle_is_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, _ = self._fixture(Path(temp))
            out = repo / "results" / "local_runs" / "lushness_testbed" / "fixture-run"
            out.mkdir(parents=True)
            manifest = freeze_bundle(repo, out, self._files(), {"frozen": True})
            self.assertEqual(verify_bundle(out)["input_hash"], manifest["input_hash"])
            with self.assertRaises(FileExistsError):
                freeze_bundle(repo, out, self._files(), {"frozen": False})


class SemanticKeysAndEvictionTests(unittest.TestCase):
    def test_readout_change_preserves_operator_but_rate_change_invalidates_it(self) -> None:
        common = {"controller": {"policy": "fixed"},
                  "measurement": {"grain": "state", "cadence": 0.25},
                  "queries": {"horizons": [1, 4]}, "sources": {"worker.py": "abc"}}
        first = semantic_keys(world={"rate": 1.0}, analysis={"readout": "active"}, **common)
        changed_readout = semantic_keys(world={"rate": 1.0}, analysis={"readout": "closure"}, **common)
        changed_rate = semantic_keys(world={"rate": 2.0}, analysis={"readout": "active"}, **common)
        self.assertEqual(first["operator_hash"], changed_readout["operator_hash"])
        self.assertEqual(first["query_hash"], changed_readout["query_hash"])
        self.assertNotEqual(first["report_hash"], changed_readout["report_hash"])
        self.assertNotEqual(first["operator_hash"], changed_rate["operator_hash"])
        grouped_sources = {"operator": {"physics.py": "stable"},
                           "analysis": {"closure_readout.py": "v1"}}
        grouped = semantic_keys({"rate": 1.0}, common["controller"], common["measurement"],
                                common["queries"], {"readout": "closure"}, grouped_sources)
        grouped_readout_source = semantic_keys(
            {"rate": 1.0}, common["controller"], common["measurement"], common["queries"],
            {"readout": "closure"}, {"operator": {"physics.py": "stable"},
                                      "analysis": {"closure_readout.py": "v2"}})
        self.assertEqual(grouped["operator_hash"], grouped_readout_source["operator_hash"])
        self.assertNotEqual(grouped["report_hash"], grouped_readout_source["report_hash"])
        changed_cadence = semantic_keys(world={"rate": 1.0},
                                        measurement={"grain": "state", "cadence": 0.5},
                                        **{k: v for k, v in common.items() if k != "measurement"},
                                        analysis={"readout": "active"})
        self.assertNotEqual(first["operator_hash"], changed_cadence["operator_hash"])

    def test_unsafe_and_protected_eviction_records_are_not_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cache"
            root.mkdir()
            pinned = root / "pinned.bin"
            disposable = root / "disposable.bin"
            pinned.write_bytes(b"123456")
            disposable.write_bytes(b"7890")
            plan = dry_run_eviction(root, [
                {"artifact_id": "pinned", "path": pinned, "bytes": 6,
                 "pinned": True, "last_used": 1},
                {"artifact_id": "scratch", "path": "disposable.bin", "bytes": 4,
                 "retention":"cache", "last_used": 2}], budget=8, target=5)
            self.assertEqual([x["artifact_id"] for x in plan["eviction_candidates"]], ["scratch"])
            self.assertFalse(plan["deleted"])
            self.assertTrue(pinned.exists())
            self.assertTrue(disposable.exists())
            with self.assertRaisesRegex(ValueError, "escapes cache root"):
                dry_run_eviction(root, [{"path": "../outside.bin", "bytes": 1}], budget=0, target=0)

    def test_cache_hit_requires_complete_run_and_intact_hashed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            payload = base / "result.json"
            payload.write_text('{"result": 1}\n', encoding="utf-8")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            index = ArtifactIndex(base / "runs.sqlite")
            index.register_run("r1", status="complete", manifest={"input_hash": "x"},
                               input_hash="x", cache_key="op")
            index.register_artifact("a1", payload, bytes=payload.stat().st_size,
                                    retention="cache", sha256=digest, run_id="r1")
            self.assertIsNotNone(index.cache_manifest("op"))
            payload.write_text('{"result": 2}\n', encoding="utf-8")
            self.assertIsNone(index.cache_manifest("op"))


if __name__ == "__main__":
    unittest.main()

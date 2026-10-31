import tempfile
import unittest
from pathlib import Path

from frameforge.core import inspect, manifests


class UnrealCandidateTests(unittest.TestCase):
    def test_unreal_detection_is_candidate_and_nonblocking(self):
        manifest = manifests()["unreal-engine"]
        self.assertEqual(manifest["evidence_level"], "candidate")
        self.assertGreaterEqual(len(manifest["sources"]), 4)

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "MyGame.uproject").write_text("{}", encoding="utf-8")
            (project / "Plugins").mkdir()
            (project / "Source").mkdir()
            report = inspect(project)

        self.assertIn("unreal-engine", [item["plugin_id"] for item in report["suggested_plugins"]])
        self.assertEqual(report["selected_plugins"], [])
        self.assertEqual({item["rule_id"] for item in report["advisories"] if item['plugin_id']=='unreal-engine'}, {'unreal-project-plugins','unreal-source-modules'})
        self.assertFalse(report["blocking"])

    def test_unreal_negative_case(self):
        with tempfile.TemporaryDirectory() as directory:
            report = inspect(Path(directory))
        self.assertNotIn("unreal-engine", [item["plugin_id"] for item in report["suggested_plugins"]])


    def test_unreal_detection_supports_custom_descriptor_name_without_recursion(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            nested = project / "nested"
            nested.mkdir()
            (nested / "Nested.uproject").write_text("{}", encoding="utf-8")
            report = inspect(project)
        self.assertNotIn("unreal-engine", [item["plugin_id"] for item in report["suggested_plugins"]])


    def test_unreal_descriptor_glob_does_not_follow_symlink(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            project = Path(directory)
            external = Path(outside) / "External.uproject"
            external.write_text("{}", encoding="utf-8")
            try:
                (project / "Linked.uproject").symlink_to(external)
            except OSError:
                self.skipTest("symlink creation is not available")
            report = inspect(project)
        self.assertNotIn("unreal-engine", [item["plugin_id"] for item in report["suggested_plugins"]])

    def test_unreal_descriptor_glob_rejects_parent_traversal(self):
        import json
        from frameforge.core import manifests
        with tempfile.TemporaryDirectory() as directory:
            plugin_dir = Path(directory)
            manifest = json.loads((Path(__file__).resolve().parents[1] / "src/frameforge/manifests/unreal.json").read_text())
            manifest["id"] = "unreal-unsafe-test"
            manifest["detection_globs"] = ["../*.uproject"]
            (plugin_dir / "unsafe.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                manifests(plugin_dir)

    def test_blueprint_only_without_source_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "project.uproject").write_text("{}", encoding="utf-8")
            report = inspect(project)
        source_rule = next(item for item in report['advisories'] if item['rule_id'] == 'unreal-source-modules')
        self.assertEqual(source_rule['evidence'], [])

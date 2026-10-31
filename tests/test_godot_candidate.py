import tempfile
import unittest
from pathlib import Path

from frameforge.core import inspect, manifests


class GodotCandidateTests(unittest.TestCase):
    def test_godot_detection_is_candidate_and_nonblocking(self):
        manifest = manifests()["godot"]
        self.assertEqual(manifest["evidence_level"], "candidate")
        self.assertGreaterEqual(len(manifest["sources"]), 4)

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "project.godot").write_text("config_version=5\n", encoding="utf-8")
            (project / "addons").mkdir()
            report = inspect(project)

        self.assertIn("godot", [item["plugin_id"] for item in report["suggested_plugins"]])
        self.assertEqual(report["selected_plugins"], [])
        self.assertTrue(any(item["rule_id"] == "godot-addons" for item in report["advisories"]))
        self.assertFalse(report["blocking"])

    def test_non_godot_project_is_not_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            report = inspect(Path(directory))
        self.assertNotIn("godot", [item["plugin_id"] for item in report["suggested_plugins"]])

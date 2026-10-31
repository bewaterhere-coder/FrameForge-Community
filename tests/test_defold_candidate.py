import tempfile
import unittest
from pathlib import Path

from frameforge.core import inspect, manifests


class DefoldCandidateTests(unittest.TestCase):
    def test_defold_detection_is_candidate_and_nonblocking(self):
        manifest = manifests()["defold"]
        self.assertEqual(manifest["evidence_level"], "candidate")
        self.assertEqual(manifest["detection"], [["game.project"]])
        self.assertTrue(any(source["publisher"] == "Defold" for source in manifest["sources"]))

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "game.project").write_text("[project]\ntitle = Sample\n", encoding="utf-8")
            report = inspect(project)

        self.assertIn("defold", [item["plugin_id"] for item in report["suggested_plugins"]])
        self.assertEqual(report["selected_plugins"], [])
        self.assertFalse(report["blocking"])

    def test_non_defold_project_is_not_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "project.godot").write_text("config_version=5\n", encoding="utf-8")
            report = inspect(project)
        self.assertNotIn("defold", [item["plugin_id"] for item in report["suggested_plugins"]])

    def test_defold_candidate_does_not_require_assumed_directory_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "game.project").write_text("[project]\n", encoding="utf-8")
            (project / "custom-content-layout").mkdir()
            report = inspect(project)
        self.assertIn("defold", [item["plugin_id"] for item in report["suggested_plugins"]])
        self.assertEqual(report["selected_plugins"], [])

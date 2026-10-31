import tempfile
import unittest
from pathlib import Path

from frameforge.core import inspect, manifests


class PublicPluginExampleTests(unittest.TestCase):
    def test_example_manifest_loads_and_discovery_does_not_activate(self):
        repo = Path(__file__).resolve().parents[1]
        plugin_dir = repo / "examples" / "plugin-manifests"
        catalog = manifests(plugin_dir)
        self.assertIn("example-engine", catalog)

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "project.config").write_text("example-engine", encoding="utf-8")
            report = inspect(project, plugin_dir=plugin_dir)

        self.assertIn("example-engine", [item["plugin_id"] for item in report["suggested_plugins"]])
        self.assertEqual(report["selected_plugins"], [])
        self.assertFalse(report["blocking"])

"""Independent acceptance contrast: positive defect, ordinary advice, insufficient evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class AcceptanceMatrix(unittest.TestCase):
    def _project(self, root, engine, selected=True):
        if engine == "unity":
            f = root / "ProjectSettings/ProjectVersion.txt"
            f.parent.mkdir(parents=True)
            f.write_text("6000.0")
        else:
            (root / "Dockerfile").write_text("FROM cloudwu/skynet")
        if selected:
            p = root / ".frameforge/profile.json"
            p.parent.mkdir()
            p.write_text(json.dumps({"schema_version": 1, "selected_plugins": [
                {"id": engine, "version": "1.0.0"}]}))

    def test_confirmed_assembly_cycle_is_specific_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "unity")
            assets = root / "Assets/Code"
            assets.mkdir(parents=True)
            (assets / "A.asmdef").write_text(json.dumps({"name": "A", "references": ["B"]}))
            (assets / "B.asmdef").write_text(json.dumps({"name": "B", "references": ["A"]}))
            finding = inspect(root)["structural_observations"][0]
            self.assertEqual(finding["status"], "review_needed")
            self.assertEqual(finding["evidence"], [{"assemblies": ["A", "B"]}])
            self.assertFalse(finding["blocking"])

    def test_normal_assembly_has_no_defect_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "unity")
            assets = root / "Assets/Code"
            assets.mkdir(parents=True)
            (assets / "A.asmdef").write_text(json.dumps({"name": "A", "references": ["B"]}))
            (assets / "B.asmdef").write_text(json.dumps({"name": "B", "references": []}))
            finding = inspect(root)["structural_observations"][0]
            self.assertEqual(finding["status"], "no_cycle_in_resolved_names")
            self.assertEqual(finding["evidence"], [])

    def test_unbound_transaction_is_unknown_not_defect(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "skynet")
            finding = inspect(root)["structural_observations"][0]
            self.assertEqual(finding["status"], "not_evaluated")
            self.assertFalse(finding["blocking"])

    def test_no_selection_has_no_structural_check(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "unity", selected=False)
            self.assertEqual(inspect(root)["structural_observations"], [])

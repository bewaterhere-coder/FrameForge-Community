import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class ArtUiTests(unittest.TestCase):
    def _root(self, d):
        root = Path(d)
        (root / 'Assets/Art/UI').mkdir(parents=True)
        return root

    def test_discovery_does_not_activate(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            output = inspect(root)
            self.assertIn('art-ui', [x['plugin_id'] for x in output['suggested_plugins']])
            self.assertFalse(output['blocking'])
            self.assertEqual(output['selected_plugins'], [])
            self.assertEqual(output['professional_guidance'], [])

    def test_selected_plugin_with_project_standard(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / 'Assets/Art/UI/Common').mkdir()
            (root / 'docs').mkdir()
            (root / 'docs/art-direction.md').write_text('Project-owned art standard')
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1,
                'selected_plugins': [{'id': 'art-ui', 'version': '1.0.0'}],
                'standards': {'art-ui': 'docs/art-direction.md'}}))
            result = inspect(root)
            self.assertFalse(result['blocking'])
            self.assertEqual(result['warnings'], [])
            checks = [x for x in result['advisories'] if x['plugin_id'] == 'art-ui']
            self.assertEqual(len(checks), 3)
            self.assertEqual(checks[0]['status'], 'evidence_found')
            self.assertEqual(checks[0]['evidence'], ['Assets/Art/UI/Common'])

    def test_missing_standard_is_warning_not_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1,
                'selected_plugins': [{'id': 'art-ui', 'version': '1.0.0'}]}))
            output = inspect(root)
            self.assertIn('STANDARD_MISSING', [x['code'] for x in output['warnings']])
            self.assertFalse(output['blocking'])

    def test_symlink_outside_project_not_evidence(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root = self._root(d)
            (root / 'Assets/Art/UI/Common').symlink_to(outside, target_is_directory=True)
            checks = [x for x in inspect(root)['advisories'] if x['plugin_id']=='art-ui']
            self.assertEqual(checks[0]['status'], 'review_recommended')
    def test_directory_evidence_is_not_conformance(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / 'Assets/Art/UI/Common').mkdir()
            result = inspect(root)
            item = next(x for x in result['advisories'] if x['rule_id'] == 'art-ui-shared-components')
            self.assertEqual(item['status'], 'evidence_found')
            self.assertEqual(item['confidence'], 'file_presence_only')
            self.assertEqual(item['activation'], 'preview_only')
            self.assertEqual(result['selected_plugins'], [])
            self.assertFalse(result['blocking'])

    def test_missing_ui_candidate_is_not_confirmed_gap(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            result = inspect(root)
            item = next(x for x in result['advisories'] if x['rule_id'] == 'art-ui-shared-components')
            self.assertEqual(item['status'], 'review_recommended')
            self.assertEqual(item['evidence'], [])
            self.assertFalse(result['blocking'])

    def test_unavailable_standard_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1,
                'selected_plugins': [{'id': 'art-ui', 'version': '1.0.0'}],
                'standards': {'art-ui': 'docs/nonexistent-art.md'}}))
            result = inspect(root)
            self.assertIn('STANDARD_UNAVAILABLE', [x['code'] for x in result['warnings']])
            self.assertFalse(result['blocking'])

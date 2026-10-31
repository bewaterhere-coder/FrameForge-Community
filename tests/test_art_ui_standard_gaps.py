import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class ArtUiStandardGaps(unittest.TestCase):
    def create(self, root, clause='Use shared UI assets', paths=None, enabled=True):
        (root/'Assets/Art/UI/Common').mkdir(parents=True)
        (root/'docs').mkdir()
        (root/'docs/art.md').write_text(clause+'\n')
        (root/'.frameforge').mkdir()
        (root/'.frameforge/profile.json').write_text(json.dumps({
            'schema_version': 1,
            'selected_plugins': [{'id':'art-ui','version':'1.0.0'}] if enabled else [],
            'standards': {'art-ui':'docs/art.md'},
            'art_ui_checks': [{'id':'reuse','clause':'Use shared UI assets','evidence_paths':paths or []}]}))
    def test_clause_located(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root, paths=['Assets/Art/UI/Common'])
            r=inspect(root)
            self.assertEqual(r['art_ui_standard_gaps'][0]['status'],'review_required')
            self.assertEqual(r['art_ui_standard_gaps'][0]['clause_lines'],[1])
            self.assertFalse(r['blocking'])
    def test_clause_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root,clause='Unrelated rule')
            r=inspect(root)
            self.assertEqual(r['art_ui_standard_gaps'][0]['status'],'clause_not_found')
            self.assertFalse(r['blocking'])
    def test_evidence_missing_is_not_violation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root,paths=['Assets/Art/UI/Missing'])
            self.assertEqual(inspect(root)['art_ui_standard_gaps'][0]['status'],'evidence_not_found')
    def test_no_activation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root,enabled=False)
            self.assertEqual(inspect(root)['art_ui_standard_gaps'],[])
    def test_invalid_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root)
            p=root/'.frameforge/profile.json'
            data=json.loads(p.read_text()); data['art_ui_checks'][0]['evidence_paths']=['../outside']
            p.write_text(json.dumps(data))
            self.assertIn('ART_UI_CHECKS_INVALID',[x['code'] for x in inspect(root)['warnings']])
    def test_ambiguous_clause(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root,clause='Use shared UI assets\nUse shared UI assets')
            self.assertEqual(inspect(root)['art_ui_standard_gaps'][0]['status'],'clause_ambiguous')

    def test_invalid_optional_checks_preserve_selected_plugins(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root)
            p=root/'.frameforge/profile.json'; data=json.loads(p.read_text())
            data['art_ui_checks'][0]['evidence_paths']=['../outside']
            p.write_text(json.dumps(data))
            result=inspect(root)
            self.assertEqual(result['selected_plugins'][0]['id'],'art-ui')
            self.assertEqual(result['art_ui_standard_gaps'],[])
            self.assertFalse(result['blocking'])

    def test_symlinked_parent_is_not_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root)
            common=root/'Assets/Art/UI/Common'
            common.rmdir()
            actual=root/'actual'; actual.mkdir()
            common.symlink_to(actual, target_is_directory=True)
            result=inspect(root)
            self.assertEqual(result['art_ui_standard_gaps'][0]['status'],'review_required')
            self.assertEqual(result['art_ui_standard_gaps'][0]['evidence'],[])

    def test_symlinked_standard_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.create(root)
            actual=root/'docs/art.md'; actual.rename(root/'docs/real.md')
            actual.symlink_to(root/'docs/real.md')
            self.assertEqual(inspect(root)['art_ui_standard_gaps'][0]['status'],'standard_unavailable')

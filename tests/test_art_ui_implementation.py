import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect

class EvidenceTests(unittest.TestCase):
    def setup_project(self, root, signal='expected-token', path='Assets/UI/Visual.asset'):
        (root/'Assets/Art/UI').mkdir(parents=True)
        (root/'Assets/UI').mkdir(parents=True)
        (root/'docs').mkdir()
        (root/'docs/art.md').write_text('Asset contract clause\n')
        (root/'Assets/UI/Visual.asset').write_text('expected-token\n')
        (root/'.frameforge').mkdir()
        data={'schema_version':1,'selected_plugins':[{'id':'art-ui','version':'1.0.0'}],
              'standards':{'art-ui':'docs/art.md'},
              'art_ui_checks':[{'id':'asset','clause':'Asset contract clause','evidence_paths':[]}],
              'art_ui_implementation_checks':[{'check_id':'asset','path':path,'contains':signal}]}
        (root/'.frameforge/profile.json').write_text(json.dumps(data))
    def test_signal_and_nonmatching(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.setup_project(p)
            self.assertEqual(inspect(p)['art_ui_implementation_evidence'][0]['status'],'signal_found')
            data=json.loads((p/'.frameforge/profile.json').read_text())
            data['art_ui_implementation_checks'][0]['contains']='other'
            (p/'.frameforge/profile.json').write_text(json.dumps(data))
            r=inspect(p)
            self.assertEqual(r['art_ui_implementation_evidence'][0]['status'],'signal_not_found')
            self.assertFalse(r['blocking'])
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.setup_project(p,path='Assets/UI/missing.asset')
            self.assertEqual(inspect(p)['art_ui_implementation_evidence'][0]['status'],'source_unavailable')
    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            p=Path(d);self.setup_project(p)
            (p/'Assets/UI/Visual.asset').unlink()
            t=Path(out)/'external.asset';t.write_text('expected-token')
            (p/'Assets/UI/Visual.asset').symlink_to(t)
            self.assertEqual(inspect(p)['art_ui_implementation_evidence'][0]['status'],'source_unavailable')
    def test_invalid_optional_config_preserves_plugins(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.setup_project(p,path='../escape')
            r=inspect(p)
            self.assertEqual(r['selected_plugins'][0]['id'],'art-ui')
            self.assertEqual(r['art_ui_implementation_evidence'],[])
            self.assertIn('ART_UI_IMPLEMENTATION_CHECKS_INVALID',[w['code'] for w in r['warnings']])
    def test_unbound_clause_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.setup_project(p)
            (p/'docs/art.md').write_text('other clause')
            self.assertEqual(inspect(p)['art_ui_implementation_evidence'][0]['status'],'reference_unverified')

    def test_authoritative_standard_cannot_be_implementation_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.setup_project(p)
            profile=p/'.frameforge/profile.json'
            data=json.loads(profile.read_text())
            data['art_ui_implementation_checks'][0]['path']='docs/art.md'
            profile.write_text(json.dumps(data))
            r=inspect(p)
            self.assertEqual(r['art_ui_implementation_evidence'],[])
            self.assertIn('ART_UI_IMPLEMENTATION_CHECKS_INVALID',[w['code'] for w in r['warnings']])
            self.assertEqual(r['selected_plugins'][0]['id'],'art-ui')
            self.assertFalse(r['blocking'])

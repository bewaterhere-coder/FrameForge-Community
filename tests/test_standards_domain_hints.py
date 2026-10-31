import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect

class DomainHintsTests(unittest.TestCase):
    def test_hints_are_explainable_not_authority(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'docs').mkdir();(p/'.frameforge').mkdir()
            for n in ('CODE-ARCHITECTURE.md','UI-ASSET-规范.md','TEST-STANDARDS.md','STARTUP.md'):
                (p/'docs'/n).write_text('not verified')
            (p/'.frameforge/profile.json').write_text(json.dumps({'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'docs/CODE-ARCHITECTURE.md'}}))
            x=inspect(p);c={y['reference']:y for y in x['standard_candidates']['candidates']}
            self.assertIn('architecture',c['docs/CODE-ARCHITECTURE.md']['domain_hints'])
            self.assertEqual(c['docs/UI-ASSET-规范.md']['domain_hints'],['art-ui','asset-pipeline'])
            self.assertEqual(c['docs/TEST-STANDARDS.md']['domain_hints'],['testing'])
            self.assertNotIn('docs/STARTUP.md',c)
            a=x['standard_authority_review']['items'][0]
            self.assertEqual(a['domain_hint_matches'],[])
            self.assertIn('docs/UI-ASSET-规范.md',a['other_candidates'])
            self.assertEqual(a['potential_conflict'],'not_evaluated')
            self.assertFalse(x['blocking'])

    def test_unbound_multi_domain_hint_without_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'docs').mkdir()
            (p/'docs/UI-ASSET-规范.md').write_text('Draft')
            x=inspect(p)
            c=x['standard_candidates']['candidates'][0]
            self.assertEqual(c['domain_hints'],['art-ui','asset-pipeline'])
            self.assertEqual(c['owner_approved'],'unverified')
            self.assertEqual(x['standard_authority_review']['items'][0]['other_candidates'],['docs/UI-ASSET-规范.md'])
            self.assertFalse(x['standard_authority_review']['content_conflicts_verified'])

    def test_legacy_output_fields_remain_and_all_candidates_retained(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'docs').mkdir();(p/'.frameforge').mkdir()
            (p/'docs/architecture.md').write_text('Design')
            (p/'docs/UI-规范.md').write_text('Visual')
            (p/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'docs/architecture.md'}}))
            x=inspect(p)
            self.assertEqual(x['schema_version'],1)
            self.assertEqual(x['standard_sources'][0]['status'],'bound_reference')
            self.assertEqual(x['standard_authority_review']['items'][0]['other_candidates'],['docs/UI-规范.md'])
            self.assertEqual(x['standard_authority_review']['items'][0]['domain_hint_matches'],[])
            self.assertEqual(x['warnings'],[])
            self.assertFalse(x['blocking'])

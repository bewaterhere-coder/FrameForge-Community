import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect

class AuthorityTests(unittest.TestCase):
    def test_bound_and_alternatives_never_claim_conflict_or_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'docs').mkdir();(p/'.frameforge').mkdir()
            (p/'docs/architecture-A.md').write_text('MVP')
            (p/'docs/architecture-B.md').write_text('ECS')
            (p/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'docs/architecture-A.md'}}))
            result=inspect(p);entry=result['standard_authority_review']['items'][0]
            self.assertEqual(entry['bound_reference'],'docs/architecture-A.md')
            self.assertEqual(entry['other_candidates'],['docs/architecture-B.md'])
            self.assertEqual(entry['potential_conflict'],'not_evaluated')
            self.assertFalse(result['standard_authority_review']['content_conflicts_verified'])
            self.assertEqual(entry['authority'],'owner_confirmation_unverified')
            self.assertFalse(result['blocking'])

    def test_only_candidates_require_owner_decision(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'architecture.md').write_text('Candidate')
            result=inspect(p);entry=result['standard_authority_review']['items'][0]
            self.assertIsNone(entry['bound_reference'])
            self.assertEqual(entry['action'],'confirm_authoritative_project_standard')
            self.assertEqual(result['warnings'][0]['code'],'PROFILE_MISSING')

    def test_invalid_binding_does_not_authorize_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.frameforge').mkdir();(p/'architecture.md').write_text('Candidate')
            (p/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'missing.md'}}))
            result=inspect(p);entry=result['standard_authority_review']['items'][0]
            self.assertEqual(entry['bound_status'],'reference_unavailable')
            self.assertEqual(entry['other_candidates'],['architecture.md'])
            self.assertEqual(entry['potential_conflict'],'not_evaluated')

    def test_separately_bound_domains_are_not_mutual_alternatives(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'docs').mkdir();(p/'.frameforge').mkdir()
            (p/'docs/architecture.md').write_text('MVP')
            (p/'docs/UI标准.md').write_text('UI only')
            (p/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'docs/architecture.md','art-ui':'docs/UI标准.md'}}))
            result=inspect(p)
            items=result['standard_authority_review']['items']
            self.assertEqual(len(items),2)
            self.assertTrue(all(item['other_candidates']==[] for item in items))
            self.assertTrue(all(item['candidate_relation']=='unclassified_project_wide' for item in items))
            self.assertTrue(all(item['potential_conflict']=='not_evaluated' for item in items))

    def test_project_roots_remain_isolated(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ('one','two'):
                p=Path(d)/name;p.mkdir();(p/'docs').mkdir();(p/'.frameforge').mkdir()
                (p/'docs/architecture.md').write_text(name)
                (p/'.frameforge/profile.json').write_text(json.dumps({
                    'schema_version':1,'selected_plugins':[],
                    'standards':{'architecture':'docs/architecture.md'}}))
            a=inspect(Path(d)/'one')['standard_authority_review']
            b=inspect(Path(d)/'two')['standard_authority_review']
            self.assertEqual(a,b)
            self.assertEqual(a['items'][0]['other_candidates'],[])
            self.assertFalse(a['content_conflicts_verified'])

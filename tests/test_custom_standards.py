import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class CustomStandardsTests(unittest.TestCase):
    def test_two_independent_project_standards(self):
        with tempfile.TemporaryDirectory() as base:
            for name, rule in [('alpha', 'MVP is required'), ('beta', 'ECS is required')]:
                root = Path(base)/name
                (root/'.frameforge').mkdir(parents=True)
                (root/'Assets').mkdir()
                (root/'Assets/Root.cs').write_text(rule)
                (root/'docs').mkdir()
                (root/'docs/architecture.md').write_text(rule)
                (root/'ProjectSettings').mkdir()
                (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
                (root/'.frameforge/profile.json').write_text(json.dumps({
                    'schema_version': 1,
                    'selected_plugins': [{'id': 'unity', 'version': '1.0.0'}],
                    'standards': {'architecture': 'docs/architecture.md'},
                    'semantic_rules': [{'id': 'rule', 'plugin_id': 'unity',
                        'topic': 'Architecture', 'recommendation': 'Review',
                        'language': 'csharp', 'paths': ['Assets/Root.cs'],
                        'tokens': [rule]}],
                    'check_clauses': {'rule': {
                        'id': 'RULE-1', 'reference': 'docs/architecture.md',
                        'text': rule}}}))
                result = inspect(root)
                self.assertEqual(result['standard_sources'][0]['status'], 'bound_reference')
                self.assertEqual(result['standard_sources'][0]['owner_approved'], 'unverified')
                self.assertEqual(result['clause_coverage'][0]['status'], 'evidence_observed')
                self.assertEqual(result['clause_coverage'][0]['compliance'], 'unverified')
                self.assertEqual(result['warnings'], [])
                self.assertFalse(result['blocking'])

    def test_missing_and_candidate_are_not_approved(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'ARCHITECTURE.md').write_text('Candidate only')
            report = inspect(root)
            self.assertEqual(report['standard_sources'][0]['status'], 'candidate_reference')
            self.assertEqual(report['standard_sources'][0]['owner_approved'], 'unverified')
            self.assertEqual(report['warnings'][0]['code'], 'PROFILE_MISSING')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1, 'selected_plugins': [],
                'standards': {'architecture': 'missing.md'}}))
            report = inspect(root)
            self.assertEqual(report['standard_sources'][0]['status'], 'reference_unavailable')
            self.assertEqual(report['standard_sources'][0]['owner_approved'], 'unverified')

    def test_outside_symlink_never_becomes_valid_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'project'
            root.mkdir()
            outside = Path(d)/'outside.md'
            outside.write_text('not authorized')
            (root/'link.md').symlink_to(outside)
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1, 'selected_plugins': [],
                'standards': {'architecture': 'link.md'}}))
            report = inspect(root)
            self.assertEqual(report['standard_sources'][0]['status'], 'reference_unavailable')
            self.assertFalse(report['blocking'])

    def test_bound_clause_without_semantic_check_is_not_evaluated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'docs').mkdir()
            (root/'docs/rules.md').write_text('Custom project rule')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1, 'selected_plugins': [],
                'standards': {'architecture': 'docs/rules.md'},
                'check_clauses': {'r1': {'id': 'R1',
                    'reference': 'docs/rules.md', 'text': 'Custom project rule'}}}))
            result = inspect(root)
            self.assertEqual(result['clause_coverage'][0]['status'], 'not_evaluated')
            self.assertEqual(result['clause_coverage'][0]['compliance'], 'unverified')
            self.assertFalse(result['blocking'])

    def test_old_result_fields_and_warning_shape_remain(self):
        with tempfile.TemporaryDirectory() as d:
            result=inspect(Path(d))
            self.assertEqual(result['schema_version'], 1)
            self.assertEqual(result['selected_plugins'], [])
            self.assertEqual(result['standards'], {})
            self.assertEqual(result['discovered_standards'], {})
            self.assertEqual(result['semantic_checks'], [])
            self.assertEqual(result['warnings'][0]['code'], 'PROFILE_MISSING')
            self.assertIn('remediation', result['warnings'][0])
            self.assertFalse(result['blocking'])

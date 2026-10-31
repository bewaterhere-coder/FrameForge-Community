"""First-use AI Host regression: no Profile, explicit opt-in, fresh recheck."""
import json
import tempfile
import unittest
from pathlib import Path

from frameforge.host_adapter import inspect_project, explain_warnings, verify_remediation


class FirstUseJourneyTests(unittest.TestCase):
    def test_unity_first_use_and_owner_configured_recheck(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'ProjectSettings').mkdir()
            (root / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
            before = inspect_project(root)
            self.assertEqual([p['plugin_id'] for p in before['suggested_plugins']], ['unity'])
            self.assertEqual(before['selected_plugins'], [])
            self.assertEqual([w['code'] for w in before['warnings']],
                             ['PROFILE_MISSING', 'STANDARD_SUGGESTED'])
            self.assertEqual(before['standard_sources'], [])
            self.assertEqual(before['clause_coverage'], [])
            self.assertFalse(before['blocking'])
            self.assertFalse((root / '.frameforge').exists())
            self.assertEqual(explain_warnings(root)['warnings'], before['warnings'])
            self.assertTrue(all(w['remediation']['auto_apply'] is False
                                for w in before['warnings']))

            # This simulates a separate project-owner action, NOT a Host mutation.
            (root / 'docs').mkdir()
            (root / 'docs/architecture.md').write_text('# Owner-provided design')
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1,
                'selected_plugins': [{'id': 'unity', 'version': '1.0.0'}],
                'standards': {'architecture': 'docs/architecture.md'},
            }))
            after = inspect_project(root)
            self.assertEqual(after['selected_plugins'], [{'id': 'unity', 'version': '1.0.0'}])
            self.assertEqual(after['warnings'], [])
            self.assertEqual(after['standard_sources'][0]['status'], 'bound_reference')
            self.assertEqual(after['standard_sources'][0]['owner_approved'], 'unverified')
            self.assertEqual(after['standard_authority_review']['items'][0]['potential_conflict'],
                             'not_evaluated')
            self.assertEqual(after['clause_coverage'], [])
            fresh = verify_remediation(root, before['warnings'])
            self.assertEqual(fresh['resolved_codes'], ['PROFILE_MISSING', 'STANDARD_SUGGESTED'])
            self.assertEqual(fresh['remaining_warnings'], [])
            self.assertEqual(fresh['new_codes'], [])
            self.assertEqual(fresh['verification'], 'fresh_readonly_inspection')
            self.assertFalse(fresh['formal_acceptance'])
            self.assertFalse(fresh['blocking'])

    def test_no_unapproved_owner_config_change_is_automatic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'ProjectSettings').mkdir()
            (root / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
            original = inspect_project(root)
            for _ in range(2):
                inspect_project(root)
                explain_warnings(root)
                result = verify_remediation(root, original['warnings'])
                self.assertEqual(result['resolved_codes'], [])
                self.assertEqual(result['remaining_warnings'], original['warnings'])
            self.assertFalse((root / '.frameforge').exists())
            self.assertFalse((root / 'docs').exists())

    def test_partial_remediation_does_not_claim_full_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'ProjectSettings').mkdir()
            (root / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
            before = inspect_project(root)['warnings']
            # Owner creates a valid Profile but does not bind a standard.
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1, 'selected_plugins': [{'id': 'unity', 'version': '1.0.0'}],
                'standards': {},
            }))
            result = verify_remediation(root, before)
            self.assertIn('PROFILE_MISSING', result['resolved_codes'])
            self.assertIn('STANDARD_MISSING', [w['code'] for w in result['remaining_warnings']])
            self.assertIn('STANDARD_MISSING', result['new_codes'])
            self.assertFalse(result['formal_acceptance'])
            self.assertFalse(result['blocking'])

    def test_invalid_standard_reference_keeps_warning_nonblocking(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'ProjectSettings').mkdir()
            (root / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
            before = inspect_project(root)['warnings']
            (root / '.frameforge').mkdir()
            (root / '.frameforge/profile.json').write_text(json.dumps({
                'schema_version': 1, 'selected_plugins': [{'id': 'unity', 'version': '1.0.0'}],
                'standards': {'architecture': 'docs/missing.md'},
            }))
            after = inspect_project(root)
            self.assertEqual(after['standard_sources'][0]['status'], 'reference_unavailable')
            self.assertTrue(after['warnings'])
            verified = verify_remediation(root, before)
            self.assertTrue(verified['remaining_warnings'])
            self.assertFalse(verified['formal_acceptance'])
            self.assertFalse(verified['blocking'])

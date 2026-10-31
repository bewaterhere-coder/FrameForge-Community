import tempfile
import unittest
from pathlib import Path
from frameforge.host_adapter import inspect_project, explain_warnings, verify_remediation


class HostAdapterTests(unittest.TestCase):
    def test_full_readonly_host_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'CMakeLists.txt').write_text('project(Sample)')
            before=inspect_project(root)
            context=explain_warnings(root)
            self.assertEqual(before['warnings'],context['warnings'])
            self.assertEqual([w['code'] for w in context['warnings']],
                             ['PROFILE_MISSING','STANDARD_SUGGESTED'])
            self.assertFalse((root/'.frameforge').exists())
            (root/'ARCHITECTURE.md').write_text('# Project standard')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(
                '{"schema_version":1,"selected_plugins":[{"id":"cpp","version":"1.0.0"}],'
                '"standards":{"architecture":"ARCHITECTURE.md"}}')
            check=verify_remediation(root,before['warnings'])
            self.assertEqual(check['resolved_codes'],['PROFILE_MISSING','STANDARD_SUGGESTED'])
            self.assertEqual(check['remaining_warnings'],[])
            self.assertFalse(check['formal_acceptance'])
            self.assertFalse(check['blocking'])

    def test_not_resolved_when_warning_remains(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            before=inspect_project(root)['warnings']
            check=verify_remediation(root,before)
            self.assertEqual(check['resolved_codes'],[])
            self.assertEqual(check['remaining_warnings'],before)

    def test_new_warning_reported_and_invalid_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            check=verify_remediation(root,[])
            self.assertEqual(check['new_codes'],['PROFILE_MISSING'])
            with self.assertRaises(ValueError):
                verify_remediation(root, [{'message':'missing code'}])
            self.assertFalse((root/'.frameforge').exists())

    def test_same_code_different_issue_is_not_silently_matched(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'.frameforge').mkdir()
            profile=root/'.frameforge/profile.json'
            profile.write_text('{"schema_version":1,"selected_plugins":'
                               '[{"id":"cpp","version":"0.8"}],"standards":{}}')
            before=inspect_project(root)['warnings']
            profile.write_text('{"schema_version":1,"selected_plugins":'
                               '[{"id":"unity","version":"0.8"}],"standards":{}}')
            result=verify_remediation(root,before)
            self.assertIn('PLUGIN_VERSION_MISMATCH',result['resolved_codes'])
            self.assertIn('PLUGIN_VERSION_MISMATCH',result['new_codes'])
            self.assertNotEqual(result['resolved_warnings'],result['new_warnings'])
            self.assertTrue(result['remaining_warnings'])
            self.assertFalse(result['formal_acceptance'])

    def test_rejects_untrustworthy_previous_warning_shape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for invalid in (None,{},[{'code':'X'}],[{'code':' ', 'message':'x'}],
                            [{'code':'X','message':''}],[{'code':'X','message':3}]):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(ValueError):
                        verify_remediation(root,invalid)

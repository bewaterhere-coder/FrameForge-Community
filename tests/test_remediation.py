import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class RemediationTests(unittest.TestCase):
    def test_absent_profile_is_not_auto_fixed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            warning = inspect(root)['warnings'][0]
            self.assertEqual(warning['code'], 'PROFILE_MISSING')
            self.assertFalse(warning['remediation']['auto_apply'])
            self.assertEqual(warning['remediation']['status'], 'needs_review')
            self.assertFalse((root/'.frameforge').exists())

    def test_resolution_requires_project_change_and_recheck(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'CMakeLists.txt').write_text('project(Example)')
            initial = inspect(root)
            self.assertEqual([w['code'] for w in initial['warnings']],
                             ['PROFILE_MISSING', 'STANDARD_SUGGESTED'])
            (root/'ARCHITECTURE.md').write_text('Project-owned architecture')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(
                '{"schema_version":1,"selected_plugins":[{"id":"cpp","version":"1.0.0"}],'
                '"standards":{"architecture":"ARCHITECTURE.md"}}')
            final = inspect(root)
            self.assertEqual(final['warnings'], [])
            self.assertFalse(final['blocking'])

    def test_invalid_reference_requires_explicit_repair(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(
                '{"schema_version":1,"selected_plugins":[{"id":"cpp","version":"1.0.0"}],'
                '"standards":{"architecture":"../outside.md"}}')
            warning = inspect(root)['warnings'][0]
            self.assertEqual(warning['code'], 'STANDARD_UNAVAILABLE')
            self.assertEqual(warning['remediation']['approval'], 'project_owner_confirmation')
            self.assertFalse(warning['remediation']['auto_apply'])

    def test_remediation_does_not_modify_existing_project_configuration(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'CMakeLists.txt').write_text('project(Sample)')
            (root/'.frameforge').mkdir()
            config = root/'.frameforge/profile.json'
            config.write_text('{"schema_version":1,"selected_plugins":[{"id":"cpp","version":"0.0"}],"standards":{"architecture":"docs/absent.md"}}')
            before = config.read_bytes()
            first = inspect(root)
            second = inspect(root)
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual(first['warnings'], second['warnings'])
            self.assertEqual([w['code'] for w in first['warnings']],
                             ['PLUGIN_VERSION_MISMATCH', 'STANDARD_UNAVAILABLE'])
            self.assertTrue(all(w['remediation']['auto_apply'] is False for w in first['warnings']))
            self.assertTrue(all(w['remediation']['status'] == 'needs_review' for w in first['warnings']))

    def test_fabricated_standard_does_not_clear_unrelated_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'CMakeLists.txt').write_text('project(Sample)')
            (root/'.frameforge').mkdir()
            config = root/'.frameforge/profile.json'
            config.write_text('{"schema_version":1,"selected_plugins":[{"id":"cpp","version":"0.0"}],"standards":{"architecture":"docs/arch.md"}}')
            initial = {w['code'] for w in inspect(root)['warnings']}
            self.assertEqual(initial, {'PLUGIN_VERSION_MISMATCH', 'STANDARD_UNAVAILABLE'})
            (root/'docs').mkdir()
            (root/'docs/arch.md').write_text('draft placeholder')
            after = {w['code'] for w in inspect(root)['warnings']}
            self.assertEqual(after, {'PLUGIN_VERSION_MISMATCH'})
            self.assertEqual((root/'docs/arch.md').read_text(), 'draft placeholder')

    def test_unknown_warning_fails_closed_without_suppression(self):
        from frameforge.remediation import advise
        original = [{'code': 'FUTURE_CHECK', 'message': 'Unrecognized risk'}]
        result = advise(original)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['code'], 'FUTURE_CHECK')
        self.assertEqual(result[0]['message'], 'Unrecognized risk')
        self.assertEqual(result[0]['remediation']['approval'], 'human_review')
        self.assertFalse(result[0]['remediation']['auto_apply'])
        self.assertEqual(original, [{'code': 'FUTURE_CHECK', 'message': 'Unrecognized risk'}])

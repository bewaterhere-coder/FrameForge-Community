"""Commit-bound advisory checks do not substitute for formal acceptance."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from frameforge.host_adapter import inspect_for_acceptance


class AcceptanceAdvisoryTests(unittest.TestCase):
    def test_exact_commit_clean_checkout_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], text=True).strip()
            git('init', '-q')
            git('config', 'user.email', 'tester@example.invalid')
            git('config', 'user.name', 'Tester')
            (root/'CMakeLists.txt').write_text('project(Demo)\n')
            git('add', 'CMakeLists.txt')
            git('commit', '-qm', 'test')
            sha = git('rev-parse', 'HEAD')
            result = inspect_for_acceptance(root, sha)
            self.assertEqual(result['repository_commit'], sha)
            self.assertFalse(result['formal_acceptance'])
            self.assertFalse(result['compliance_verified'])
            self.assertFalse(result['blocking'])
            with self.assertRaisesRegex(ValueError, 'does not match'):
                inspect_for_acceptance(root, '0'*40)
            with self.assertRaisesRegex(ValueError, '40-character'):
                inspect_for_acceptance(root, 'main')
            (root/'untracked.txt').write_text('not committed')
            with self.assertRaisesRegex(ValueError, 'not clean'):
                inspect_for_acceptance(root, sha)

    def test_not_a_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'cannot verify'):
                inspect_for_acceptance(directory, 'a'*40)

    def test_explicit_profile_from_another_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], text=True).strip()
            git('init', '-q')
            git('config', 'user.email', 'tester@example.invalid')
            git('config', 'user.name', 'Tester')
            (root/'CMakeLists.txt').write_text('project(Demo)')
            git('add', '.')
            git('commit', '-qm', 'code')
            code_sha = git('rev-parse', 'HEAD')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(
                '{"schema_version":1,"selected_plugins":[],"standards":{}}')
            git('add', '.frameforge/profile.json')
            git('commit', '-qm', 'profile')
            source_sha = git('rev-parse', 'HEAD')
            git('checkout', '-q', code_sha)
            result = inspect_for_acceptance(root, code_sha, profile_source_commit=source_sha)
            self.assertEqual(result['profile_source']['commit'], source_sha)
            self.assertEqual(result['profile_source']['mode'], 'explicit_git_commit')
            self.assertNotIn('PROFILE_MISSING', [w['code'] for w in result['inspection']['warnings']])
            self.assertEqual(result['repository_commit'], code_sha)
            self.assertFalse(result['compliance_verified'])
            with self.assertRaisesRegex(ValueError, 'cannot verify'):
                inspect_for_acceptance(root, code_sha, profile_source_commit='0'*40)

import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import manifests, inspect


class PluginExtensionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plugins = self.root / 'plugins'
        self.plugins.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def add(self, name='custom', manifest=None):
        manifest = manifest or {'id': name, 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']]}
        (self.plugins / (name + '.json')).write_text(json.dumps(manifest))

    def test_external_plugin_detects_without_activation(self):
        self.add()
        (self.root / 'custom.project').touch()
        result = inspect(self.root, self.plugins)
        self.assertIn('custom', {p['plugin_id'] for p in result['suggested_plugins']})
        self.assertEqual(result['selected_plugins'], [])
        self.assertIn('STANDARD_SUGGESTED', [w['code'] for w in result['warnings']])

    def test_external_catalog_is_opt_in(self):
        self.add()
        self.assertNotIn('custom', manifests())
        self.assertIn('custom', manifests(self.plugins))

    def test_collision_rejected(self):
        self.add('unity')
        with self.assertRaisesRegex(ValueError, 'Duplicate plugin'):
            manifests(self.plugins)

    def test_manifest_id_must_match_public_schema(self):
        self.add('bad-id', {'id': 'Bad ID', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin identity'):
            manifests(self.plugins)

    def test_manifest_domain_must_be_nonempty(self):
        self.add('empty-domain', {'id': 'empty-domain', 'version': '1.0.0', 'domain': '', 'standards': ['architecture'], 'detection': [['custom.project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin standards'):
            manifests(self.plugins)

    def test_manifest_paths_reject_windows_backslash_traversal(self):
        self.add('backslash-path', {'id': 'backslash-path', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['..\\\\outside\\\\project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin detection'):
            manifests(self.plugins)

    def test_manifest_paths_reject_windows_drive_prefix(self):
        self.add('drive-path', {'id': 'drive-path', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['C:/outside/project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin detection'):
            manifests(self.plugins)

    def test_manifest_sources_validate_required_fields_and_date(self):
        self.add('bad-source', {'id': 'bad-source', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']], 'sources': [{'publisher': 'Example', 'title': 'Guide', 'url': 'https://example.com', 'engine_versions': '1.x', 'accessed': 'not-a-date'}]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin source date'):
            manifests(self.plugins)

    def test_manifest_professional_guidance_accepts_schema_nonempty_whitespace(self):
        self.add('guidance-space', {'id': 'guidance-space', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']], 'professional_guidance': [{'id': ' ', 'topic': ' ', 'signal': ' ', 'recommendation': ' '}]})
        self.assertIn('guidance-space', manifests(self.plugins))

    def test_bad_manifest_rejected(self):
        self.add('broken', {'id': 'broken', 'version':'1.0.0', 'domain':'code', 'standards':'not-a-list', 'detection':[]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin manifest'):
            manifests(self.plugins)

    def test_nonexistent_extension_dir_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Plugin directory missing'):
            manifests(self.root / 'missing')

    def test_project_not_mutated(self):
        self.add()
        prior = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file())
        inspect(self.root, self.plugins)
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file())
        self.assertEqual(prior, after)

    def test_escape_marker_rejected(self):
        self.add('escape', {'id':'escape','version':'1.0.0','domain':'code','standards':['architecture'],'detection':[['../outside']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin'):
            manifests(self.plugins)

    def test_absolute_marker_rejected(self):
        self.add('absolute', {'id':'absolute','version':'1.0.0','domain':'code','standards':['architecture'],'detection':[['/etc/passwd']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin'):
            manifests(self.plugins)

    def test_symlink_outside_project_not_detected(self):
        outside = self.root.parent / ('frameforge-outside-' + self.root.name)
        outside.write_text('x')
        try:
            (self.root/'custom.project').symlink_to(outside)
            self.add()
            self.assertNotIn('custom', [p['plugin_id'] for p in inspect(self.root, self.plugins)['suggested_plugins']])
        finally:
            outside.unlink()
        self.add('drive-path', {'id': 'drive-path', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['C:/outside/project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin detection'):
            manifests(self.plugins)

    def test_manifest_sources_validate_required_fields_and_date(self):
        self.add('bad-source', {'id': 'bad-source', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']], 'sources': [{'publisher': 'Example', 'title': 'Guide', 'url': 'https://example.com', 'engine_versions': '1.x', 'accessed': 'not-a-date'}]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin source date'):
            manifests(self.plugins)

    def test_manifest_professional_guidance_accepts_schema_nonempty_whitespace(self):
        self.add('guidance-space', {'id': 'guidance-space', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['custom.project']], 'professional_guidance': [{'id': ' ', 'topic': ' ', 'signal': ' ', 'recommendation': ' '}]})
        self.assertIn('guidance-space', manifests(self.plugins))

    def test_bad_manifest_rejected(self):
        self.add('broken', {'id': 'broken', 'version':'1.0.0', 'domain':'code', 'standards':'not-a-list', 'detection':[]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin manifest'):
            manifests(self.plugins)

    def test_nonexistent_extension_dir_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Plugin directory missing'):
            manifests(self.root / 'missing')

    def test_project_not_mutated(self):
        self.add()
        prior = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file())
        inspect(self.root, self.plugins)
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file())
        self.assertEqual(prior, after)

    def test_escape_marker_rejected(self):
        self.add('escape', {'id':'escape','version':'1.0.0','domain':'code','standards':['architecture'],'detection':[['../outside']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin'):
            manifests(self.plugins)

    def test_absolute_marker_rejected(self):
        self.add('absolute', {'id':'absolute','version':'1.0.0','domain':'code','standards':['architecture'],'detection':[['/etc/passwd']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin'):
            manifests(self.plugins)

    def test_symlink_outside_project_not_detected(self):
        outside = self.root.parent / ('frameforge-outside-' + self.root.name)
        outside.write_text('x')
        try:
            (self.root/'custom.project').symlink_to(outside)
            self.add()
            self.assertNotIn('custom', [p['plugin_id'] for p in inspect(self.root, self.plugins)['suggested_plugins']])
        finally:
            outside.unlink()

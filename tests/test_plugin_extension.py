import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import manifests, inspect, _valid_project_path


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
        self.add('backslash-path', {'id': 'backslash-path', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [[r'..\outside\project']]})
        with self.assertRaisesRegex(ValueError, 'Invalid plugin detection'):
            manifests(self.plugins)

    def test_manifest_paths_reject_nul_character(self):
        self.add('nul-path', {'id': 'nul-path', 'version': '1.0.0', 'domain': 'code', 'standards': ['architecture'], 'detection': [['bad\x00path']]})
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

    def test_manifest_professional_guidance_rejects_whitespace_only_fields(self):
        for field in ("id", "topic", "signal", "recommendation"):
            with self.subTest(field=field):
                guidance = {"id": "guidance", "topic": "topic", "signal": "signal",
                            "recommendation": "recommendation"}
                guidance[field] = "   "
                self.add("guidance-space-" + field, {
                    "id": "guidance-space-" + field, "version": "1.0.0",
                    "domain": "code", "standards": ["architecture"],
                    "detection": [["custom.project"]],
                    "professional_guidance": [guidance],
                })
                with self.assertRaisesRegex(ValueError, "Invalid professional guidance"):
                    manifests(self.plugins)

    def test_schema_project_path_pattern_matches_runtime_path_boundary(self):
        import re
        schema_path = Path(__file__).resolve().parents[1] / "docs/plugin-manifest.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        pattern = re.compile(schema["$defs"]["projectPath"]["pattern"])
        guidance_fields = schema["properties"]["professional_guidance"]["items"]["properties"]
        for field in ("id", "topic", "signal", "recommendation"):
            self.assertIsNotNone(re.search(guidance_fields[field]["pattern"], "valid value"))
            self.assertIsNone(re.search(guidance_fields[field]["pattern"], "   "))
        values = ["../outside", "a/../b", "src/../file.cs", r"a\b",
                  "bad\x00path", "/etc/passwd", "C:/outside", "src/file.cs"]
        for value in values:
            with self.subTest(value=repr(value)):
                self.assertEqual(pattern.fullmatch(value) is not None,
                                 _valid_project_path(value))

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

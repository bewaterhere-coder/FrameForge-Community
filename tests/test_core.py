import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect, manifests

class FrameworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def profile(self, plugins, standards=None):
        p=self.root/'.frameforge/profile.json';p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps({'schema_version':1,'selected_plugins':plugins,'standards':standards or {}}))
    def test_documented_profile_example_matches_core_contract(self):
        example = Path(__file__).resolve().parents[1] / 'docs/profile-example.json'
        profile_data = example.read_text(encoding='utf-8')
        result = inspect(self.root, profile_data=profile_data)
        self.assertEqual(
            {item['id'] for item in result['selected_plugins']},
            {'unity', 'art-ui'},
        )
        self.assertNotIn('PROFILE_INVALID', [item['code'] for item in result['warnings']])
        self.assertEqual(result['standards']['architecture'], 'docs/architecture.md')
        self.assertEqual(result['standards']['art-ui'], 'docs/art-direction.md')
        self.assertFalse(result['blocking'])

    def test_empty_nonblocking(self):
        r=inspect(self.root);self.assertFalse(r['blocking']);self.assertEqual(r['warnings'][0]['code'],'PROFILE_MISSING')
    def test_discovery_does_not_activate(self):
        p=self.root/'ProjectSettings/ProjectVersion.txt';p.parent.mkdir();p.write_text('Unity')
        r=inspect(self.root);self.assertEqual(r['suggested_plugins'][0]['plugin_id'],'unity');self.assertEqual(r['selected_plugins'],[])
    def test_missing_architecture_advisory_for_detected_engine(self):
        p=self.root/'ProjectSettings/ProjectVersion.txt';p.parent.mkdir();p.write_text('Unity')
        r=inspect(self.root)
        self.assertEqual([w['code'] for w in r['warnings']], ['PROFILE_MISSING','STANDARD_SUGGESTED'])
        self.assertFalse(r['blocking'])
    def test_existing_architecture_does_not_trigger_missing_warning(self):
        p=self.root/'ProjectSettings/ProjectVersion.txt';p.parent.mkdir();p.write_text('Unity')
        (self.root/'ARCHITECTURE.md').write_text('project owned')
        self.assertNotIn('STANDARD_SUGGESTED', [w['code'] for w in inspect(self.root)['warnings']])
    def test_skynet_not_detected_by_generic_dirs(self):
        (self.root/'service').mkdir();(self.root/'lualib').mkdir()
        self.assertEqual(inspect(self.root)['suggested_plugins'],[])
    def test_skynet_detected_from_pinned_runtime_dockerfile(self):
        (self.root/'Dockerfile').write_text('RUN git clone https://github.com/cloudwu/skynet.git /opt/skynet')
        result=inspect(self.root)
        self.assertEqual(result['suggested_plugins'][0]['plugin_id'], 'skynet')
        self.assertIn('STANDARD_SUGGESTED', [w['code'] for w in result['warnings']])
    def test_mixed_stack(self):
        (self.root/'CMakeLists.txt').write_text('project(x)');p=self.root/'skynet-src/skynet.h';p.parent.mkdir();p.write_text('')
        self.profile([{'id':'skynet','version':'1.0.0'}]);r=inspect(self.root)
        self.assertEqual({x['plugin_id'] for x in r['suggested_plugins']},{'cpp','skynet'})
        self.assertEqual([x['code'] for x in r['warnings']],['STANDARD_MISSING'])
    def test_existing_standard_without_profile(self):
        (self.root/'ARCHITECTURE.md').write_text('owned')
        r=inspect(self.root);self.assertEqual(r['discovered_standards']['architecture'],'ARCHITECTURE.md')
    def test_existing_standard_satisfies_selected_plugin(self):
        (self.root/'ARCHITECTURE.md').write_text('owned');self.profile([{'id':'cpp','version':'1.0.0'}]);self.assertEqual(inspect(self.root)['warnings'],[])
    def test_version_warning(self):
        self.profile([{'id':'cpp','version':'0.8'}]);self.assertIn('PLUGIN_VERSION_MISMATCH',[x['code'] for x in inspect(self.root)['warnings']])
    def test_path_escape_warning(self):
        self.profile([{'id':'cpp','version':'1.0.0'}],{'architecture':'../outside.md'})
        self.assertEqual(inspect(self.root)['warnings'][0]['code'],'STANDARD_UNAVAILABLE')
    def test_profile_rejects_windows_backslash_path(self):
        self.profile([{'id':'cpp','version':'1.0.0'}], {'architecture': r'..\outside.md'})
        (self.root / r'..\outside.md').write_text('must not be bound')
        self.assertIn('STANDARD_UNAVAILABLE', [w['code'] for w in inspect(self.root)['warnings']])

    def test_profile_rejects_windows_drive_path(self):
        self.profile([{'id':'cpp','version':'1.0.0'}], {'architecture': 'C:/outside.md'})
        drive = self.root / 'C:'
        drive.mkdir()
        (drive / 'outside.md').write_text('must not be bound')
        self.assertIn('STANDARD_UNAVAILABLE', [w['code'] for w in inspect(self.root)['warnings']])

    def test_profile_nul_path_is_reported_as_unavailable(self):
        self.profile([{'id':'cpp','version':'1.0.0'}], {'architecture': 'docs/arch\x00itecture.md'})
        result = inspect(self.root)
        self.assertIn('STANDARD_UNAVAILABLE', [w['code'] for w in result['warnings']])
        self.assertFalse(result['blocking'])

    def test_profile_duplicate_plugin_ids_are_invalid_nonblocking(self):
        self.profile([
            {'id':'cpp','version':'1.0.0'},
            {'id':'cpp','version':'1.0.0'},
        ])
        result = inspect(self.root)
        self.assertIn('PROFILE_INVALID', [w['code'] for w in result['warnings']])
        self.assertFalse(result['blocking'])
        self.assertEqual(result['selected_plugins'], [])

    def write_semantic_profile(self, selected, rules):
        profile = self.root/'.frameforge/profile.json'
        profile.parent.mkdir(exist_ok=True)
        profile.write_text(json.dumps({
            'schema_version': 1,
            'selected_plugins': selected,
            'standards': {},
            'semantic_rules': rules,
        }))

    def semantic_rule(self, plugin_id='unity', rule_id='rule-1', paths=None):
        return {
            'id': rule_id, 'plugin_id': plugin_id, 'topic': 'architecture',
            'recommendation': 'review evidence', 'language': 'csharp',
            'paths': paths or ['Assets/Root.cs'], 'tokens': ['Root.Update()'],
        }

    def test_semantic_rule_unknown_plugin_is_reported_nonblocking(self):
        self.write_semantic_profile([], [self.semantic_rule(plugin_id='missing-engine')])
        result = inspect(self.root)
        self.assertIn('SEMANTIC_RULE_PLUGIN_UNKNOWN', [w['code'] for w in result['warnings']])
        self.assertEqual(result['semantic_checks'], [])
        self.assertFalse(result['blocking'])

    def test_semantic_rule_requires_explicit_plugin_selection(self):
        self.write_semantic_profile([], [self.semantic_rule()])
        result = inspect(self.root)
        self.assertIn('SEMANTIC_RULE_PLUGIN_NOT_SELECTED', [w['code'] for w in result['warnings']])
        self.assertEqual(result['semantic_checks'], [])
        self.assertFalse(result['blocking'])

    def test_selected_semantic_rule_is_not_silently_dropped_when_plugin_not_discovered(self):
        self.write_semantic_profile(
            [{'id': 'unity', 'version': '1.0.0'}],
            [self.semantic_rule(paths=['Assets/NotPresent.cs'])],
        )
        result = inspect(self.root)
        self.assertEqual(len(result['semantic_checks']), 1)
        self.assertEqual(result['semantic_checks'][0]['status'], 'not_evaluated')
        self.assertNotIn('SEMANTIC_RULE_PLUGIN_NOT_SELECTED', [w['code'] for w in result['warnings']])
        self.assertFalse(result['blocking'])

    def test_semantic_rule_selected_plugin_version_mismatch_is_reported(self):
        self.write_semantic_profile(
            [{'id': 'unity', 'version': '0.0.0'}],
            [self.semantic_rule()],
        )
        result = inspect(self.root)
        self.assertIn('SEMANTIC_RULE_PLUGIN_VERSION_MISMATCH', [w['code'] for w in result['warnings']])
        self.assertEqual(result['semantic_checks'], [])
        self.assertFalse(result['blocking'])

    def test_check_clause_rejects_blank_or_padded_ids_nonblocking(self):
        cases = [
            ('', {'id': 'ARCH-1', 'text': 'Must unsubscribe', 'reference': 'docs/architecture.md'}),
            ('   ', {'id': 'ARCH-1', 'text': 'Must unsubscribe', 'reference': 'docs/architecture.md'}),
            (' lifecycle ', {'id': 'ARCH-1', 'text': 'Must unsubscribe', 'reference': 'docs/architecture.md'}),
            ('lifecycle', {'id': ' ARCH-1 ', 'text': 'Must unsubscribe', 'reference': 'docs/architecture.md'}),
        ]
        for check_id, clause in cases:
            with self.subTest(check_id=check_id, clause_id=clause['id']):
                profile = self.root/'.frameforge/profile.json'
                profile.parent.mkdir(exist_ok=True)
                profile.write_text(json.dumps({
                    'schema_version': 1,
                    'selected_plugins': [],
                    'standards': {},
                    'check_clauses': {check_id: clause},
                }))
                result = inspect(self.root)
                self.assertIn('PROFILE_INVALID', [w['code'] for w in result['warnings']])
                self.assertEqual(result['clause_coverage'], [])
                self.assertFalse(result['blocking'])

    def test_profile_invalid_nonblocking(self):
        p=self.root/'.frameforge/profile.json';p.parent.mkdir();p.write_text('{bad')
        r=inspect(self.root);self.assertFalse(r['blocking']);self.assertEqual(r['warnings'][0]['code'],'PROFILE_INVALID')
    def test_unknown_plugin_warning(self):
        self.profile([{'id':'future','version':'1.0'}]);self.assertEqual(inspect(self.root)['warnings'][0]['code'],'PLUGIN_UNKNOWN')
    def test_catalog_manifest(self): self.assertIn('unity',manifests())

if __name__=='__main__':unittest.main()

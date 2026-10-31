import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from frameforge.plugin_checks import run, validate_profile_checks


class DispatchTests(unittest.TestCase):
    def invoke(self, chosen=(), found=(), binding=None):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            return run(root, chosen, [{'plugin_id': p} for p in found], {},
                       [], [], binding, {}, lambda *_: None)

    @patch('frameforge.plugin_checks.unity_assemblies', side_effect=AssertionError('unity ran'))
    @patch('frameforge.plugin_checks.skynet_transaction', side_effect=AssertionError('skynet ran'))
    @patch('frameforge.plugin_checks.art_ui_standard_gaps', side_effect=AssertionError('art ran'))
    @patch('frameforge.plugin_checks.review_art_ui_unity_binding', side_effect=AssertionError('binding ran'))
    def test_discovered_only_never_executes(self, *_):
        self.assertEqual(self.invoke((), ('unity', 'skynet', 'art-ui'), {'common': {}, 'main': {}}),
                         ([], [], [], []))

    @patch('frameforge.plugin_checks.unity_assemblies', side_effect=AssertionError('unity ran'))
    @patch('frameforge.plugin_checks.skynet_transaction', side_effect=AssertionError('skynet ran'))
    @patch('frameforge.plugin_checks.art_ui_standard_gaps', side_effect=AssertionError('art ran'))
    def test_selected_but_not_detected_never_executes(self, *_):
        self.assertEqual(self.invoke(('unity', 'skynet', 'art-ui'), ()), ([], [], [], []))

    @patch('frameforge.plugin_checks.review_art_ui_unity_binding', side_effect=AssertionError('binding ran'))
    def test_binding_requires_both_active_plugins(self, _):
        cfg = {'common': {}, 'main': {}}
        self.assertEqual(self.invoke(('unity', 'art-ui'), ('art-ui',), cfg)[2], [])
        self.assertEqual(self.invoke(('unity', 'art-ui'), ('unity',), cfg)[2], [])

    @patch('frameforge.plugin_checks.unity_assemblies', return_value={'check_id': 'unity'})
    @patch('frameforge.plugin_checks.skynet_transaction', return_value={'check_id': 'skynet'})
    def test_combination_dispatch_only_active(self, skynet, unity):
        result = self.invoke(('unity', 'skynet'), ('unity', 'skynet'))
        self.assertEqual(result[3], [{'check_id': 'unity'}, {'check_id': 'skynet-transaction-branches',
                           'status': 'not_evaluated', 'evidence': [], 'blocking': False}])
        unity.assert_called_once()
        skynet.assert_not_called()

    def test_profile_check_validation_is_exposed_by_dispatch_boundary(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            profile = {
                'art_ui_checks': [{'id': 'ui-safe-area', 'clause': 'safe area',
                                   'evidence_paths': ['Assets/UI']}],
                'art_ui_implementation_checks': [{'check_id': 'ui-safe-area',
                                                  'path': 'Assets/UI/screen.cs',
                                                  'contains': 'SafeArea'}],
                'art_ui_unity_binding': {'common': {'asset': 'Assets/Common.asset',
                                                    'group': 'Assets/Common.asset',
                                                    'address': 'common'},
                                         'main': {'asset': 'Assets/Main.asset',
                                                  'group': 'Assets/Main.asset',
                                                  'address': 'main'}}
            }
            checks, implementation, binding, warnings = validate_profile_checks(
                profile, root, {}, lambda _root, rel: root / rel)
            self.assertEqual([item['id'] for item in checks], ['ui-safe-area'])
            self.assertEqual([item['check_id'] for item in implementation], ['ui-safe-area'])
            self.assertEqual(binding, profile['art_ui_unity_binding'])
            self.assertEqual(warnings, [])

    def test_invalid_optional_profile_check_keeps_warning_and_does_not_raise(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            profile = {'art_ui_checks': 'invalid',
                       'art_ui_implementation_checks': [],
                       'art_ui_unity_binding': {'common': {}, 'main': {}}}
            checks, implementation, binding, warnings = validate_profile_checks(
                profile, root, {}, lambda _root, rel: root / rel)
            self.assertEqual(checks, [])
            self.assertEqual(implementation, [])
            self.assertIsNone(binding)
            self.assertEqual([item['code'] for item in warnings], [
                'ART_UI_CHECKS_INVALID', 'ART_UI_UNITY_BINDING_INVALID'])

    def test_core_does_not_import_domain_specific_validator_modules(self):
        source = (Path(__file__).parents[1] / 'src/frameforge/core.py').read_text()
        self.assertNotIn('from .art_ui_', source)
        self.assertIn('validate_profile_checks', source)

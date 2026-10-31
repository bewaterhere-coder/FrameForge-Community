import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from frameforge.plugin_checks import run


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

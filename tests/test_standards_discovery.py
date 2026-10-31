import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect


class StandardsDiscoveryTests(unittest.TestCase):
    def test_unbound_candidates_are_not_approved_or_activated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'docs').mkdir()
            (root/'docs/MY-ARCHITECTURE.md').write_text('# Custom MVVM')
            (root/'docs/UI规范.md').write_text('# Custom UI')
            (root/'docs/notes.md').write_text('Not standard')
            (root/'docs/NETWORK-TEST.md').write_text('Test report, not a standard')
            (root/'docs/STARTUP.md').write_text('Not an art rule')
            (root/'docs/BUILD.md').write_text('Not a UI rule')
            result=inspect(root)
            names=[c['reference'] for c in result['standard_candidates']['candidates']]
            self.assertEqual(names,['docs/MY-ARCHITECTURE.md','docs/UI规范.md'])
            self.assertEqual(result['selected_plugins'],[])
            self.assertTrue(all(c['owner_approved']=='unverified' for c in result['standard_candidates']['candidates']))
            self.assertFalse(result['blocking'])

    def test_symlink_escape_and_large_file_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'project';root.mkdir()
            outside=Path(d)/'architecture.md';outside.write_text('Outside')
            (root/'architecture.md').symlink_to(outside)
            (root/'test-standards.md').write_bytes(b'x'*500001)
            self.assertEqual(inspect(root)['standard_candidates']['candidates'],[])

    def test_candidate_does_not_override_explicit_binding(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'docs').mkdir();(root/'.frameforge').mkdir()
            (root/'docs/architecture-one.md').write_text('MVP')
            (root/'docs/architecture-two.md').write_text('ECS')
            (root/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[],
                'standards':{'architecture':'docs/architecture-two.md'}}))
            result=inspect(root)
            self.assertEqual(result['standard_sources'][0]['reference'],'docs/architecture-two.md')
            self.assertEqual(len(result['standard_candidates']['candidates']),2)
            self.assertFalse(result['blocking'])

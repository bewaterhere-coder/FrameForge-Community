import tempfile
import json
import unittest
from pathlib import Path
from frameforge.core import inspect

class GuidanceTests(unittest.TestCase):
    def test_unity_selection_and_generic_structure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            source=root/'Assets/Engine/Controller.cs'
            source.parent.mkdir(parents=True)
            source.write_text('public class Controller : MonoBehaviour {}')
            self.assertEqual(inspect(root)['professional_guidance'], [])
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            result=inspect(root)['professional_guidance']
            self.assertEqual(len(result),2)
            self.assertEqual(result[0]['evidence'][0]['path'],'Assets/Engine/Controller.cs')
            self.assertEqual(result[0]['status'],'review_recommended')
            self.assertEqual(result[1]['status'],'not_evaluated')

    def test_skynet_no_project_specific_path(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'Dockerfile').write_text('FROM cloudwu/skynet')
            f=root/'backend/custom_actor.lua'
            f.parent.mkdir()
            f.write_text('skynet.start(function() end)')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'skynet','version':'1.0.0'}]}))
            result=inspect(root)['professional_guidance']
            self.assertEqual(len(result),2)
            self.assertEqual(result[0]['evidence'][0]['path'],'backend/custom_actor.lua')

    def test_unmatched_signal_is_not_a_gap(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            r=inspect(root)['professional_guidance']
            self.assertTrue(all(item['status']=='not_evaluated' for item in r))

    def test_comments_not_treated_as_signals(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            source=root/'Assets/Comment.cs'
            source.parent.mkdir()
            source.write_text('// MonoBehaviour placeholder')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            r=inspect(root)['professional_guidance']
            self.assertEqual(r[0]['status'],'not_evaluated')

    def test_test_sources_do_not_generate_production_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'Dockerfile').write_text('FROM cloudwu/skynet')
            test=root/'tests/txn.lua'
            test.parent.mkdir()
            test.write_text("query(db,'START TRANSACTION')")
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'skynet','version':'1.0.0'}]}))
            result=inspect(root)['professional_guidance']
            self.assertEqual(result[1]['status'],'not_evaluated')

    def test_asmdef_guidance_reads_actual_asmdef_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            (root/'Assets').mkdir()
            (root/'Assets/Game.asmdef').write_text(json.dumps({'name':'Game','references':['Core']}))
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            rule=next(x for x in inspect(root)['professional_guidance'] if x['guidance_id']=='unity-assemblies')
            self.assertEqual(rule['status'],'review_recommended')
            self.assertEqual(rule['evidence'][0]['path'],'Assets/Game.asmdef')

    def test_guidance_source_types_do_not_cross_match(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            (root/'Assets').mkdir()
            (root/'Assets/Notes.cs').write_text('class Example { string x = "references"; }')
            (root/'Assets/Empty.asmdef').write_text(json.dumps({'name':'Empty'}))
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            rule=next(x for x in inspect(root)['professional_guidance'] if x['guidance_id']=='unity-assemblies')
            self.assertEqual(rule['status'],'not_evaluated')
            self.assertEqual(rule['evidence'],[])

    def test_guidance_truncation_is_not_missing_standard(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            assets=root/'Assets'
            assets.mkdir()
            for i in range(155):
                (assets/f'Unit{i:03d}.cs').write_text('class C {}')
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps(
                {'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            result=inspect(root)
            self.assertTrue(result['professional_guidance'][0]['scan']['truncated'])
            self.assertEqual(result['professional_guidance'][1]['status'],'not_evaluated')
            self.assertFalse(result['blocking'])

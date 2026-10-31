import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect, manifests

class AdvisoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_unity_preview_is_not_activation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'ProjectSettings').mkdir()
            (p/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000')
            result=inspect(p)
            self.assertEqual(result['selected_plugins'], [])
            rules=[r for r in result['advisories'] if r['plugin_id']=='unity']
            self.assertGreater(len(rules),2)
            self.assertTrue(all(r['activation']=='preview_only' for r in rules))
            self.assertTrue(all(r['status']=='review_recommended' for r in rules))
            self.assertFalse(result['blocking'])

    def test_sky_net_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'service').mkdir(parents=True)
            (p/'service/main.lua').write_text('require "skynet"')
            (p/'service/actor.lua').write_text('test')
            results=inspect(p)['advisories']
            worker=next(x for x in results if x['rule_id']=='skynet-worker')
            self.assertEqual(worker['status'],'evidence_found')
            self.assertEqual(worker['evidence'],['service/actor.lua'])

    def test_bad_advisory_path(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            m={'id':'x','version':'1','domain':'code','standards':[],'detection':[],
               'advisories':[{'id':'x','topic':'x','recommendation':'x','any_paths':['../secret']}]}
            (p/'x.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'Invalid plugin manifest'):
                manifests(p)

    def test_no_implicit_semantic_activation(self):
        (self.root/'ProjectSettings').mkdir()
        (self.root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
        self.assertEqual(inspect(self.root)['semantic_checks'], [])

    def test_selected_project_rule(self):
        (self.root/'ProjectSettings').mkdir()
        (self.root/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
        source=self.root/'Assets/Scripts/Root.cs'
        source.parent.mkdir(parents=True)
        source.write_text('Event += OnEvent;')
        (self.root/'.frameforge').mkdir()
        rule={'id':'root-events','plugin_id':'unity','topic':'lifecycle','language':'csharp',
              'paths':['Assets/Scripts/Root.cs'],'tokens':['Event += OnEvent;','Event -= OnEvent;'],
              'recommendation':'Unsubscribe before destruction'}
        profile={'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}],
                 'semantic_rules':[rule]}
        (self.root/'.frameforge/profile.json').write_text(json.dumps(profile))
        r=inspect(self.root)
        self.assertEqual(r['semantic_checks'][0]['status'],'review_needed')
        profile['selected_plugins'][0]['version']='old'
        (self.root/'.frameforge/profile.json').write_text(json.dumps(profile))
        self.assertEqual(inspect(self.root)['semantic_checks'],[])

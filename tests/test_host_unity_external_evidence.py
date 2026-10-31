import json
import tempfile
import unittest
from pathlib import Path
from frameforge.host_adapter import inspect_project

class HostUnityEvidenceTests(unittest.TestCase):
    def test_host_explicit_evidence_and_default(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'ProjectSettings').mkdir()
            (root/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
            (root/'Assets').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['GUID:'+'f'*32]}))
            (root/'.frameforge').mkdir()
            (root/'.frameforge/profile.json').write_text(json.dumps({'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            baseline=inspect_project(root)
            evidence={'GUID:'+'f'*32:{'status':'not_observed_in_package_cache','package':'com.unity.timeline'}}
            changed=inspect_project(root,unity_external_evidence=evidence)
            a=baseline['structural_observations'][0]
            b=changed['structural_observations'][0]
            self.assertIsNone(a['unresolved_reference_context'][0]['external_evidence'])
            self.assertEqual(b['unresolved_reference_context'][0]['external_evidence'], evidence['GUID:'+'f'*32])
            self.assertEqual(b['unresolved_reference_context'][0]['resolution'], 'unverified')
            self.assertEqual(b['unresolved_reference_context'][0]['external_dependency_state'], 'external_package_not_observed')
            self.assertEqual(a['unresolved_reference_context'][0]['external_dependency_state'], 'external_evidence_unverified')
            self.assertEqual(a['unresolved_references'],b['unresolved_references'])
            self.assertEqual(b['status'],a['status'])
            self.assertFalse(changed['blocking'])

    def test_unselected_plugin_does_not_run(self):
        with tempfile.TemporaryDirectory() as d:
            report=inspect_project(d,unity_external_evidence={'Missing': {'status':'observed_in_package_cache','package':'fake'}})
            self.assertEqual(report['structural_observations'],[])

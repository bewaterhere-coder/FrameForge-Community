import json
import tempfile
import unittest
from pathlib import Path
from frameforge.core import inspect

class ClauseEvidenceTests(unittest.TestCase):
    def run_case(self, clause_text, code_text, selected=True):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.frameforge').mkdir();(p/'docs').mkdir();(p/'Assets').mkdir()
            (p/'ProjectSettings').mkdir();(p/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000')
            (p/'docs/architecture.md').write_text(clause_text)
            (p/'Assets/Root.cs').write_text(code_text)
            profile={'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}] if selected else [],
                'standards':{'architecture':'docs/architecture.md'},
                'semantic_rules':[{'id':'lifecycle','plugin_id':'unity','topic':'unsubscribe',
                'language':'csharp','paths':['Assets/Root.cs'],'tokens':['-='],'recommendation':'Review teardown'}],
                'check_clauses':{'lifecycle':{'id':'ARCH-1','text':'Must unsubscribe','reference':'docs/architecture.md'}}}
            (p/'.frameforge/profile.json').write_text(json.dumps(profile))
            return inspect(p)

    def test_located_clause_and_code_hint_still_unverified(self):
        x=self.run_case('Must unsubscribe\n','void Dispose(){ Event -= Handler; }')
        c=x['clause_coverage'][0]
        self.assertEqual(c['status'],'evidence_observed')
        self.assertEqual(c['clause_evidence'],{'status':'located','line':1})
        self.assertEqual(c['code_evidence']['locations'][0]['line'],1)
        self.assertIsNone(c['not_evaluated_reason'])
        self.assertEqual(c['compliance'],'unverified')
        self.assertFalse(x['blocking'])

    def test_missing_clause_is_not_compliance_failure(self):
        c=self.run_case('Something else','void Dispose(){ Event -= Handler; }')['clause_coverage'][0]
        self.assertEqual(c['status'],'not_evaluated')
        self.assertEqual(c['clause_evidence']['status'],'not_found')
        self.assertEqual(c['not_evaluated_reason'],'clause_not_uniquely_located')
        self.assertEqual(c['compliance'],'unverified')

    def test_unselected_rule_not_executed(self):
        c=self.run_case('Must unsubscribe','Event -= Handler;',False)['clause_coverage'][0]
        self.assertEqual(c['not_evaluated_reason'],'rule_not_executed')
        self.assertEqual(c['code_evidence']['locations'],[])

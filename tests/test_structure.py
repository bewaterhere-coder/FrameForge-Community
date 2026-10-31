import json
import tempfile
import unittest
from pathlib import Path
from frameforge.structure import unity_assemblies, skynet_transaction

class StructureTests(unittest.TestCase):
    def test_cycle_and_noncycle(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'Assets'
            p.mkdir()
            for name, refs in [('A',['B']),('B',['A'])]:
                (p/(name+'.asmdef')).write_text(json.dumps({'name':name,'references':refs}))
            self.assertEqual(unity_assemblies(d)['status'],'review_needed')
            (p/'B.asmdef').write_text(json.dumps({'name':'B','references':[]}))
            self.assertEqual(unity_assemblies(d)['status'],'no_cycle_in_resolved_names')
    def test_transaction_not_certified(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'service/txn.lua';p.parent.mkdir()
            p.write_text("query(db,'START TRANSACTION')\nif false then query(db,'ROLLBACK') end\nquery(db,'COMMIT')")
            self.assertEqual(skynet_transaction(d,'service/txn.lua')['status'],'branch_review_recommended')
    def test_outside(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(skynet_transaction(d,'../outside')['status'],'not_evaluated')

    def test_no_automatic_structural_scan(self):
        from frameforge.core import inspect
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'ProjectSettings').mkdir()
            (p/'ProjectSettings/ProjectVersion.txt').write_text('Unity')
            self.assertEqual(inspect(p)['structural_observations'], [])
            (p/'.frameforge').mkdir()
            (p/'.frameforge/profile.json').write_text(json.dumps({
                'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
            self.assertEqual(inspect(p)['structural_observations'][0]['check_id'],'unity-asmdef-cycle')

    def test_guid_cycle_and_unresolved(self):
        with tempfile.TemporaryDirectory() as d:
            assets=Path(d)/'Assets';assets.mkdir()
            ids={'A':'a'*32,'B':'b'*32}
            for name,target in [('A','B'),('B','A')]:
                f=assets/(name+'.asmdef')
                f.write_text(json.dumps({'name':name,'references':['GUID:'+ids[target]]}))
                (assets/(name+'.asmdef.meta')).write_text('guid: '+ids[name]+'\n')
            self.assertEqual(unity_assemblies(d)['status'],'review_needed')
            (assets/'B.asmdef.meta').unlink()
            result=unity_assemblies(d)
            self.assertEqual(result['status'],'no_cycle_in_resolved_names')
            self.assertIn('GUID:'+ids['B'],result['unresolved_references'])
            self.assertEqual(result['resolution_status'],'review_recommended')
            self.assertIn('ASMDEF_REFERENCE_UNRESOLVED',[x['code'] for x in result['diagnostics']])
            self.assertFalse(result['blocking'])

    def test_transaction_failure_markers_are_evidence_only(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'txn.lua'
            f.write_text("query(db,'START TRANSACTION')\nlocal rolled_back=query(db,'ROLLBACK')\nif not rolled_back then return nil end\n-- COMMIT outcome unknown\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'txn.lua')
            self.assertEqual(result['status'],'branch_review_recommended')
            self.assertEqual(result['evidence'][0]['rollback_failure_check_lines'],[3])
            self.assertEqual(result['evidence'][0]['unknown_commit_comment_lines'],[4])

    def test_skynet_requires_explicit_transaction_path(self):
        from frameforge.core import inspect
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'Dockerfile').write_text('FROM cloudwu/skynet')
            f=root/'backend/transaction.lua';f.parent.mkdir()
            f.write_text("query(db,'START TRANSACTION')")
            (root/'.frameforge').mkdir()
            profile={'schema_version':1,'selected_plugins':[{'id':'skynet','version':'1.0.0'}]}
            pp=root/'.frameforge/profile.json';pp.write_text(json.dumps(profile))
            self.assertEqual(inspect(root)['structural_observations'][0]['status'],'not_evaluated')
            profile['structural_paths']={'skynet_transaction':'backend/transaction.lua'}
            pp.write_text(json.dumps(profile))
            self.assertEqual(inspect(root)['structural_observations'][0]['status'],'branch_review_recommended')
            profile['structural_paths']={'skynet_transaction':'../other'}
            pp.write_text(json.dumps(profile))
            self.assertIn('PROFILE_INVALID',[w['code'] for w in inspect(root)['warnings']])

    def test_linear_early_exit_without_rollback_is_review_needed(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'START TRANSACTION')\nreturn nil, 'ERROR'\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['status'],'review_needed')
            self.assertEqual(result['evidence'][0]['potential_early_exit'][0]['line'],2)

    def test_rollback_or_branch_does_not_falsely_certify(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'START TRANSACTION')\nif false then return nil end\nquery(db,'ROLLBACK')\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['status'],'branch_review_recommended')
            self.assertEqual(result['evidence'][0]['potential_early_exit'],[])

    def test_begin_failure_guard_does_not_create_defect_warning(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("local started=query(db,'START TRANSACTION')\nif not started then\n return nil,'DB_ERROR'\nend\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['status'],'branch_review_recommended')
            self.assertEqual(result['evidence'][0]['potential_early_exit'],[])

    def test_delegated_rollback_does_not_create_defect_warning(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'START TRANSACTION')\nabort_transaction(db)\nreturn nil,'ERROR'\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['status'],'branch_review_recommended')
            self.assertEqual(result['evidence'][0]['potential_early_exit'],[])

    def test_duplicate_guid_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'Assets';root.mkdir()
            for name in ('A','B'):
                (root/(name+'.asmdef')).write_text(json.dumps({'name':name,'references':[]}))
                (root/(name+'.asmdef.meta')).write_text('guid: '+('a'*32)+'\n')
            r=unity_assemblies(d)
            self.assertEqual(r['resolution_status'],'review_recommended')
            self.assertIn('ASMDEF_GUID_CONFLICT',[x['code'] for x in r['diagnostics']])

    def test_no_asmdef_is_not_success_proof(self):
        with tempfile.TemporaryDirectory() as d:
            r=unity_assemblies(d)
            self.assertIn('ASMDEF_NOT_FOUND_IN_PROJECT',[x['code'] for x in r['diagnostics']])
            self.assertFalse(r['blocking'])


    def test_checked_in_package_reference_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            assets=root/'Assets'; assets.mkdir()
            package=root/'Packages/com.sample/Runtime'; package.mkdir(parents=True)
            (assets/'A.asmdef').write_text(json.dumps({'name':'A','references':['Package.A']}))
            (package/'Package.asmdef').write_text(json.dumps({'name':'Package.A','references':[]}))
            result=unity_assemblies(root)
            self.assertEqual(result['unresolved_references'],[])
            self.assertEqual(result['assemblies_read'],2)
            self.assertEqual(result['resolution_status'],'resolved_within_scanned_project')

    def test_missing_registry_package_remains_uncertain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['Unity.Addressables']}))
            result=unity_assemblies(root)
            self.assertIn('Unity.Addressables',result['unresolved_references'])
            self.assertEqual(result['resolution_status'],'review_recommended')

    def test_manifest_context_is_not_resolution_proof(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir();(root/'Packages').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['Unity.Addressables']}))
            (root/'Packages/manifest.json').write_text(json.dumps({'dependencies':{'com.unity.addressables':'4.1.1'}}))
            result=unity_assemblies(root)
            self.assertIn('Unity.Addressables',result['unresolved_references'])
            self.assertEqual(result['package_context']['status'],'manifest_declared_not_verified')
            self.assertIn('ASMDEF_PACKAGE_CONTEXT_AVAILABLE',[x['code'] for x in result['diagnostics']])
            self.assertFalse(result['blocking'])

    def test_invalid_manifest_is_uncertain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir();(root/'Packages').mkdir()
            (root/'Packages/manifest.json').write_text('{invalid')
            result=unity_assemblies(root)
            self.assertEqual(result['package_context']['status'],'manifest_invalid')
            self.assertFalse(result['blocking'])

    def test_missing_manifest_and_lock_are_not_resolution_proof(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'Assets').mkdir(); (root/'Packages').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['Unity.Addressables']}))
            a=unity_assemblies(root)
            self.assertEqual(a['package_context']['status'],'not_evaluated')
            self.assertIn('Unity.Addressables',a['unresolved_references'])
            manifest=root/'Packages/manifest.json'
            manifest.write_text(json.dumps({'dependencies':{'com.unity.addressables':'4.1.1'}}))
            b=unity_assemblies(root)
            self.assertEqual(b['package_context']['status'],'manifest_declared_not_verified')
            self.assertFalse(b['package_context']['lockfile_present'])
            self.assertIn('Unity.Addressables',b['unresolved_references'])
            self.assertFalse(b['blocking'])

    def test_manifest_no_dependencies_and_symlink_are_uncertain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Packages').mkdir()
            manifest=root/'Packages/manifest.json'
            manifest.write_text('{}')
            self.assertEqual(unity_assemblies(root)['package_context']['status'],'manifest_invalid')
            manifest.unlink()
            outside=root/'external.json';outside.write_text(json.dumps({'dependencies':{'com.unity.addressables':'4.1.1'}}))
            manifest.symlink_to(outside)
            self.assertEqual(unity_assemblies(root)['package_context']['status'],'not_evaluated')

    def test_commit_failure_and_rollback_notes_are_review_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tx.lua'
            p.write_text("query(db,'START TRANSACTION')\n"
                         "local rolled_back=query(db,'ROLLBACK')\n"
                         "if not rolled_back then return nil,'DB_ERROR' end\n"
                         "local committed=query(db,'COMMIT')\n"
                         "if not committed then return nil,'DB_ERROR' end\n")
            r=skynet_transaction(d,'tx.lua')
            codes={v['code'] for v in r['risk_notes']}
            self.assertIn('SKYNET_COMMIT_FAILURE_PATH',codes)
            self.assertIn('SKYNET_ROLLBACK_FAILURE_PATH',codes)
            self.assertFalse(r['blocking'])

    def test_commit_guard_must_match_commit_result_variable(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'START TRANSACTION')\n"
                         "local committed=query(db,'COMMIT')\n"
                         "-- if not committed then return nil end\n"
                         "if not unrelated then return nil end\n")
            r=skynet_transaction(d,'tx.lua')
            self.assertNotIn('SKYNET_COMMIT_FAILURE_PATH',[x['code'] for x in r['risk_notes']])
            f.write_text("query(db,'START TRANSACTION')\n"
                         "local committed=query(db,'COMMIT')\n"
                         "if not committed then return nil end\n")
            self.assertIn('SKYNET_COMMIT_FAILURE_PATH',[x['code'] for x in skynet_transaction(d,'tx.lua')['risk_notes']])

    def test_persistence_signals_are_evidence_only(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'txn.lua'
            f.write_text(
                "query(db,'START TRANSACTION')\n"
                "query(db,'SELECT * FROM player_module_data FOR UPDATE')\n"
                "query(db,'UPDATE player_module_data SET data_version=data_version+1 WHERE id=1 AND data_version=3')\n"
                "query(db,'SELECT result_version FROM player_lineup_requests')\n"
                "query(db,'INSERT INTO player_lineup_requests (id) VALUES (1)')\n"
                "query(db,'COMMIT')\n")
            r=skynet_transaction(d,'txn.lua')
            signals={x['code']:x for x in r['persistence_signals']}
            self.assertEqual(len(signals),4)
            self.assertTrue(all(x['status']=='observed' for x in signals.values()))
            self.assertFalse(r['blocking'])

    def test_persistence_signals_ignore_comment_only_lines(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'txn.lua'
            f.write_text("-- SELECT * FROM tbl FOR UPDATE\n"
                         "-- AND data_version=4\n"
                         "-- INSERT INTO player_lineup_requests\n"
                         "-- SELECT * FROM player_lineup_requests\n")
            signals=skynet_transaction(d,'txn.lua')['persistence_signals']
            self.assertTrue(all(x['status']=='not_observed' for x in signals))

    def test_persistence_signals_ignore_non_sql_logging(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text(
                "print('SELECT * FROM x FOR UPDATE')\n"
                "local message='AND data_version=2'\n"
                "log('INSERT INTO player_lineup_requests')\n"
                "log('FROM player_lineup_requests')\n"
                "query(db,'SELECT 1') -- FOR UPDATE AND data_version=1\n")
            signals=skynet_transaction(d,'tx.lua')['persistence_signals']
            self.assertTrue(all(x['status']=='not_observed' for x in signals))

    def test_generic_receipt_candidate_does_not_depend_on_table_name(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'SELECT * FROM generic_request_receipts')\n"
                         "query(db,'INSERT INTO generic_request_receipts (id) VALUES (1)')\n")
            x={v['code']:v for v in skynet_transaction(d,'tx.lua')['persistence_signals']}
            self.assertEqual(x['DURABLE_RECEIPT_INSERT']['lines'],[2])
            self.assertEqual(x['REPLAY_RECEIPT_READ']['lines'],[1])

    def test_unpaired_insert_does_not_claim_receipt_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'tx.lua'
            f.write_text("query(db,'INSERT INTO unrelated_table (id) VALUES (1)')\n")
            x={v['code']:v for v in skynet_transaction(d,'tx.lua')['persistence_signals']}
            self.assertEqual(x['DURABLE_RECEIPT_INSERT']['status'],'not_observed')
            self.assertEqual(x['REPLAY_RECEIPT_READ']['status'],'not_observed')

    def test_duplicate_asmdef_names_are_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'Assets';(root/'One').mkdir(parents=True);(root/'Two').mkdir()
            for folder in ('One','Two'):
                (root/folder/'Dup.asmdef').write_text(json.dumps({'name':'Same','references':[]}))
            result=unity_assemblies(d)
            self.assertEqual(result['duplicate_assembly_names'],['Same'])
            self.assertEqual(result['resolution_status'],'review_recommended')
            self.assertIn('ASMDEF_DUPLICATE_NAME',[x['code'] for x in result['diagnostics']])
            self.assertFalse(result['blocking'])

    def test_skynet_rollback_comment_is_not_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'tx.lua').write_text("query(db,'START TRANSACTION')\n-- if not rolled_back then return end\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['evidence'][0]['rollback_failure_check_lines'],[])
            self.assertEqual(result['risk_notes'],[])
            self.assertFalse(result['blocking'])

    def test_duplicate_names_preserve_guid_conflict_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'Assets'
            for folder in ('One','Two'):
                sub=root/folder;sub.mkdir(parents=True)
                (sub/'Dup.asmdef').write_text(json.dumps({'name':'Same','references':[]}))
                (sub/'Dup.asmdef.meta').write_text('guid: '+('a'*32)+'\n')
            result=unity_assemblies(d)
            self.assertEqual(result['duplicate_assembly_names'],['Same'])
            self.assertEqual(result['conflicting_guids'],['a'*32])
            self.assertIn('ASMDEF_GUID_CONFLICT',[x['code'] for x in result['diagnostics']])
            self.assertFalse(result['blocking'])

    def test_skynet_inline_comment_excluded_but_real_guard_remains(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'tx.lua').write_text("query(db,'START TRANSACTION')\nlocal x=1 -- if not rolled_back then return end\nif not rolled_back then return nil end\nquery(db,'COMMIT')\n")
            result=skynet_transaction(d,'tx.lua')
            self.assertEqual(result['evidence'][0]['rollback_failure_check_lines'],[3])
            self.assertFalse(result['blocking'])

    def test_unresolved_reference_context_does_not_claim_package_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir();(root/'Packages').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':[
                'Unity.Addressables','GUID:'+'a'*32,'Unknown.External']}))
            (root/'Packages/manifest.json').write_text(json.dumps({'dependencies':{
                'com.unity.addressables':'4.1.1'}}))
            x=unity_assemblies(root)
            context={c['reference']:c for c in x['unresolved_reference_context']}
            self.assertEqual(context['Unity.Addressables']['classification'],'assembly_name_unresolved')
            self.assertEqual(context['Unity.Addressables']['declared_package_hints'], ['com.unity.addressables'])
            self.assertEqual(context['GUID:'+'a'*32]['classification'],'guid_unresolved')
            self.assertEqual(context['Unknown.External']['declared_package_hints'],[])
            self.assertTrue(all(c['resolution']=='unverified' for c in context.values()))
            self.assertIn('Unity.Addressables',x['unresolved_references'])
            self.assertFalse(x['blocking'])

    def test_unrelated_package_same_suffix_not_misattributed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir();(root/'Packages').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':[
                'Unity.Addressables','Vendor.Addressables','GUID:'+'a'*32]}))
            (root/'Packages/manifest.json').write_text(json.dumps({'dependencies':{
                'com.vendor.addressables':'1.0.0','com.unity.addressables':'4.1.1'}}))
            context={v['reference']:v for v in unity_assemblies(root)['unresolved_reference_context']}
            self.assertEqual(context['Unity.Addressables']['declared_package_hints'], ['com.unity.addressables'])
            self.assertEqual(context['Vendor.Addressables']['declared_package_hints'], [])
            self.assertEqual(context['GUID:'+'a'*32]['declared_package_hints'], [])
            self.assertEqual(context['Unity.Addressables']['resolution'],'unverified')

    def test_explicit_external_evidence_is_context_not_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':[
                'GUID:'+'a'*32, 'GUID:'+'b'*32]}))
            observations={
                'GUID:'+'a'*32:{'status':'observed_in_package_cache','package':'com.unity.addressables'},
                'GUID:'+'b'*32:{'status':'not_observed_in_package_cache','package':'com.unity.timeline'}}
            output=unity_assemblies(root,observations)
            refs={c['reference']:c for c in output['unresolved_reference_context']}
            self.assertEqual(refs['GUID:'+'a'*32]['external_evidence'],observations['GUID:'+'a'*32])
            self.assertEqual(refs['GUID:'+'b'*32]['external_evidence'],observations['GUID:'+'b'*32])
            self.assertTrue(all(v['resolution']=='unverified' for v in refs.values()))
            self.assertEqual(refs['GUID:'+'a'*32]['external_dependency_state'], 'external_package_observed')
            self.assertEqual(refs['GUID:'+'b'*32]['external_dependency_state'], 'external_package_not_observed')
            self.assertEqual(len(output['unresolved_references']),2)
            self.assertFalse(output['blocking'])
            baseline = unity_assemblies(root)['unresolved_reference_context'][0]
            self.assertIsNone(baseline['external_evidence'])
            self.assertEqual(baseline['external_dependency_state'], 'external_evidence_unverified')

    def test_malformed_external_evidence_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['Missing']}))
            for external in ({'Missing':{'status':'resolved','package':'fake'}},
                             {'Missing':{'status':'observed_in_package_cache','package':[]}},
                             ['Missing'], None):
                item=unity_assemblies(root,external)['unresolved_reference_context'][0]
                self.assertIsNone(item['external_evidence'])
                self.assertEqual(item['resolution'],'unverified')

    def test_empty_package_evidence_cannot_be_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'Assets').mkdir()
            (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['Missing']}))
            for value in ('', '   '):
                r=unity_assemblies(root, {'Missing':{'status':'observed_in_package_cache','package':value}})
                self.assertIsNone(r['unresolved_reference_context'][0]['external_evidence'])
                self.assertEqual(r['unresolved_reference_context'][0]['resolution'],'unverified')

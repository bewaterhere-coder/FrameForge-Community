import tempfile
import unittest
from pathlib import Path
from frameforge.semantic import evaluate, validate_rules


def rule(paths=None):
    return {"plugin_id":"unity","id":"sample-event","topic":"lifecycle",
            "recommendation":"review cleanup","language":"csharp",
            "paths":paths or ["Assets/Scripts/Root.cs"],
            "tokens":["Event += OnEvent;", "Event -= OnEvent;"]}


class SemanticTests(unittest.TestCase):
    def test_positive_negative_and_comments(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            f=root/"Assets/Scripts/Root.cs"
            f.parent.mkdir(parents=True)
            f.write_text("Event += OnEvent;\n// Event -= OnEvent;\n")
            self.assertEqual(evaluate(root,rule())["status"],"review_needed")
            f.write_text("Event += OnEvent;\nEvent -= OnEvent;")
            self.assertEqual(evaluate(root,rule())["status"],"pattern_observed_control_flow_unverified")

    def test_relocation_and_absence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            r=rule(["Scripts/Other.cs"])
            self.assertEqual(evaluate(root,r)["status"],"not_evaluated")
            f=root/"Scripts/Other.cs"
            f.parent.mkdir(parents=True)
            f.write_text("Event += OnEvent;\nEvent -= OnEvent;")
            self.assertEqual(evaluate(root,r)["evidence"][0]["path"],"Scripts/Other.cs")

    def test_evidence_is_collected_across_all_declared_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first = root/"Assets/Scripts/Root.cs"
            second = root/"Assets/Scripts/Events.cs"
            first.parent.mkdir(parents=True)
            first.write_text("Event += OnEvent;\n")
            second.write_text("Event -= OnEvent;\n")
            result = evaluate(root, rule(["Assets/Scripts/Root.cs", "Assets/Scripts/Events.cs"]))
            self.assertEqual(result["status"], "pattern_observed_control_flow_unverified")
            self.assertEqual({item["path"] for item in result["evidence"]},
                             {"Assets/Scripts/Root.cs", "Assets/Scripts/Events.cs"})
            self.assertEqual(result["missing_tokens"], [])

    def test_later_declared_path_is_not_ignored_after_first_file_exists(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first = root/"Root.cs"
            second = root/"Events.cs"
            first.write_text("unrelated code\n")
            second.write_text("Event += OnEvent;\nEvent -= OnEvent;\n")
            result = evaluate(root, rule(["Root.cs", "Events.cs"]))
            self.assertEqual(result["status"], "pattern_observed_control_flow_unverified")
            self.assertEqual({item["path"] for item in result["evidence"]}, {"Events.cs"})

    def test_invalid_paths_and_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError,"path"):
            validate_rules([rule(["../secret"])])
        with self.assertRaisesRegex(ValueError,"duplicate"):
            validate_rules([rule(),rule()])

    def test_lua_transaction_markers_not_control_flow_proof(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            f=root/"service/transaction.lua"
            f.parent.mkdir(parents=True)
            f.write_text("query(db,'START TRANSACTION')\nif false then query(db,'ROLLBACK') end\nquery(db,'COMMIT')")
            r={"id":"tx","plugin_id":"skynet","topic":"transaction","language":"lua",
               "paths":["service/transaction.lua"],"tokens":["'START TRANSACTION'","'ROLLBACK'","'COMMIT'"],
               "recommendation":"test recovery"}
            self.assertEqual(evaluate(root,r)["status"],"pattern_observed_control_flow_unverified")

    def test_windows_drive_path_rejected_on_posix_hosts(self):
        with self.assertRaisesRegex(ValueError, "path"):
            validate_rules([rule(["C:/outside.cs"])])

    def test_windows_escape_and_rule_limit_rejected(self):
        with self.assertRaisesRegex(ValueError,"path"):
            validate_rules([rule(["..\\secret"])])
        with self.assertRaisesRegex(ValueError,"too many"):
            validate_rules([dict(rule(), id=str(i)) for i in range(101)])

    def test_outside_symlink_not_read(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            root=Path(d)
            f=root/"Assets/Scripts/Root.cs"
            f.parent.mkdir(parents=True)
            outside=Path(other)/"Root.cs"
            outside.write_text("Event += OnEvent;\nEvent -= OnEvent;")
            f.symlink_to(outside)
            self.assertEqual(evaluate(root,rule())["status"],"not_evaluated")

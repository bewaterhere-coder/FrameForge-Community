"""CLI entrypoint contract: JSON output, read-only inspection and errors."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from frameforge.cli import main
from frameforge.core import inspect, manifests


class CliTests(unittest.TestCase):
    def test_plugins_outputs_the_packaged_catalog_as_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--plugins"])

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue()),
                         {"plugins": list(manifests().values())})

    def test_project_inspection_matches_core_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CMakeLists.txt").write_text("project(CliDemo)\n")
            before = sorted(path.relative_to(root).as_posix()
                            for path in root.rglob("*") if path.is_file())
            expected = inspect(root)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main([str(root)])

            after = sorted(path.relative_to(root).as_posix()
                           for path in root.rglob("*") if path.is_file())
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue()), expected)
            self.assertEqual(after, before)

    def test_invalid_plugin_directory_returns_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(["--plugins", "--plugin-dir", str(missing)])

            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Plugin directory missing", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

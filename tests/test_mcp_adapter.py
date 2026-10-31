"""MCP tool parity is verified without importing the optional SDK in CLI tests."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from frameforge.core import manifests
from frameforge.host_adapter import inspect_project, explain_warnings, verify_remediation
from frameforge.mcp_server import create_server


class FakeMCP:
    def __init__(self, name):
        self.name = name
        self.tools = {}

    def tool(self):
        def decorate(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorate


class MCPAdapterTests(unittest.TestCase):
    def setUp(self):
        env_patch = patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': tempfile.gettempdir()})
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def test_sdk_absent_error_and_base_import(self):
        # The module itself must import without installing the optional SDK.
        self.assertTrue(callable(create_server))

    def test_tool_parity_and_readonly(self):
        import sys
        import types
        sdk = types.ModuleType('mcp')
        server_module = types.ModuleType('mcp.server')
        fastmcp_module = types.ModuleType('mcp.server.mcpserver')
        fastmcp_module.MCPServer = FakeMCP
        with patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': tempfile.gettempdir()}), patch.dict(sys.modules, {'mcp': sdk, 'mcp.server': server_module,
                                      'mcp.server.mcpserver': fastmcp_module}):
            server = create_server()
        self.assertEqual(set(server.tools), {
            'list_plugins', 'inspect_project', 'explain_warnings',
            'verify_remediation', 'inspect_for_acceptance'})
        self.assertEqual(server.tools['list_plugins'](),
                         {'plugins': list(manifests().values())})
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'CMakeLists.txt').write_text('project(Demo)')
            before = server.tools['inspect_project'](d)
            self.assertEqual(before, inspect_project(d))
            self.assertEqual(server.tools['explain_warnings'](d),
                             explain_warnings(d))
            self.assertEqual(server.tools['verify_remediation'](
                d, before['warnings']), verify_remediation(d, before['warnings']))
            self.assertFalse((root / '.frameforge').exists())

    def test_bad_previous_warnings_propagate(self):
        import sys
        import types
        sdk = types.ModuleType('mcp')
        sm = types.ModuleType('mcp.server')
        fm = types.ModuleType('mcp.server.mcpserver')
        fm.MCPServer = FakeMCP
        with patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': tempfile.gettempdir()}), patch.dict(sys.modules, {'mcp': sdk, 'mcp.server': sm,
                                      'mcp.server.mcpserver': fm}):
            server = create_server()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                server.tools['verify_remediation'](d, [{'code': 'X'}])


    def test_mcp_2_sdk_registers_and_calls_tools(self):
        import asyncio
        try:
            from mcp.server.mcpserver import MCPServer
        except ImportError:
            self.skipTest('MCP 2.x optional extra is not installed in this test environment')

        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            (Path(root) / 'CMakeLists.txt').write_text('project(McpDemo)')
            with patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': root}):
                server = create_server()
                self.assertIsInstance(server, MCPServer)

                async def exercise():
                    tools = await server.list_tools()
                    self.assertEqual({tool.name for tool in tools}, {
                        'list_plugins', 'inspect_project', 'explain_warnings',
                        'verify_remediation', 'inspect_for_acceptance'})
                    result = await server.call_tool('inspect_project', {'project': root})
                    self.assertIsNotNone(result)
                    self.assertFalse((Path(root) / '.frameforge').exists())
                    from mcp.server.mcpserver.exceptions import UnexpectedToolError
                    with self.assertRaises(UnexpectedToolError) as raised:
                        await server.call_tool('inspect_project', {'project': outside})
                    self.assertIn('outside approved MCP roots', str(raised.exception.__cause__))

                asyncio.run(exercise())

    def test_path_policy_rejects_outside_and_symlink_escape(self):
        from frameforge.mcp_server import _allowed_path
        with tempfile.TemporaryDirectory() as permitted, tempfile.TemporaryDirectory() as outside:
            with patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': permitted}):
                self.assertEqual(_allowed_path(permitted), str(Path(permitted).resolve()))
                with self.assertRaises(ValueError):
                    _allowed_path(outside)
                with self.assertRaises(ValueError):
                    _allowed_path('')
                (Path(permitted) / 'escape').symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    _allowed_path(str(Path(permitted) / 'escape'))
            with patch.dict(os.environ, {'FRAMEFORGE_MCP_PROJECT_ROOTS': ''}):
                with self.assertRaises(ValueError):
                    _allowed_path(permitted)

"""Optional local stdio MCP adapter. No project writes or new inspection logic."""
from __future__ import annotations

import os
from pathlib import Path

from .core import manifests


def _allowed_path(path: str) -> str:
    """Restrict MCP requests to explicitly opted-in local roots."""
    roots = os.environ.get('FRAMEFORGE_MCP_PROJECT_ROOTS', '')
    allowed = [Path(p).expanduser().resolve() for p in roots.split(os.pathsep) if p.strip()]
    if not allowed:
        raise ValueError('FRAMEFORGE_MCP_PROJECT_ROOTS must list approved local roots')
    if not isinstance(path, str) or not path.strip():
        raise ValueError('nonempty project or plugin directory path required')
    target = Path(path).expanduser().resolve()
    if not any(target.is_relative_to(root) for root in allowed):
        raise ValueError('path is outside approved MCP roots')
    return str(target)


def _plugin_dir(path: str | None) -> str | None:
    return _allowed_path(path) if path is not None else None
from . import host_adapter


def create_server():
    """Create tools lazily so the base CLI needs no MCP dependency."""
    try:
        try:
            # MCP Python SDK 2.x renamed FastMCP to MCPServer.
            from mcp.server.mcpserver import MCPServer
            server_factory = MCPServer
        except ImportError:
            # Keep compatibility with SDK 1.x for existing hosts during migration.
            from mcp.server.fastmcp import FastMCP
            server_factory = FastMCP
    except ImportError as exc:
        raise RuntimeError('MCP extra missing: install frameforge-community[mcp]') from exc

    server = server_factory(name="FrameForge")

    @server.tool()
    def list_plugins(plugin_dir: str | None = None) -> dict:
        """List plugin metadata. Discovery does not activate plugins."""
        return {"plugins": list(manifests(_plugin_dir(plugin_dir)).values())}

    @server.tool()
    def inspect_project(project: str, plugin_dir: str | None = None,
                        unity_external_evidence: dict | None = None) -> dict:
        """Inspect a project read-only; warnings never block development."""
        return host_adapter.inspect_project(_allowed_path(project), _plugin_dir(plugin_dir), unity_external_evidence)

    @server.tool()
    def explain_warnings(project: str, plugin_dir: str | None = None) -> dict:
        """Return current project warnings and advisory status without changes."""
        return host_adapter.explain_warnings(_allowed_path(project), _plugin_dir(plugin_dir))

    @server.tool()
    def verify_remediation(project: str, previous_warnings: list[dict],
                                plugin_dir: str | None = None) -> dict:
        """Fresh read-only comparison; not formal acceptance or a receipt."""
        return host_adapter.verify_remediation(_allowed_path(project), previous_warnings, _plugin_dir(plugin_dir))

    @server.tool()
    def inspect_for_acceptance(project: str, expected_commit: str,
                               plugin_dir: str | None = None,
                               profile_source_commit: str | None = None) -> dict:
        """Commit-bound read-only advisory; it does not perform formal acceptance."""
        return host_adapter.inspect_for_acceptance(
            _allowed_path(project), expected_commit, _plugin_dir(plugin_dir), profile_source_commit)

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()

"""Small in-process read-only interface for authorized AI hosts."""
from __future__ import annotations

from pathlib import Path
from .core import inspect


def inspect_project(project, plugin_dir=None, unity_external_evidence=None):
    """Return the same evidence as the established CLI."""
    return inspect(Path(project), plugin_dir=plugin_dir, unity_external_evidence=unity_external_evidence)


def explain_warnings(project, plugin_dir=None):
    """Return live warnings and remediation context, without applying changes."""
    result = inspect_project(project, plugin_dir)
    return {'project': result['project'], 'warnings': result['warnings'],
            'blocking': result['blocking']}


def verify_remediation(project, previous_warnings, plugin_dir=None):
    """Compare caller-supplied previous warning codes against a fresh inspection.

    This is a comparison, not an approval or a durable receipt. Warning
    identity uses code plus message, so a different issue sharing a code is
    never misreported as the same issue.
    """
    if not isinstance(previous_warnings, list) or not all(
        isinstance(w, dict) and isinstance(w.get('code'), str) and w['code'].strip()
        and isinstance(w.get('message'), str) and w['message'].strip()
        for w in previous_warnings
    ):
        raise ValueError('previous_warnings must be a list of warnings with codes')
    result = inspect_project(project, plugin_dir)
    from collections import Counter
    before = Counter((w['code'], w['message']) for w in previous_warnings)
    after = Counter((w['code'], w['message']) for w in result['warnings'])
    resolved = sorted((before - after).elements())
    newly_found = sorted((after - before).elements())
    return {'project': result['project'], 'resolved_codes': [code for code, _ in resolved],
            'resolved_warnings': [{'code': code, 'message': message} for code, message in resolved],
            'remaining_warnings': result['warnings'],
            'new_codes': [code for code, _ in newly_found],
            'new_warnings': [{'code': code, 'message': message} for code, message in newly_found],
            'blocking': result['blocking'], 'verification': 'fresh_readonly_inspection',
            'formal_acceptance': False}


def inspect_for_acceptance(project, expected_commit, plugin_dir=None, profile_source_commit=None):
    """Read-only, commit-bound advisory snapshot for an external acceptance host.

    Never issues a formal verdict. A dirty checkout or mismatched HEAD is not
    acceptable as source evidence for an exact PR commit.
    """
    import re
    import subprocess
    root = Path(project).resolve()
    if not isinstance(expected_commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", expected_commit):
        raise ValueError("expected_commit must be a full 40-character commit SHA")

    def git(*args):
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True,
            text=True, timeout=15, check=False)
        if result.returncode:
            raise ValueError("cannot verify project Git source")
        return result.stdout.strip()

    if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("project must be the Git repository root")
    actual = git("rev-parse", "HEAD")
    if actual.lower() != expected_commit.lower():
        raise ValueError("checkout HEAD does not match expected_commit")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("checkout is not clean; cannot bind inspection to commit")
    profile_source = {"mode": "pr_checkout", "commit": actual}
    profile_data = None
    if profile_source_commit is not None:
        if not isinstance(profile_source_commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", profile_source_commit):
            raise ValueError("profile_source_commit must be a full commit SHA")
        # Explicitly chosen Git content; never silently inherit latest main.
        profile_data = git("show", profile_source_commit + ":.frameforge/profile.json")
        if not profile_data:
            raise ValueError("profile source is empty")
        profile_source = {"mode": "explicit_git_commit", "commit": profile_source_commit.lower(),
                          "path": ".frameforge/profile.json"}
    result = inspect(root, plugin_dir=plugin_dir, profile_data=profile_data)
    return {
        "schema_version": "frameforge.acceptance_advisory.v1",
        "repository_commit": actual,
        "profile_source": profile_source,
        "inspection_scope": "whole_project_bounded_inspection",
        "inspection": result,
        "status": "warning" if result["warnings"] else "no_warnings_observed",
        "compliance_verified": False,
        "formal_acceptance": False,
        "blocking": False,
    }

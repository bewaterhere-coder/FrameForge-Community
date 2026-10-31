"""Bounded, read-only candidates for project-owned standards; never authority."""
import re
from pathlib import Path

NAMES = ('architecture', 'coding', 'code-style', 'art', 'ui', 'asset',
         'resource', 'test', 'testing', 'standard', 'convention', '规范', '架构', '美术', '资源', '测试')
DIRS = ('.', 'docs', 'docs/architecture', 'docs/standards', 'docs/requirements',
        'Documentation', 'documentation', 'specs')


DOMAINS = {
    'architecture': ('architecture', '架构', 'coding', 'code'),
    'art-ui': ('ui', 'art', '美术', '界面'),
    'asset-pipeline': ('asset', 'resource', '资源'),
    'testing': ('test', 'testing', '测试'),
}


def domain_hints(stem):
    parts = set(re.split(r'[^\w]+|_', stem.lower()))
    hints = [domain for domain, terms in DOMAINS.items()
             if any((term in stem if any(ord(c) > 127 for c in term)
                     else term in parts) for term in terms)]
    return sorted(hints)


def discover(root, project_file):
    candidates = []
    visited = 0
    truncated = False
    for folder in DIRS:
        directory = project_file(root, folder)
        if directory is None or not directory.is_dir() or directory.is_symlink():
            continue
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            continue
        for entry in entries:
            visited += 1
            if visited > 400:
                truncated = True
                break
            if entry.is_symlink() or not entry.is_file() or entry.suffix.lower() not in ('.md', '.rst', '.txt'):
                continue
            stem = entry.stem.lower()
            # A test report is not necessarily a testing standard.
            if stem.endswith(('-test', '-tests', '-test-report', '-test-results')) and not any(
                token in stem for token in ('standard', 'convention', '规范')
            ):
                continue
            # Match filename terms, not incidental substrings (startup != art,
            # build != ui). Keep separators such as '-' and '_' as boundaries.
            parts = set(re.split(r'[^\w]+|_', stem))
            if not any((token in stem if any(ord(c) > 127 for c in token) else token in parts) for token in NAMES):
                continue
            rel = entry.relative_to(root).as_posix()
            safe = project_file(root, rel)
            if safe is None or not safe.is_file() or safe.stat().st_size > 500_000:
                continue
            candidates.append({'reference': rel, 'status': 'candidate_reference',
                               'owner_approved': 'unverified', 'evidence': 'filename_only',
                               'domain_hints': domain_hints(stem),
                               'domain_hint_basis': 'filename_tokens_only'})
            if len(candidates) >= 100:
                truncated = True
                break
        if truncated:
            break
    return {'candidates': sorted(candidates, key=lambda item: item['reference']),
            'scan': {'entries_visited': visited, 'truncated': truncated}}

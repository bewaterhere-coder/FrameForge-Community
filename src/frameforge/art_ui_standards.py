"""Optional Art/UI standard evidence checks; non-blocking."""
from pathlib import Path

def art_ui_safe_reference(root, rel, project_file):
    """Reject symlinked components while keeping references within the project."""
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
        return None
    candidate = root
    for part in Path(rel).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return None
    return project_file(root, rel)


def art_ui_standard_gaps(root, standard_ref, checks, project_file):
    """Check project-declared clause text and evidence references, never visual compliance."""
    output = []
    source = art_ui_safe_reference(root, standard_ref, project_file) if standard_ref else None
    valid_source = source is not None and source.is_file() and not source.is_symlink() and source.stat().st_size <= 500_000
    try:
        lines = source.read_text(encoding='utf-8').splitlines() if valid_source else None
    except (OSError, UnicodeError):
        lines = None
    for item in checks:
        positions = [i for i, line in enumerate(lines, 1) if item['clause'] in line] if lines is not None else []
        evidence = [rel for rel in item['evidence_paths']
                    if (target := art_ui_safe_reference(root, rel, project_file)) is not None and target.exists()]
        status = ('standard_unavailable' if lines is None else 'clause_not_found' if not positions
                  else 'clause_ambiguous' if len(positions) > 1 else
                  'evidence_not_found' if item['evidence_paths'] and not evidence else 'review_required')
        output.append({
            'check_id': item['id'], 'status': status, 'standard': standard_ref,
            'clause': item['clause'], 'clause_lines': positions[:5],
            'evidence': evidence, 'blocking': False, 'confidence': 'reference_and_presence_only',
            'recommendation': 'Review the project-owned Art/UI rule and real visual evidence; this is not a compliance verdict.'
        })
    return output


def validate_art_ui_checks(value, project_file):
    if not isinstance(value, list) or len(value) > 32:
        raise ValueError('art_ui_checks must be a bounded list')
    ids = set()
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'] or len(item['id']) > 80 or item['id'] in ids:
            raise ValueError('invalid art_ui_checks id')
        ids.add(item['id'])
        if not isinstance(item.get('clause'), str) or not item['clause'].strip() or len(item['clause']) > 240:
            raise ValueError('invalid art_ui_checks clause')
        paths = item.get('evidence_paths', [])
        if not isinstance(paths, list) or len(paths) > 16 or any(
                not isinstance(rel, str) or not rel or project_file(Path('/'), rel) is None
                for rel in paths):
            raise ValueError('invalid art_ui_checks evidence_paths')
    return value

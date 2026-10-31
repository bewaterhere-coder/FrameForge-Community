"""Bounded, opt-in source-content checks. Never assert runtime or visual compliance."""
from pathlib import Path

def _safe_file(root, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
        return None
    path = root
    for part in Path(rel).parts:
        path = path / part
        if path.is_symlink():
            return None
    target = path.resolve()
    return target if target.is_relative_to(root.resolve()) and target.is_file() else None

def evaluate(root, checks, clause_results):
    clauses = {x['check_id']: x for x in clause_results}
    output = []
    for check in checks:
        cid = check['check_id']
        bound = clauses.get(cid)
        source = _safe_file(root, check['path'])
        matches = []
        if source is not None:
            try:
                if source.stat().st_size <= 250_000:
                    lines = source.read_text(encoding='utf-8').splitlines()
                    matches = [i for i, line in enumerate(lines, 1) if check['contains'] in line]
                else:
                    source = None
            except (OSError, UnicodeError):
                source = None
        status = ('reference_unverified' if not bound or bound['status'] != 'review_required'
                  else 'source_unavailable' if source is None
                  else 'signal_found' if matches else 'signal_not_found')
        output.append({'check_id':cid,'status':status,'path':check['path'],
                       'line_numbers':matches[:5], 'blocking':False,
                       'confidence':'bounded_literal_text_only',
                       'recommendation':'Inspect the real resource, platform configuration and rendered behavior; literal text is not proof of compliance.'})
    return output

def validate(value, declared):
    if not isinstance(value, list) or len(value)>32:
        raise ValueError('invalid art_ui_implementation_checks')
    ids=set()
    for item in value:
        if not isinstance(item, dict) or set(item)!={'check_id','path','contains'}:
            raise ValueError('invalid art_ui implementation check shape')
        cid=item['check_id']
        if not isinstance(cid,str) or cid not in declared or cid in ids:
            raise ValueError('art_ui implementation check must bind one declared clause')
        ids.add(cid)
        if (not isinstance(item['path'],str) or not item['path'] or len(item['path'])>240
            or Path(item['path']).is_absolute() or '..' in Path(item['path']).parts
            or not isinstance(item['contains'],str) or not item['contains'].strip()
            or len(item['contains'])>240):
            raise ValueError('invalid art_ui implementation path or signal')
    return value

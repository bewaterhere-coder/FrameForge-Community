"""Bounded structural observations; no project-specific standards or gates."""
import json
import re
from pathlib import Path


def unity_assemblies(root, external_evidence=None):
    root = Path(root).resolve()
    nodes = {}
    guid_to_name = {}
    conflicting_guids = set()
    duplicate_names = set()
    for base in (root / 'Assets', root / 'Packages'):
        if not base.is_dir():
            continue
        # Package sources checked into the project are available; registry/cache packages are not.
        for path in base.rglob('*.asmdef'):
            if path.is_symlink() or not path.resolve().is_relative_to(root) or path.stat().st_size > 100000:
                continue
            try:
                obj = json.loads(path.read_text(encoding='utf-8'))
                name, refs = obj['name'], obj.get('references', [])
                if not isinstance(name, str) or not isinstance(refs, list):
                    continue
                if name in nodes:
                    duplicate_names.add(name)
                else:
                    nodes[name] = (path.relative_to(root).as_posix(), [r for r in refs if isinstance(r, str)])
                meta = path.with_name(path.name + '.meta')
                if meta.is_file() and not meta.is_symlink() and meta.stat().st_size < 30000:
                    match = re.search(r'^guid:\s*([0-9a-fA-F]{32})\s*$', meta.read_text(encoding='utf-8'), re.M)
                    if match:
                        guid = match.group(1).lower()
                        if guid in guid_to_name:
                            conflicting_guids.add(guid)
                        guid_to_name[guid] = name
            except (OSError, ValueError, KeyError, UnicodeError):
                continue
    graph = {}
    unresolved = set()
    for name, (_, refs) in nodes.items():
        targets = []
        for ref in refs:
            if ref.startswith('GUID:'):
                guid = ref[5:].lower()
                dest = guid_to_name.get(guid) if guid not in conflicting_guids else None
            else:
                dest = ref if ref in nodes else None
            if dest:
                targets.append(dest)
            else:
                unresolved.add(ref)
        graph[name] = targets
    cycles, seen = set(), set()
    def visit(node, chain):
        if node in chain:
            cycle = chain[chain.index(node):]
            cycles.add(tuple(sorted(cycle)))
            return
        if node in seen:
            return
        for target in graph[node]:
            visit(target, chain + [node])
        seen.add(node)
    for name in graph:
        visit(name, [])
    package_context = {'status': 'not_evaluated', 'declared_packages': [], 'lockfile_present': False}
    manifest = root / 'Packages/manifest.json'
    lockfile = root / 'Packages/packages-lock.json'
    if (manifest.is_file() and not manifest.is_symlink()
            and manifest.stat().st_size <= 100_000):
        try:
            declarations = json.loads(manifest.read_text(encoding='utf-8'))['dependencies']
            if isinstance(declarations, dict) and all(isinstance(k,str) and isinstance(v,str)
                                                       for k,v in declarations.items()):
                package_context = {'status': 'manifest_declared_not_verified',
                                   'declared_packages': sorted(declarations),
                                   'lockfile_present': lockfile.is_file() and not lockfile.is_symlink()}
            else:
                package_context['status'] = 'manifest_invalid'
        except (OSError, ValueError, KeyError, UnicodeError):
            package_context['status'] = 'manifest_invalid'
    # Caller-supplied observation only: never read host cache or trust paths.
    evidence = external_evidence if isinstance(external_evidence, dict) else {}
    reference_context = []
    packages = package_context['declared_packages']
    for ref in sorted(unresolved):
        # An assembly label is not a package ID. Show an explicit, conservative
        # namespace hint, never mark the reference resolved from a manifest.
        package_hints = [pkg for pkg in packages
                         if not ref.startswith('GUID:')
                         and ref.lower().startswith('unity.')
                         and pkg.lower().startswith('com.unity.')
                         and ref.lower().split('.')[-1] == pkg.rsplit('.', 1)[-1].lower()]
        observed = evidence.get(ref)
        if not isinstance(observed, dict) or observed.get('status') not in ('observed_in_package_cache', 'not_observed_in_package_cache') or not isinstance(observed.get('package'), str) or not observed['package'].strip() or len(observed['package']) > 128:
            observed = None
        # Host observations refine the review bucket but never resolve a reference.
        # A cache miss alone does not prove that a package is optional or broken.
        if observed and observed['status'] == 'observed_in_package_cache':
            external_state = 'external_package_observed'
        elif observed and observed['status'] == 'not_observed_in_package_cache':
            external_state = 'external_package_not_observed'
        else:
            external_state = 'external_evidence_unverified'
        reference_context.append({'reference': ref,
                                  'external_dependency_state': external_state,
                                  'classification': 'guid_unresolved' if ref.startswith('GUID:')
                                  else 'assembly_name_unresolved',
                                  'declared_package_hints': package_hints,
                                  'hint_basis': 'unity_namespace_and_name_suffix_only' if package_hints else None,
                                  'external_evidence': {'status': observed['status'], 'package': observed['package']} if observed else None,
                                  'resolution': 'unverified'})
    diagnostics = []
    if unresolved and package_context['status']=='manifest_declared_not_verified':
        diagnostics.append({'code': 'ASMDEF_PACKAGE_CONTEXT_AVAILABLE',
                            'count': len(package_context['declared_packages']),
                            'recommendation': 'Package manifest declarations provide context only; inspect resolved package assemblies and Unity compilation before treating references as missing.'})
    if duplicate_names:
        diagnostics.append({'code': 'ASMDEF_DUPLICATE_NAME', 'count': len(duplicate_names),
                            'recommendation': 'Multiple asmdef files declare the same assembly name; review duplicate paths and Unity compilation.'})
    if conflicting_guids:
        diagnostics.append({'code': 'ASMDEF_GUID_CONFLICT', 'count': len(conflicting_guids),
                            'recommendation': 'Inspect duplicate assembly meta GUIDs before relying on the resolved dependency graph.'})
    if unresolved:
        diagnostics.append({'code': 'ASMDEF_REFERENCE_UNRESOLVED', 'count': len(unresolved),
                            'recommendation': 'Resolve references using Unity package and assembly context; external package targets may be valid.'})
    if not nodes:
        diagnostics.append({'code': 'ASMDEF_NOT_FOUND_IN_PROJECT', 'count': 0,
                            'recommendation': 'No asmdef found under Assets or checked-in Packages; registry/cache packages are not scanned.'})
    return {'check_id': 'unity-asmdef-cycle', 'status': 'review_needed' if cycles else 'no_cycle_in_resolved_names',
            'evidence': [{'assemblies': list(c)} for c in sorted(cycles)],
            'assemblies_read': len(nodes), 'unresolved_references': sorted(unresolved),
            'conflicting_guids': sorted(conflicting_guids),
            'duplicate_assembly_names': sorted(duplicate_names),
            'unresolved_reference_context': reference_context,
            'resolution_status': 'review_recommended' if unresolved or conflicting_guids or duplicate_names else 'resolved_within_scanned_project',
            'diagnostics': diagnostics,
            'package_context': package_context,
            'recommendation': 'Review direct assembly reference cycles; resolve GUID references separately and verify Unity compilation.',
            'blocking': False}


def skynet_transaction(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 200000:
        return {'check_id': 'skynet-transaction-branches', 'status': 'not_evaluated', 'evidence': [], 'blocking': False}
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError):
        return {'check_id': 'skynet-transaction-branches', 'status': 'not_evaluated', 'evidence': [], 'blocking': False}
    def locate(token):
        return [i for i, line in enumerate(lines, 1) if token in line and not line.lstrip().startswith('--')]
    begin, commit, rollback = (locate(x) for x in ("'START TRANSACTION'", "'COMMIT'", "'ROLLBACK'"))
    # These are review signals, not a Lua control-flow parser or transaction proof.
    unknown_commit_markers = [i for i, line in enumerate(lines, 1)
                              if ('COMMIT outcome unknown' in line or 'uncertain COMMIT' in line)
                              and line.lstrip().startswith('--')]
    rollback_fail_markers = [i for i, line in enumerate(lines, 1)
                             if ('if not rolled_back' in line.split('--', 1)[0]
                                 or 'if not rollback' in line.split('--', 1)[0])]
    # Only flag an explicitly observable unprotected early return in a small
    # linear transaction span. Branching, helper calls and loops are uncertain.
    # This is not a Lua control-flow parser.
    findings = []
    if len(begin) == 1 and commit:
        for number in range(begin[0] + 1, min(commit[0], len(lines) + 1)):
            statement = lines[number - 1].strip()
            if not statement or statement.startswith('--'):
                continue
            if re.match(r'^return\b', statement) and not rollback:
                prior = [line.strip() for line in lines[begin[0]:number - 1] if line.strip() and not line.lstrip().startswith('--')]
                # A preceding guard or helper call makes an early return's
                # transaction state uncertain, not a demonstrable defect.
                if any(re.match(r'^(if|elseif|else|for|while|repeat|function|end)\b', item) for item in prior):
                    continue
                if any(re.search(r'\b(?:rollback|abort(?:_transaction)?|cancel_transaction|fail)\s*\(', item, re.I) for item in prior):
                    continue
                findings.append({'line': number, 'reason': 'return_between_begin_commit_without_rollback_marker'})
    commit_error_lines = []
    for number in commit:
        statement = lines[number - 1].strip()
        # Require a direct assignment of the COMMIT query result. Nearby
        # unrelated guards/comments cannot establish this signal.
        match = re.match(r"^local\s+(\w+)(?:\s*,\s*\w+)*\s*=\s*query\s*\([^\n]*['\"]COMMIT['\"]", statement)
        if not match:
            continue
        result_name = match.group(1)
        for line in lines[number:min(number + 4, len(lines))]:
            code = line.split('--', 1)[0].strip()
            if re.match(r'^if\s+not\s+' + re.escape(result_name) + r'\s+then\s+return\b', code):
                commit_error_lines.append(number)
                break
    risk_notes = []
    if commit_error_lines:
        risk_notes.append({'code': 'SKYNET_COMMIT_FAILURE_PATH', 'lines': commit_error_lines,
                           'recommendation': 'Review uncertain COMMIT handling and durable replay readback.'})
    if rollback_fail_markers:
        risk_notes.append({'code': 'SKYNET_ROLLBACK_FAILURE_PATH', 'lines': rollback_fail_markers,
                           'recommendation': 'Review rollback failure handling and connection reuse safety.'})
    # Lightweight, bounded SQL-string evidence only. Markers are not proof
    # that a transaction is atomic, retry-safe or functionally correct.
    # Only match a query call with SQL fragments on the same source line.
    # Documentation strings, logging and inline comments are not SQL evidence.
    sql_code = [(i, code) for i, line in enumerate(lines, 1)
                if (code := line.split('--', 1)[0]).strip()
                and re.search(r'\bquery\s*\(', code)]
    persistence_signals = []
    # A receipt candidate is a table that has both a read and an insert.
    # Do not bake a consuming project's table or version-column name into core.
    inserts, reads = {}, {}
    for number, code in sql_code:
        for table in re.findall(r'\bINSERT\s+INTO\s+([A-Za-z_][A-Za-z_0-9]*)\b', code, re.I):
            inserts.setdefault(table.lower(), []).append(number)
        for table in re.findall(r'\bFROM\s+([A-Za-z_][A-Za-z_0-9]*)\b', code, re.I):
            reads.setdefault(table.lower(), []).append(number)
    candidates = sorted(inserts.keys() & reads.keys())
    rules = (
        ('ROW_LOCK_FOR_UPDATE', r'\bFOR\s+UPDATE\b',
         'Review row lock scope and concurrency.'),
        ('CAS_VERSION_CONDITION', r'\bAND\s+[A-Za-z_][A-Za-z_0-9]*version\s*=',
         'Review version predicate and affected-row checks.'),
    )
    for code, expression, recommendation in rules:
        matches = [number for number, line in sql_code if re.search(expression, line, re.I)]
        persistence_signals.append({'code': code, 'lines': matches,
                                    'status': 'observed' if matches else 'not_observed',
                                    'recommendation': recommendation})
    for code, matches, recommendation in (
        ('DURABLE_RECEIPT_INSERT', sorted({n for t in candidates for n in inserts[t]}),
         'Insert/read table candidate only; verify it is an idempotency receipt and atomic with state update.'),
        ('REPLAY_RECEIPT_READ', sorted({n for t in candidates for n in reads[t]}),
         'Insert/read table candidate only; verify same-request replay semantics.'),
    ):
        persistence_signals.append({'code': code, 'lines': matches,
                                    'status': 'observed' if matches else 'not_observed',
                                    'recommendation': recommendation})
    return {'check_id': 'skynet-transaction-branches', 'status': 'review_needed' if findings else ('branch_review_recommended' if begin else 'not_evaluated'),
            'evidence': [{'path': relative, 'begin_lines': begin, 'commit_lines': commit, 'rollback_lines': rollback,
                          'rollback_failure_check_lines': rollback_fail_markers,
                          'potential_early_exit': findings,
                          'unknown_commit_comment_lines': unknown_commit_markers}],
            'risk_notes': risk_notes,
            'persistence_signals': persistence_signals,
            'recommendation': 'Trace rollback on every failure after BEGIN and unknown COMMIT handling; static markers do not prove control flow.',
            'blocking': False}

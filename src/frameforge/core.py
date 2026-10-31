"""Read-only, project-owned framework inspection."""
from __future__ import annotations
import json
import re
from pathlib import Path
from importlib.resources import files
from .semantic import evaluate, validate_rules
from .plugin_checks import run as run_plugin_checks, validate_profile_checks
from .remediation import advise as advise_warnings
from .custom_standards import summarize as summarize_custom_standards
from .standards_discovery import discover as discover_project_standards
from .standards_authority import resolve as resolve_standard_authority

PROFILE_PATH = '.frameforge/profile.json'
STANDARD_CANDIDATES = {
    'architecture': ['ARCHITECTURE.md', 'docs/architecture.md', 'docs/CODE-ARCHITECTURE-BASELINE-V1.md'],
    'art-ui': ['docs/art-direction.md', 'docs/ART-DIRECTION.md'],
    'asset-pipeline': ['docs/asset-pipeline.md', 'docs/ASSET-PIPELINE.md'],
}


def _validate_manifest(obj, source):
    """Reject malformed declarations before using plugin metadata."""
    if (not isinstance(obj, dict)
            or not isinstance(obj.get('id'), str)
            or not re.fullmatch(r'[a-z0-9][a-z0-9._-]*', obj['id'])
            or not isinstance(obj.get('version'), str) or not obj['version']):
        raise ValueError('Invalid plugin identity: ' + source)
    if (not isinstance(obj.get('domain'), str) or not obj['domain']
            or not isinstance(obj.get('standards'), list) or not all(isinstance(x, str) and x for x in obj['standards'])):
        raise ValueError('Invalid plugin standards: ' + source)
    if not isinstance(obj.get('detection'), list) or not all(isinstance(group, list) and group and all(isinstance(x, str) and x and not Path(x).is_absolute() and '..' not in Path(x).parts for x in group) for group in obj['detection']):
        raise ValueError('Invalid plugin detection: ' + source)
    globs = obj.get('detection_globs', [])
    if not isinstance(globs, list) or not all(
        isinstance(pattern, str) and pattern and '/' not in pattern and '\\' not in pattern
        and pattern not in ('.', '..') and not pattern.startswith('.')
        for pattern in globs
    ):
        raise ValueError('Invalid plugin detection globs: ' + source)
    markers = obj.get('content_markers', [])
    if not isinstance(markers, list) or not all(isinstance(x, dict) and isinstance(x.get('path'), str) and x['path'] and not Path(x['path']).is_absolute() and '..' not in Path(x['path']).parts and isinstance(x.get('contains'), str) and x['contains'] for x in markers):
        raise ValueError('Invalid plugin content markers: ' + source)
    checks = obj.get('advisories', [])
    if not isinstance(checks, list):
        raise ValueError('Invalid plugin advisories: ' + source)
    for check in checks:
        if not isinstance(check, dict) or not all(isinstance(check.get(k), str) and check[k] for k in ('id', 'topic', 'recommendation')):
            raise ValueError('Invalid advisory declaration: ' + source)
        paths = check.get('any_paths')
        if not isinstance(paths, list) or not paths or not all(isinstance(x, str) and x and not Path(x).is_absolute() and '..' not in Path(x).parts for x in paths):
            raise ValueError('Invalid advisory paths: ' + source)
    guidance = obj.get('professional_guidance', [])
    if not isinstance(guidance, list) or not all(
        isinstance(rule, dict) and all(isinstance(rule.get(k), str) and rule[k].strip()
        and len(rule[k]) <= 512 for k in ('id', 'topic', 'signal', 'recommendation'))
        and rule.get('source_suffix', '.cs' if obj['id']=='unity' else '.lua') in ('.cs','.lua','.asmdef')
        for rule in guidance
    ):
        raise ValueError('Invalid professional guidance: ' + source)
    return obj


def professional_preview(root, manifest):
    """Bounded source hints; unmatched signals never imply a missing capability."""
    import re
    suffix = '.cs' if manifest['id'] == 'unity' else '.lua'
    suffixes = {rule.get('source_suffix', suffix) for rule in manifest.get('professional_guidance', [])}
    evidence = []
    # Avoid following directory symlinks, and cap both directory walk and files read.
    visited = 0
    pending = [root]
    while pending and len(evidence) < 150 and visited < 3000:
        directory = pending.pop()
        try:
            children = sorted(directory.iterdir())
        except OSError:
            continue
        for path in children:
            visited += 1
            if visited > 3000:
                break
            if path.is_symlink() or path.name in ('.git', 'Library', 'Temp', 'obj', 'node_modules', 'Tests', 'tests', 'Packages', 'Editor'):
                continue
            if path.is_dir():
                pending.append(path)
                continue
            if not path.is_file() or path.suffix not in suffixes:
                continue
            rel = path.relative_to(root).as_posix()
            safe = project_file(root, rel)
            if safe is None or not safe.is_file() or safe.stat().st_size > 100_000:
                continue
            try:
                content = safe.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                continue
            pattern = (r'//[^\n]*|/\*[\s\S]*?\*/' if path.suffix in ('.cs','.asmdef')
                       else r'--\[\[[\s\S]*?\]\]|--[^\n]*')
            content = re.sub(pattern, lambda m: re.sub(r'[^\n]', ' ', m.group()), content)
            evidence.append((rel, content))
            if len(evidence) >= 150:
                break
    output = []
    for rule in manifest.get('professional_guidance', []):
        hits = [{'path': path, 'line': i}
                for path, content in evidence
                if Path(path).suffix == rule.get('source_suffix', suffix)
                for i, line in enumerate(content.splitlines(), 1)
                if rule['signal'] in line][:3]
        output.append({
            'plugin_id': manifest['id'], 'guidance_id': rule['id'],
            'topic': rule['topic'],
            'status': 'review_recommended' if hits else 'not_evaluated',
            'evidence': hits, 'recommendation': rule['recommendation'],
            'confidence': 'bounded_signal_sample' if hits else 'no_matching_signal_in_sample',
            'scan': {'files_read': len(evidence), 'entries_visited': visited,
                     'truncated': bool(pending) or visited >= 3000 or len(evidence) >= 150},
            'activation': 'explicit_selection',
        })
    return output


def advisory_preview(root, manifest):
    """Evaluate bounded, declarative evidence. No code is imported or run."""
    output = []
    for rule in manifest.get('advisories', []):
        evidence = [rel for rel in rule['any_paths'] if (target := project_file(root, rel)) is not None and target.exists() and not target.is_symlink()]
        output.append({
            'plugin_id': manifest['id'], 'rule_id': rule['id'],
            'topic': rule['topic'], 'status': 'evidence_found' if evidence else 'review_recommended',
            'evidence': evidence,
            'recommendation': rule['recommendation'],
            'confidence': 'file_presence_only',
            'activation': 'preview_only'
        })
    return output


def manifests(plugin_dir=None):
    """Load packaged metadata plus optional external JSON manifests. Never import plugin code."""
    result = {}
    sources = [(f.name, f.read_text(encoding='utf-8')) for f in files('frameforge.manifests').iterdir() if f.name.endswith('.json')]
    if plugin_dir is not None:
        directory = Path(plugin_dir)
        if not directory.is_dir():
            raise ValueError('Plugin directory missing: ' + str(directory))
        for f in sorted(directory.glob('*.json')):
            if f.is_symlink() or not f.is_file():
                continue
            sources.append((str(f), f.read_text(encoding='utf-8')))
    for source, payload in sources:
        try:
            obj = _validate_manifest(json.loads(payload), source)
        except (ValueError, TypeError) as exc:
            raise ValueError('Invalid plugin manifest ' + source + ': ' + str(exc)) from exc
        if obj['id'] in result:
            raise ValueError('Duplicate plugin identity: ' + obj['id'])
        result[obj['id']] = obj
    return result


def project_file(root, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
        return None
    path = (root / rel).resolve()
    return path if path.is_relative_to(root.resolve()) else None


def detect(root, manifest):
    evidence = []
    for group in manifest['detection']:
        if all((target := project_file(root, marker)) is not None and target.exists() for marker in group):
            evidence = group
            break
    if evidence:
        return evidence
    for pattern in manifest.get('detection_globs', []):
        # Only inspect direct children; never recurse or follow symlinks.
        matches = sorted(path.name for path in root.glob(pattern) if path.is_file() and not path.is_symlink())
        if matches:
            return [matches[0]]
    for marker in manifest.get('content_markers', []):
        target = project_file(root, marker['path'])
        if target and target.is_file() and target.stat().st_size <= 256_000:
            try:
                if marker['contains'] in target.read_text(encoding='utf-8'):
                    return [marker['path']]
            except (OSError, UnicodeError):
                pass
    return []


def inspect(project, plugin_dir=None, profile_data=None, unity_external_evidence=None):
    root = Path(project).resolve()
    if not root.is_dir():
        raise ValueError('Project directory not found: ' + str(root))
    catalog = manifests(plugin_dir)
    found = [{'plugin_id': p['id'], 'version': p['version'], 'evidence': evidence, 'status': 'suggested'} for p in catalog.values() if (evidence := detect(root, p))]
    existing = {domain: next((candidate for candidate in paths if (target := project_file(root, candidate)) is not None and target.is_file()), None) for domain, paths in STANDARD_CANDIDATES.items()}
    existing = {k: v for k, v in existing.items() if v}
    warnings = []
    selected = []
    standards = {}
    clauses = {}
    rules = []
    structural_paths = {}
    art_ui_checks = []
    art_ui_implementation_checks = []
    art_ui_unity_binding = None
    profile_path = project_file(root, PROFILE_PATH)
    if profile_data is None and (profile_path is None or not profile_path.is_file()):
        warnings.append({'code': 'PROFILE_MISSING', 'message': 'Framework profile absent; development remains allowed'})
    else:
        try:
            profile = json.loads(profile_data) if profile_data is not None else json.loads(profile_path.read_text(encoding='utf-8'))
            if not isinstance(profile, dict) or profile.get('schema_version') != 1 or not isinstance(profile.get('selected_plugins'), list) or not isinstance(profile.get('standards', {}), dict):
                raise ValueError('schema mismatch')
            selected = profile['selected_plugins']
            standards = profile.get('standards', {})
            if not all(isinstance(i, dict) and isinstance(i.get('id'), str) and i['id'] and isinstance(i.get('version'), str) and i['version'] for i in selected):
                raise ValueError('selected_plugins entries must have id and version')
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in standards.items()):
                raise ValueError('standards must be string references')
            rules = validate_rules(profile.get('semantic_rules', []))
            (art_ui_checks, art_ui_implementation_checks,
             art_ui_unity_binding, check_warnings) = validate_profile_checks(
                profile, root, standards, project_file)
            warnings.extend(check_warnings)
            structural_paths = profile.get('structural_paths', {})
            if not isinstance(structural_paths, dict) or any(
                k != 'skynet_transaction' or not isinstance(v, str) or not v
                or project_file(root, v) is None for k, v in structural_paths.items()
            ):
                raise ValueError('invalid structural_paths')
            clauses = profile.get('check_clauses', {})
            if not isinstance(clauses, dict) or not all(
                isinstance(k, str) and isinstance(v, dict)
                and isinstance(v.get('id'), str) and bool(v['id'].strip())
                and isinstance(v.get('text'), str) and bool(v['text'].strip())
                and isinstance(v.get('reference'), str) and bool(v['reference'].strip())
                for k, v in clauses.items()
            ):
                raise ValueError('check_clauses must map check IDs to id/text/reference')

        except (ValueError, OSError) as exc:
            warnings.append({'code': 'PROFILE_INVALID', 'message': str(exc)})
            selected, standards, clauses, rules, structural_paths, art_ui_checks, art_ui_implementation_checks, art_ui_unity_binding = [], {}, {}, [], {}, [], [], None
    if not selected:
        for suggestion in found:
            plugin = catalog[suggestion['plugin_id']]
            for domain in plugin['standards']:
                if domain not in existing:
                    warnings.append({'code': 'STANDARD_SUGGESTED', 'message': suggestion['plugin_id'] + ': consider defining ' + domain + ' standards; development remains allowed'})
    for item in selected:
        plugin = catalog.get(item['id'])
        if plugin is None:
            warnings.append({'code': 'PLUGIN_UNKNOWN', 'message': item['id']})
            continue
        if item['version'] != plugin['version']:
            warnings.append({'code': 'PLUGIN_VERSION_MISMATCH', 'message': item['id'] + ': selected ' + item['version'] + ', available ' + plugin['version']})
        for domain in plugin['standards']:
            ref = standards.get(domain) or existing.get(domain)
            if not ref:
                warnings.append({'code': 'STANDARD_MISSING', 'message': item['id'] + ': ' + domain})
            elif not (target := project_file(root, ref)) or not target.is_file():
                warnings.append({'code': 'STANDARD_UNAVAILABLE', 'message': item['id'] + ': ' + str(ref)})
    advisory = [entry for suggestion in found for entry in advisory_preview(root, catalog[suggestion['plugin_id']])]
    selected_versions = {item['id']: item['version'] for item in selected}
    semantic = [evaluate(root, rule) for rule in rules
                if rule['plugin_id'] in catalog
                and selected_versions.get(rule['plugin_id']) == catalog[rule['plugin_id']]['version']
                and any(s['plugin_id'] == rule['plugin_id'] for s in found)]
    # Project-owned architecture reference is the sole source of authority.
    # Discovery never silently binds standards or activates a plugin.
    chosen = {item['id'] for item in selected if item['id'] in catalog and item['version'] == catalog[item['id']]['version']}
    architecture_ref = standards.get('architecture')
    for observation in semantic:
        observation['contract'] = {'status': 'unbound', 'reference': None}
        if observation['plugin_id'] not in chosen:
            continue
        if not architecture_ref:
            observation['contract']['status'] = 'reference_missing'
        elif (source := project_file(root, architecture_ref)) is None or not source.is_file():
            observation['contract'].update(status='reference_unavailable', reference=architecture_ref)
        else:
            observation['contract'].update(status='reference_available_unverified', reference=architecture_ref)

    for observation in semantic:
        binding = observation['contract']
        clause = clauses.get(observation['check_id']) if observation['plugin_id'] in chosen else None
        if not clause:
            continue
        reference = clause['reference']
        binding.update(clause_id=clause['id'], clause_reference=reference)
        if reference != architecture_ref or binding['status'] != 'reference_available_unverified':
            binding['clause_status'] = 'reference_mismatch_or_unavailable'
            continue
        source = project_file(root, reference)
        if not source or not source.is_file() or source.stat().st_size > 500_000:
            binding['clause_status'] = 'reference_unreadable'
            continue
        try:
            content = source.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            binding['clause_status'] = 'reference_unreadable'
            continue
        lines = [i for i, line in enumerate(content.splitlines(), 1) if clause['text'] in line]
        binding['clause_status'] = 'located' if len(lines) == 1 else ('ambiguous' if lines else 'not_found')
        if len(lines) == 1:
            binding['clause_line'] = lines[0]
            binding['clause_excerpt'] = clause['text']
    professional = [entry for suggestion in found if suggestion['plugin_id'] in chosen
                    for entry in professional_preview(root, catalog[suggestion['plugin_id']])]
    art_ui_gaps, art_ui_implementation, art_ui_unity_binding_evidence, structural = run_plugin_checks(
        root, chosen, found, standards, art_ui_checks, art_ui_implementation_checks,
        art_ui_unity_binding, structural_paths, project_file, unity_external_evidence)
    custom = summarize_custom_standards(root, standards, existing, clauses, semantic, project_file)
    custom['standard_candidates'] = discover_project_standards(root, project_file)
    custom['standard_authority_review'] = resolve_standard_authority(
        custom['standard_sources'], custom['standard_candidates'])
    return {**custom, 'art_ui_unity_binding_evidence': art_ui_unity_binding_evidence, 'art_ui_implementation_evidence': art_ui_implementation, 'art_ui_standard_gaps': art_ui_gaps, 'structural_observations': structural, 'professional_guidance': professional, 'semantic_checks': semantic, 'advisories': advisory, 'schema_version': 1, 'project': str(root), 'suggested_plugins': found, 'selected_plugins': selected, 'standards': standards, 'discovered_standards': existing, 'warnings': advise_warnings(warnings), 'blocking': False}

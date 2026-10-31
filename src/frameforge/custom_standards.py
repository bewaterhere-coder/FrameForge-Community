"""Read-only source and clause coverage context for project-owned standards."""
from __future__ import annotations

from pathlib import Path


def summarize(root, standards, discovered, clauses, semantic, project_file):
    sources = []
    # Explicit profile bindings are context, not proof of owner approval.
    for domain, ref in sorted(standards.items()):
        path = project_file(root, ref)
        valid = bool(path and path.is_file() and not path.is_symlink())
        sources.append({'domain': domain, 'reference': ref, 'source': 'profile',
                        'status': 'bound_reference' if valid else 'reference_unavailable',
                        'owner_approved': 'unverified'})
    for domain, ref in sorted(discovered.items()):
        if domain not in standards:
            sources.append({'domain': domain, 'reference': ref, 'source': 'discovery',
                            'status': 'candidate_reference', 'owner_approved': 'unverified'})
    checks = {item['check_id']: item for item in semantic}
    coverage = []
    for check_id, clause in sorted(clauses.items()):
        # Only a clause actually located in a project-owned document is classified
        # as located; token scans never establish standards compliance.
        check = checks.get(check_id)
        contract = check.get('contract', {}) if check else {}
        located = contract.get('clause_status') == 'located'
        signal = check and check.get('status') == 'pattern_observed_control_flow_unverified'
        clause_status = contract.get('clause_status', 'not_evaluated')
        evidence = check.get('evidence', []) if check else []
        coverage.append({'check_id': check_id, 'clause_id': clause['id'],
                         'reference': clause['reference'],
                         'status': 'evidence_observed' if located and signal else
                                   'reference_located' if located else 'not_evaluated',
                         'compliance': 'unverified',
                         'clause_evidence': {'status': clause_status,
                                             'line': contract.get('clause_line') if located else None},
                         'code_evidence': {'status': check['status'] if check else 'not_evaluated',
                                           'locations': evidence},
                         'not_evaluated_reason': (
                             'rule_not_executed' if not check else
                             'clause_not_uniquely_located' if not located else
                             'code_signal_not_confirmed' if not signal else None)})
    return {'standard_sources': sources, 'clause_coverage': coverage}

"""Read-only project standard authority questions, never authority decisions."""

def resolve(sources, discovery):
    """Identify unbound alternatives, without inferring content conflicts."""
    bound = {s['domain']: s for s in sources if s['source'] == 'profile'}
    candidate_paths = [c['reference'] for c in discovery['candidates']]
    bound_paths = {s['reference'] for s in bound.values()}
    candidates = {c['reference']: c for c in discovery['candidates']}
    results = []
    for domain, source in sorted(bound.items()):
        alternatives = [ref for ref in candidate_paths if ref not in bound_paths]
        # Filename heuristics do not establish domain equivalence or conflict.
        results.append({'domain': domain, 'bound_reference': source['reference'],
                        'bound_status': source['status'],
                        'authority': 'owner_confirmation_unverified',
                        'other_candidates': alternatives,
                        'domain_hint_matches': [ref for ref in alternatives
                                                if domain in candidates[ref].get('domain_hints', [])],
                        'candidate_relation': 'unclassified_project_wide',
                        'potential_conflict': 'not_evaluated',
                        'action': 'review_authority_and_alternatives' if alternatives or
                                  source['status'] == 'reference_unavailable'
                                  else 'verify_project_owner_approval'})
    if not bound and candidate_paths:
        results.append({'domain': None, 'bound_reference': None,
                        'bound_status': 'unbound', 'authority': 'owner_confirmation_unverified',
                        'other_candidates': candidate_paths,
                        'candidate_relation': 'unclassified_project_wide',
                        'potential_conflict': 'not_evaluated',
                        'action': 'confirm_authoritative_project_standard'})
    return {'items': results, 'scope': 'candidate_paths_only',
            'content_conflicts_verified': False, 'blocking': False}

"""Read-only remediation hints for AI hosts; never apply project mutations."""

REMEDIATION = {
    'PROFILE_MISSING': ('inspect_project_and_propose_profile', 'project_owner_confirmation',
                        'A valid project-owned .frameforge/profile.json is present'),
    'PROFILE_INVALID': ('inspect_profile_schema_and_propose_correction', 'project_owner_confirmation',
                        'The profile parses and validates on the next inspection'),
    'STANDARD_SUGGESTED': ('locate_project_owned_standard_or_propose_definition', 'project_owner_confirmation',
                           'A relevant project standard is discoverable or explicitly bound'),
    'STANDARD_MISSING': ('find_authoritative_standard_and_propose_binding', 'project_owner_confirmation',
                          'Selected plugin has an available project-owned standard'),
    'STANDARD_UNAVAILABLE': ('verify_reference_and_propose_safe_path', 'project_owner_confirmation',
                              'The referenced standard exists inside the project root'),
    'PLUGIN_UNKNOWN': ('inspect_catalog_and_propose_plugin_selection', 'project_owner_confirmation',
                       'All selected plugin IDs resolve in the current catalog'),
    'PLUGIN_VERSION_MISMATCH': ('compare_manifest_versions_and_propose_binding', 'project_owner_confirmation',
                                'Selected version matches an available plugin version'),
    'ART_UI_CHECKS_INVALID': ('inspect_check_config_and_propose_correction', 'project_owner_confirmation',
                               'Art/UI standard checks validate on the next inspection'),
    'ART_UI_IMPLEMENTATION_CHECKS_INVALID': ('inspect_implementation_check_config', 'project_owner_confirmation',
                                              'Art/UI implementation checks validate on the next inspection'),
    'ART_UI_UNITY_BINDING_INVALID': ('inspect_unity_binding_config', 'project_owner_confirmation',
                                      'Art/UI Unity binding validates on the next inspection'),
}


def advise(warnings):
    """Enrich existing warnings; unknown codes remain actionable only by human review."""
    result = []
    for warning in warnings:
        action, approval, verification = REMEDIATION.get(
            warning['code'],
            ('review_unknown_warning', 'human_review', 'Re-inspect and establish a supported evidence-based resolution'))
        result.append({**warning, 'remediation': {
            'proposed_action': action,
            'approval': approval,
            'verification': verification,
            'status': 'needs_review',
            'auto_apply': False,
        }})
    return result

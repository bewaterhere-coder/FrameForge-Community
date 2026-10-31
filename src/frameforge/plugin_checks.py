"""Small built-in check dispatcher. Only explicitly selected, discovered plugins run."""
from .structure import unity_assemblies, skynet_transaction
from .art_ui_standards import art_ui_standard_gaps, validate_art_ui_checks
from .art_ui_evidence import evaluate as evaluate_art_ui_implementation
from .art_ui_evidence import validate as validate_art_ui_implementation_checks
from .art_ui_unity_binding import review as review_art_ui_unity_binding
from .art_ui_unity_binding import validate as validate_art_ui_binding


def validate_profile_checks(profile, root, standards, project_file):
    """Validate optional built-in professional checks behind one Core boundary."""
    warnings = []
    art_ui_checks = []
    implementation_checks = []
    unity_binding = None

    try:
        art_ui_checks = validate_art_ui_checks(profile.get('art_ui_checks', []), project_file)
    except ValueError as exc:
        warnings.append({'code': 'ART_UI_CHECKS_INVALID', 'message': str(exc)})

    try:
        implementation_checks = validate_art_ui_implementation_checks(
            profile.get('art_ui_implementation_checks', []),
            {item['id'] for item in art_ui_checks})
        standard_ref = standards.get('art-ui')
        if standard_ref and any(
            project_file(root, check['path']) == project_file(root, standard_ref)
            for check in implementation_checks
        ):
            raise ValueError('implementation evidence cannot reuse the authoritative Art/UI standard file')
    except ValueError as exc:
        warnings.append({'code': 'ART_UI_IMPLEMENTATION_CHECKS_INVALID', 'message': str(exc)})
        implementation_checks = []

    if 'art_ui_unity_binding' in profile:
        try:
            unity_binding = validate_art_ui_binding(profile['art_ui_unity_binding'])
        except ValueError as exc:
            warnings.append({'code': 'ART_UI_UNITY_BINDING_INVALID', 'message': str(exc)})

    return art_ui_checks, implementation_checks, unity_binding, warnings


def run(root, chosen, found, standards, art_ui_checks, implementation_checks,
        unity_binding, structural_paths, project_file, unity_external_evidence=None):
    active = set(chosen) & {entry['plugin_id'] for entry in found}
    gaps = (art_ui_standard_gaps(root, standards.get('art-ui'), art_ui_checks, project_file)
            if 'art-ui' in active else [])
    implementation = (evaluate_art_ui_implementation(root, implementation_checks, gaps)
                      if 'art-ui' in active else [])
    bindings = (review_art_ui_unity_binding(root, unity_binding)
                if unity_binding and {'unity', 'art-ui'} <= active else [])
    structural = []
    if 'unity' in active:
        structural.append(unity_assemblies(root, unity_external_evidence))
    if 'skynet' in active:
        structural.append(skynet_transaction(root, structural_paths.get('skynet_transaction'))
                          if structural_paths.get('skynet_transaction') else
                          {'check_id': 'skynet-transaction-branches', 'status': 'not_evaluated',
                           'evidence': [], 'blocking': False})
    return gaps, implementation, bindings, structural

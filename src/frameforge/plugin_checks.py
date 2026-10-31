"""Small built-in check dispatcher. Only explicitly selected, discovered plugins run."""
from .structure import unity_assemblies, skynet_transaction
from .art_ui_standards import art_ui_standard_gaps
from .art_ui_evidence import evaluate as evaluate_art_ui_implementation
from .art_ui_unity_binding import review as review_art_ui_unity_binding


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

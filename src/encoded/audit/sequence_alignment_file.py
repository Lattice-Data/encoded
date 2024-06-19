from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_analysis_library_types(value, system):
    '''
    An AnalysisFile should only have cellranger_assay_chemistry metadata
    if it is from an RNA-seq library.
    We expect CITE-seq libraries to be paired with RNA-seq libraries.
    '''
    if value['status'] in ['deleted']:
        return

    lib_types = set()
    for l in value.get('libraries'):
        lib_types.add(l['protocol'].get('library_type'))
    if 'RNA-seq' not in lib_types:
        if value.get('cellranger_assay_chemistry'):
            detail = ('File {} has {} and does not derive from any RNA-seq library'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                'cellranger_assay_chemistry',
                )
            )
            yield AuditFailure('cellranger spec inconsistent with library_type', detail, level="ERROR")

        if 'CITE-seq' in lib_types:
            detail = ('File {} derives from at least one CITE-seq library but does not derive from any RNA-seq library'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                'cellranger_assay_chemistry',
                )
            )
            yield AuditFailure('no RNA-seq Library with CITE-seq Library', detail, level="ERROR")
            return


function_dispatcher = {
    'audit_analysis_library_types': audit_analysis_library_types
}


@audit_checker('SequenceAlignmentFile',
               frame=[
                    'libraries',
                    'libraries.protocol'
                ])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure


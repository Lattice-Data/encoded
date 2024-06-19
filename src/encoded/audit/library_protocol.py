from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_assay(value, system):
    field = 'assay_ontology'
    if value['status'] in ['deleted'] or field not in value:
        return

    req_anc = 'single cell library construction'
    if value.get(field):
        if req_anc not in value[field].get('qa_slims',[]):
            detail = ('LibraryProtocol {} {} {} not a descendent of {}.'.format(
                audit_link(value['@id'], value['@id']),
                field,
                value[field]['term_id'],
                req_anc
                )
            )
            yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_assay': ontology_check_assay
}

@audit_checker('LibraryProtocol',
               frame=[
                    'assay_ontology'
                ])
def audit_library_protocol(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

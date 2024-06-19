from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_cell(value, system):
    field = 'cell_ontology'
    if value['status'] in ['deleted'] or field not in value:
        return

    dbs = ['CL']
    terms = ['NCIT:C17998']

    term = value[field]['term_id']
    ont_db = term.split(':')[0]
    if ont_db not in dbs and term not in terms:
        detail = ('CellAnnotation {} {} {} not from {} or {}.'.format(
            audit_link(value['@id'], value['@id']),
            field,
            term,
            ','.join(dbs),
            ','.join(terms)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_cell': ontology_check_cell
}

@audit_checker('CellAnnotation',
               frame=[
                    'cell_ontology'
                ])
def audit_cell_annotation(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

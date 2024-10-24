from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_bio(value, system):
    field = 'biosample_ontology'
    if value['status'] in ['deleted'] or field not in value:
        return

    dbs = ['UBERON','NTR']

    term = value[field]['term_id']
    ont_db = term.split(':')[0]
    if ont_db not in dbs:
        detail = ('Organoid {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            term,
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_bio': ontology_check_bio
}

@audit_checker('Organoid',
               frame=[
                    'biosample_ontology'
                ])
def audit_organoid(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

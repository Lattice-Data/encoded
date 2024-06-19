from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_bmi(value, system):
    if value['status'] in ['deleted']:
        return

    if 'body_mass_index_at_collection' in value:
        for d in value['donors']:
            if d.get('body_mass_index') != 'variable':
                detail = ('Biosample {} has BMI at collection specific but donor {} BMI is not variable.'.format(
                    audit_link(value['accession'], value['@id']),
                    d['accession']
                    )
                )
                yield AuditFailure('inconsistent BMI', detail, level='ERROR')
                return


def audit_death_prop_living_donor(value, system):
    '''
    A biosample should not have a property indicating time since death
    if it is associated with a living donor.
    '''
    if value['status'] in ['deleted']:
        return

    for donor in value['donors']:
        if donor.get('living_at_sample_collection') == "True" and value.get('death_to_preservation_interval'):
            detail = ('Biosample {} has death_to_preservation_interval but is associated with at least one donor that is living at sample collection.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('death interval for living donor', detail, level='ERROR')
            return


def ontology_check_dis(value, system):
    if value['status'] in ['deleted']:
        return

    field = 'diseases'
    dbs = ['MONDO']

    invalid  = []
    for d in value.get(field, []):
        term = d['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Biosample {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'audit_bmi': audit_bmi,
    'audit_death_prop_living_donor': audit_death_prop_living_donor,
    'ontology_check_dis': ontology_check_dis
}

@audit_checker('Biosample',
               frame=[
                    'donors',
                    'diseases'
                ])
def audit_biosample(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

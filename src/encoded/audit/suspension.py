from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_suspension_intervals(value, system):
    '''
    A Suspension should have a donor.
    '''
    if value['status'] in ['deleted']:
        return

    int_field = None
    if 'collection_to_dissociation_interval' in value:
        int_field = 'collection_to_dissociation_interval'
    if 'death_to_dissociation_interval' in value:
        int_field = 'death_to_dissociation_interval'

    if int_field:
        int_flag = False
        if value['derived_from'][0]['@type'][0] == 'Suspension':
            for d in value['derived_from']:
                if 'collection_to_dissociation_interval' in d or 'death_to_dissociation_interval' in d:
                    int_flag = True
                else:
                    for dd in d['derived_from']:
                        if 'collection_to_preservation_interval' in dd or 'death_to_preservation_interval' in dd:
                            int_flag = True
        else:
            for d in value['derived_from']:
                if 'collection_to_preservation_interval' in d or 'death_to_preservation_interval' in d:
                    int_flag = True

        if int_flag == True:
            detail = ('Suspension {} has {} value but an interval field is present in one more more derived_from objects'.format(
                audit_link(value['accession'], value['@id']),
                int_field
                )
            )
            yield AuditFailure('multiple tissue handling intervals', detail, level='ERROR')
            return


def audit_death_prop_living_donor(value, system):
    '''
    A suspension should not have a property indicating time since death
    if it is associated with a living donor.
    '''
    if value['status'] in ['deleted']:
        return

    living_donor_flag = False
    for donor in value['donors']:
        if donor.get('living_at_sample_collection') == True:
            living_donor_flag = True
    if living_donor_flag == True and value.get('death_to_dissociation_interval'):
        detail = ('Biosample {} has property {} but is associated with at least one donor that is living at sample collection.'.format(
            audit_link(value['accession'], value['@id']),
            death_prop
            )
        )
        yield AuditFailure('death interval for living donor', detail, level='ERROR')
        return


def ontology_check_enr(value, system):
    if value['status'] in ['deleted']:
        return

    field = 'enriched_cell_types'
    dbs = ['CL']

    invalid = []
    for e in value.get(field, []):
        term = e['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Suspension {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def ontology_check_dep(value, system):
    if value['status'] in ['deleted']:
        return

    field = 'depleted_cell_types'
    dbs = ['CL']

    invalid = []
    for e in value.get(field, []):
        term = e['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Suspension {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'audit_suspension_intervals': audit_suspension_intervals,
    'audit_death_prop_living_donor': audit_death_prop_living_donor,
    'ontology_check_enr': ontology_check_enr,
    'ontology_check_dep': ontology_check_dep
}

@audit_checker('Suspension',
               frame=[
                    'donors',
                    'enriched_cell_types',
                    'depleted_cell_types',
                    'derived_from',
                    'derived_from.derived_from'
                ])
def audit_suspension(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

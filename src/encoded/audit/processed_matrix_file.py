from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def mappings_antibodies(value,system):
    if value.get('antibody_mappings'):
        labels = [am['label'] for am in value['antibody_mappings']]
        dups = [l for l in labels if labels.count(l) > 1]
        if dups:
            detail = ('File {} contains duplicate labels {} in antibody_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(dups))
                )
            )
            yield AuditFailure('antibody_mapping error', detail, 'ERROR')

        antibodies = []
        for l in value['libraries']:
            for susp in l['derived_from']:
                antibodies.extend(susp.get('feature_antibodies',[]))
        for am in value['antibody_mappings']:
            if am['antibody'] not in antibodies:
                detail = ('File {} contains {} in antibody_mappings but is not linked to this Antibody.'.format(
                    audit_link(value['accession'], value['@id']),
                    am['antibody']
                    )
                )
                yield AuditFailure('antibody_mapping error', detail, 'ERROR')


def mappings_donors(value,system):
    if value.get('donor_mappings'):
        labels = [dm['label'] for dm in value['donor_mappings']]
        dups = [l for l in labels if labels.count(l) > 1]
        if dups:
            detail = ('File {} contains duplicate labels {} in donor_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(dups))
                )
            )
            yield AuditFailure('donor_mappings error', detail, 'ERROR')

        donors = []
        for l in value['libraries']:
            donors.extend(l['donors'])
        for dm in value['donor_mappings']:
            if dm['donor'] not in donors:
                detail = ('File {} contains {} in donor_mappings but is not linked to this Donor.'.format(
                    audit_link(value['accession'], value['@id']),
                    dm['donor']
                    )
                )
                yield AuditFailure('donor_mappings error', detail, 'ERROR')


def mappings_matrices(value,system):
    if value.get('cell_label_mappings'):
        labels = [clm['label'] for clm in value['cell_label_mappings']]
        dups = [l for l in labels if labels.count(l) > 1]
        if dups:
            detail = ('File {} contains duplicate labels {} in cell_label_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(dups))
                )
            )
            yield AuditFailure('cell_label_mappings error', detail, 'ERROR')

        for clm in value['cell_label_mappings']:
            derived_from = [d['@id'] for d in value['derived_from']]
            if clm['raw_matrix'] not in derived_from:
                detail = ('File {} contains {} in cell_label_mappings but not derived_from.'.format(
                    audit_link(value['accession'], value['@id']),
                    clm['raw_matrix']
                    )
                )
                yield AuditFailure('cell_label_mappings error', detail, 'ERROR')


def ontology_check_dis(value, system):
    field = 'experimental_variable_disease'
    dbs = ['MONDO']

    ontobj = value.get(field)
    if ontobj:
        term = ontobj['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            detail = ('File {} {} {} not from {}.'.format(
                audit_link(value['accession'], value['@id']),
                field,
                term,
                ','.join(dbs)
                )
            )
            yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def duplicated_derfrom(value, system):
    all_seq_files = {}
    for raw in value['derived_from']:
        for seqfile in raw['derived_from']:
            if seqfile in all_seq_files:
                all_seq_files[seqfile].append(raw['accession'])
            else:
                all_seq_files[seqfile] = [raw['accession']]

    for k,v in all_seq_files.items():
        if len(v) > 1:
            detail = ('File {} has duplicated input {} from RawMatrixFiles {}.'.format(
                audit_link(value['accession'], value['@id']),
                k,
                ','.join(v)
                )
            )
            yield AuditFailure('duplicate input raw data', detail, 'ERROR')


def cellxgene_links(value, system):
    if 'cellxgene_uuid' in value and len(value['dataset']['cellxgene_urls']) == 0:
        detail = ('File {} has cellxgene_uuid but {} has no cellxgene_urls.'.format(
            audit_link(value['accession'], value['@id']),
            value['dataset']['accession']
            )
        )
        yield AuditFailure('missing cellxgene link', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_dis': ontology_check_dis,
    'duplicated_derfrom': duplicated_derfrom,
    'mappings_antibodies': mappings_antibodies,
    'mappings_donors': mappings_donors,
    'mappings_matrices': mappings_matrices,
    'cellxgene_links': cellxgene_links
}

@audit_checker('ProcessedMatrixFile',
               frame=[
                'experimental_variable_disease',
                'derived_from',
                'libraries',
                'libraries.derived_from',
                'dataset'
                ])
def audit_processed_matrix_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

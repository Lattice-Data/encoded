from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def cell_type_col_in_author_cols(value,system):
    if value.get('author_columns') and value.get('author_cell_type_column'):
        if value['author_cell_type_column'] in value['author_columns']:
            detail = ('File {} lists {} in author_columns and author_cell_type_column.'.format(
                audit_link(value['accession'], value['@id']),
                value['author_cell_type_column']
                )
            )
            yield AuditFailure('author_cell_type_column in author_columns', detail, 'ERROR')


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
        suspensions = []
        for l in value['libraries']:
            for susp in l['derived_from']:
                if susp['@id'] not in suspensions:
                    antibodies.extend(susp.get('feature_antibodies',[]))
                    suspensions.append(susp['@id'])
        for am in value['antibody_mappings']:
            if am['antibody']['@id'] not in antibodies:
                detail = ('File {} contains {} in antibody_mappings but is not linked to this Antibody. These Suspensions are currently linked: {}'.format(
                    audit_link(value['accession'], value['@id']),
                    am['antibody']['@id'],
                    ','.join(suspensions)
                    )
                )
                yield AuditFailure('antibody_mapping error', detail, 'ERROR')

            target_orgs = [t['organism'] for t in am['antibody'].get('targets', [{'organism': 'control'}])]
            if '/organisms/human/' not in target_orgs and 'control' not in target_orgs:
                detail = ('File {} contains {} in antibody_mappings that does not target human or a control.'.format(
                    audit_link(value['accession'], value['@id']),
                    am['antibody']['@id']
                    )
                )
                yield AuditFailure('antibody_mapping to non-human', detail, 'ERROR')


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

        mxs = [clm['raw_matrix'] for clm in value['cell_label_mappings']]
        dups = [m for m in mxs if mxs.count(m) > 1]
        if dups:
            detail = ('File {} contains duplicate raw_matrix {} in cell_label_mappings.'.format(
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
    if 'cellxgene_uuid' in value and len(value['dataset'].get('cellxgene_urls',[])) == 0:
        detail = ('File {} has cellxgene_uuid but {} has no cellxgene_urls.'.format(
            audit_link(value['accession'], value['@id']),
            value['dataset']['accession']
            )
        )
        yield AuditFailure('missing cellxgene link', detail, 'ERROR')

    elif 'cellxgene_uuid' not in value and len(value['dataset'].get('cellxgene_urls',[])) > 0:
        if value['output_types'] == ['gene quantifications']:
            detail = ('{} has cellxgene_urls but File {} has no cellxgene_uuid.'.format(
                value['dataset']['accession'],
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('missing cellxgene uuid', detail, 'ERROR')


def check_author_columns(value, system):
    reserved = ['assay','cell_type','development_stage',
        'disease','self_reported_ethnicity','organism',
        'sex','tissue','donor_id','is_primary_data','suspension_type',
        'tissue_type']

    clash = [c for c in value.get('author_columns',[]) if c in reserved]
    if clash:
        detail = ('File {} lists reserved fields in author_columns: {}.'.format(
            audit_link(value['accession'], value['@id']),
            ','.join(clash)
            )
        )
        yield AuditFailure('CxG schema clash', detail, 'ERROR')


def gene_activity_genome_annotation(value, system):
    gene_act_assays = ['snATAC-seq','scMethyl-seq','snMethyl-seq']
    matching_assays = [a for a in value.get('assays',[]) if a in gene_act_assays]

    if value.get('gene_activity_genome_annotation'):
        if value.get('output_types') != ['gene quantifications']:
            detail = ('File {} has gene_activity_genome_annotation but output_types is not gene quantifications.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('gene activity inconsistency', detail, 'ERROR')

        if len(matching_assays) == 0:
            detail = ('File {} has gene_activity_genome_annotation but no epigenetic assay.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('gene activity inconsistency', detail, 'ERROR')

    elif value.get('output_types') == ['gene quantifications'] and len(matching_assays) == len(value.get('assays',[])):
        detail = ('File {} has no gene_activity_genome_annotation filled in.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('gene activity inconsistency', detail, 'ERROR')


function_dispatcher = {
    'cell_type_col_in_author_cols': cell_type_col_in_author_cols,
    'ontology_check_dis': ontology_check_dis,
    'duplicated_derfrom': duplicated_derfrom,
    'mappings_antibodies': mappings_antibodies,
    'mappings_donors': mappings_donors,
    'mappings_matrices': mappings_matrices,
    'cellxgene_links': cellxgene_links,
    'check_author_columns': check_author_columns,
    'gene_activity_genome_annotation': gene_activity_genome_annotation
}

@audit_checker('ProcessedMatrixFile',
               frame=[
                'antibody_mappings',
                'antibody_mappings.antibody',
                'antibody_mappings.antibody.targets',
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

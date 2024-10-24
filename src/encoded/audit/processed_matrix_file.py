from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def spatial(value,system):
    if value['status'] in ['deleted']:
        return

    spatial_protocols = [
        'Visium-10x-GE',
        'Slide-seq2'
    ]
    assays = [l['protocol'] for l in value['libraries']]
    spatial_match = [p for p in assays if p.split('/')[2] in spatial_protocols]
    if spatial_match:
        if len(set(assays)) > 1:
            detail = ('File {} is data integrated from unexpected assays: {}.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(assays))
                )
            )
            yield AuditFailure('spatial cross-assay integration', detail, 'ERROR')
    if set(assays) == {'/library-protocols/Visium-10x-GE/'} and len(value['libraries']) == 1:
        for df in value['derived_from']:
            if df['background_barcodes_included'] != True:
                detail = ('File {} is derived_from some files without background_barcodes_included.'.format(
                    audit_link(value['accession'], value['@id'])
                    )
                )
                yield AuditFailure('single Visium needs background barcodes', detail, 'ERROR')
        if not value.get('spatial_s3_uri'):
            detail = ('File {} is from a single Visium Library missing spatial_s3_uri.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('missing spatial_s3_uri', detail, 'ERROR')
    elif value.get('spatial_s3_uri'):
        detail = ('File {} has spatial_s3_uri but is not from a single Visium Library.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('non-single-Visium with spatial_s3_uri', detail, 'ERROR')


def cell_type_col_in_author_cols(value,system):
    if value['status'] in ['deleted']:
        return

    if value.get('author_columns') and value.get('author_cell_type_column'):
        if value['author_cell_type_column'] in value['author_columns']:
            detail = ('File {} lists {} in author_columns and author_cell_type_column.'.format(
                audit_link(value['accession'], value['@id']),
                value['author_cell_type_column']
                )
            )
            yield AuditFailure('author_cell_type_column in author_columns', detail, 'ERROR')


def mappings_antibodies(value,system):
    if value['status'] in ['deleted']:
        return

    if value.get('antibody_mappings'):
        request = system['request']
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
            for s in l['derived_from']:
                susp = request.embed(s + '@@object')
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
    if value['status'] in ['deleted']:
        return

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
    if value['status'] in ['deleted']:
        return

    if value.get('cell_label_mappings'):
        derived_from = [d['@id'] for d in value['derived_from']]
        mxs = [clm['raw_matrix'] for clm in value['cell_label_mappings']]
        labels = [clm['label'] for clm in value['cell_label_mappings']]

        dup_labels = [l for l in labels if labels.count(l) > 1]
        if dup_labels:
            detail = ('File {} contains duplicate labels {} in cell_label_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(dup_labels))
                )
            )
            yield AuditFailure('cell_label_mappings error', detail, 'ERROR')

        dup_mxs = [m for m in mxs if mxs.count(m) > 1]
        if dup_mxs:
            detail = ('File {} contains duplicate raw_matrix {} in cell_label_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(set(dup_mxs))
                )
            )
            yield AuditFailure('cell_label_mappings error', detail, 'ERROR')


        missing_in_df = [m for m in mxs if m not in derived_from]
        if missing_in_df:
            detail = ('File {} contains {} in cell_label_mappings but not derived_from.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(missing_in_df)
                )
            )
            yield AuditFailure('cell_label_mappings error', detail, 'ERROR')

        missing_in_clm = [d for d in derived_from if d not in mxs]
        if missing_in_clm:
            detail = ('File {} contains {} in derived_from but not cell_label_mappings.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(missing_in_clm)
                )
            )
            yield AuditFailure('cell_label_mappings error', detail, 'ERROR')


def ontology_check_disease(value, system):
    if value['status'] in ['deleted']:
        return

    if 'experimental_variable_disease' in value:
        lib_diseases = set()
        for l in value['libraries']:
            lib_diseases.update(l.get('diseases'))
        for d in value['experimental_variable_disease']:
            if d['term_name'] not in lib_diseases:
                detail = ('File {} experimental_variable_disease {} not in associated samples and donors.'.format(
                    audit_link(value['accession'], value['@id']),
                    d['term_name'],
                    )
                )
                yield AuditFailure('experimental_variable_disease error', detail, 'ERROR')


def duplicated_derfrom(value, system):
    if value['status'] in ['deleted']:
        return

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
    if value['status'] in ['deleted']:
        return

    if 'cellxgene_uuid' in value and len(value['dataset'].get('cellxgene_urls',[])) == 0:
        detail = ('File {} has cellxgene_uuid but {} has no cellxgene_urls.'.format(
            audit_link(value['accession'], value['@id']),
            value['dataset']['accession']
            )
        )
        yield AuditFailure('missing cellxgene link', detail, 'ERROR')
        return

    if 'cellxgene_uuid' not in value and len(value['dataset'].get('cellxgene_urls',[])) > 0:
        if value['output_types'] == ['gene quantifications']:
            detail = ('{} has cellxgene_urls but File {} has no cellxgene_uuid.'.format(
                value['dataset']['accession'],
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('missing cellxgene uuid', detail, 'ERROR')
            return


def check_author_columns(value, system):
    if value['status'] in ['deleted']:
        return

    if 'author_columns' in value:

        reserved = ['assay','cell_type','development_stage',
            'disease','self_reported_ethnicity','organism',
            'sex','tissue','donor_id','is_primary_data','suspension_type',
            'tissue_type']

        clash = [c for c in value['author_columns'] if c in reserved]
        if clash:
            detail = ('File {} lists reserved fields in author_columns: {}.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(clash)
                )
            )
            yield AuditFailure('CxG schema clash', detail, 'ERROR')


def gene_activity_genome_annotation(value, system):
    if value['status'] in ['deleted']:
        return

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
    'spatial': spatial,
    'cell_type_col_in_author_cols': cell_type_col_in_author_cols,
    'ontology_check_disease': ontology_check_disease,
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
                    'dataset'
                ])
def audit_processed_matrix_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

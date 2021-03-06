from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .shared_calculated_properties import (
    CalculatedAward,
    CalculatedBiosampleOntologies,
    CalculatedBiosampleClassification,
    CalculatedBiosampleSummary,
)


@collection(
    name='libraries',
    unique_key='accession',
    properties={
        'title': 'Libraries',
        'description': 'Libraries used in the ENCODE project',
    })
class Library(Item,
            CalculatedAward,
            CalculatedBiosampleOntologies,
            CalculatedBiosampleClassification,
            CalculatedBiosampleSummary):
    item_type = 'library'
    schema = load_schema('encoded:schemas/library.json')
    name_key = 'accession'
    rev = {
        'sequencing_runs': ('SequencingRun','derived_from'),
        'direct_raw_mx': ('RawMatrixFile', 'derived_from')
    }
    embedded = [
        'award',
        'award.coordinating_pi',
        'lab',
        'protocol',
        'protocol.assay_ontology',
        'donors',
        'donors.ethnicity',
        'donors.diseases',
        'donors.development_ontology',
        'donors.organism',
        'biosample_ontologies',
        'derived_from'
    ]


    @calculated_property(schema={
        "title": "Observation count",
        "description": "The number of cells and nuclei from this library that have raw counts submitted.",
        "comment": "Do not submit.",
        "type": "integer",
        "notSubmittable": True,
    })
    def observation_count(self, request, sequencing_runs, direct_raw_mx=None):
        matrices = set()

        if direct_raw_mx:
            matrices.update(paths_filtered_by_status(request, direct_raw_mx))
        for sr in sequencing_runs:
            sr_obj = request.embed(sr, '@@object')
            if sr_obj.get('files'):
                for f in sr_obj['files']:
                    f_obj = request.embed(f, '@@object')
                    if f_obj.get('raw_matrix_files'):
                        matrices.update(f_obj['raw_matrix_files'])
        count = 0
        for m in matrices:
            mx_obj = request.embed(m, '@@object?skip_calculated=true')
            if mx_obj.get('observation_count') and mx_obj.get('background_barcodes_included') != True:
                count += mx_obj['observation_count']

        if count > 0:
            return count


    @calculated_property(schema={
        "title": "Sequencing runs",
        "description": "The sequencing runs that derive from this library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "SequencingRun.derived_from",
        },
        "notSubmittable": True,
    })
    def sequencing_runs(self, request, sequencing_runs=None):
        if sequencing_runs:
            return paths_filtered_by_status(request, sequencing_runs)


    @calculated_property(schema={
        "title": "Read count",
        "description": "The number of reads sequenced from this library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def read_count(self, request, sequencing_runs):
        count = 0
        for sr in sequencing_runs:
            props = request.embed(sr, '@@object')
            count += props.get('read_count',0)
        if count > 0:
            return count


    @calculated_property(condition='protocol', schema={
        "title": "Assay",
        "description": "The general assay used for this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "enum": [
            "snATAC-seq",
            "scRNA-seq",
            "snRNA-seq",
            "CITE-seq",
            "bulk ATAC-seq",
            "bulk RNA-seq",
            "spatial transcriptomics"
        ]
    })
    def assay(self, request, derived_from, protocol):
        protocolObject = request.embed(protocol, '@@object?skip_calculated=true')
        if protocolObject.get('library_type') in ['CITE-seq']:
            return protocolObject.get('library_type')
        elif derived_from:
            derfrObject = request.embed(derived_from[0], '@@object')
            df_type = derfrObject['@type'][0]
            if df_type == 'TissueSection' and protocolObject.get('library_type') == 'RNA-seq':
                return 'spatial transcriptomics'
            elif df_type != 'Suspension':
                mat_type = 'bulk '
            elif derfrObject.get('suspension_type') == 'cell':
                mat_type = 'sc'
            elif derfrObject.get('suspension_type') == 'nucleus':
                mat_type = 'sn'
            else:
                return protocolObject.get('library_type')
            return mat_type + protocolObject.get('library_type')
        else:
            return protocolObject.get('library_type')


    @calculated_property(condition='derived_from', schema={
        "title": "Donors",
        "description": "The donors from which samples were taken from to generate this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Donor"
        },
    })
    def donors(self, request, derived_from):
        all_donors = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            all_donors.update(bs_obj.get('donors'))
        return sorted(all_donors)


    summary_matrix = {
        'x': {
            'group_by': 'donors.ethnicity.term_name'
        },
        'y': {
            'group_by': ['donors.sex']
        }
    }

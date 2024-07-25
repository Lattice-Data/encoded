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
        'donors.causes_of_death',
        'donors.diseases',
        'donors.development_ontology',
        'donors.family_medical_history.diagnosis',
        'donors.organism',
        'biosample_ontologies',
        'derived_from',
        'derived_from.enriched_cell_types',
        'derived_from.depleted_cell_types'
    ]


    @calculated_property(condition='protocol', schema={
        "title": "Assay",
        "description": "The general assay used for this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string"
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


    @calculated_property(condition='derived_from', schema={
        "title": "Diseases",
        "description": "The diseases effecting both the donor and the specific sample used to generate this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string"
        },
    })
    def diseases(self, request, derived_from):
        all_diseases = set()

        seen = set()
        remaining = derived_from
        while remaining:
            seen.update(remaining)
            next_remaining = set()
            for i in remaining:
                temp_obj = request.embed(i, '@@object')
                if 'diseases' in temp_obj:
                    for d in temp_obj['diseases']:
                        if d not in seen:
                            ont = request.embed(d, '@@object')
                            all_diseases.add(ont['term_name'])
                            seen.add(d)
                if temp_obj.get('derived_from'):
                    next_remaining.update(temp_obj['derived_from'])
            remaining = next_remaining - seen

        return sorted(all_diseases)


    @calculated_property(condition='derived_from', define=True, schema={
        "title": "Biosample ontologies",
        "description": "An embedded property for linking to biosample type which describes the ontology of the samples the suspension derived from.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "OntologyTerm"
        },
    })
    def biosample_ontologies(self, request, derived_from):
        onts = set()
        for df in derived_from:
            df_obj = request.embed(df, '@@object')
            if df_obj.get('biosample_ontology'):
                onts.add(df_obj['biosample_ontology'])
            else:
                for doubdf in df_obj['derived_from']:
                    doubdf_obj = request.embed(doubdf, '@@object')
                    if doubdf_obj.get('biosample_ontology'):
                        onts.add(doubdf_obj['biosample_ontology'])
                    else:
                        for tripdf in doubdf_obj['derived_from']:
                            tripdf_obj = request.embed(tripdf, '@@object')
                            if tripdf_obj.get('biosample_ontology'):
                                onts.add(tripdf_obj['biosample_ontology'])
                            else:
                                for quaddf in tripdf_obj['derived_from']:
                                    quaddf_obj = request.embed(quaddf, '@@object')
                                    if quaddf_obj.get('biosample_ontology'):
                                        onts.add(quaddf_obj['biosample_ontology'])
        return sorted(onts)


    summary_matrix = {
        'x': {
            'group_by': 'donors.ethnicity.term_name'
        },
        'y': {
            'group_by': ['donors.sex']
        }
    }

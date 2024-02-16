from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    pluralize,
)
from .shared_calculated_properties import (
    CalculatedDonors,
    CalculatedBiosampleOntologies,
    CalculatedBiosampleClassification,
    CalculatedBiosampleSummary,
    CalculatedTreatmentSummary,
)


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Item, 
                CalculatedDonors,
                CalculatedBiosampleOntologies,
                CalculatedBiosampleClassification,
                CalculatedBiosampleSummary,
                CalculatedTreatmentSummary):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    name_key = 'accession'
    embedded = [
        'biosample_ontologies',
        'donors',
        'donors.organism',
        'enriched_cell_types',
        'depleted_cell_types',
        'donors.ethnicity',
        'donors.diseases',
        'donors.development_ontology',
        'feature_antibodies',
        'feature_antibodies.targets'
    ]


    @calculated_property(schema={
        "title": "Tissue handling interval",
        "description": "",
        "comment": "Do not submit.",
        "type": "string",
        "notSubmittable": True,
    })
    def tissue_handling_interval(
        self, request, biosample_classification, derived_from,
        collection_to_dissociation_interval=None, collection_to_dissociation_interval_units=None,
        death_to_dissociation_interval=None, death_to_dissociation_interval_units=None):
        if collection_to_dissociation_interval:
            return pluralize(collection_to_dissociation_interval, collection_to_dissociation_interval_units)
        if death_to_dissociation_interval:
            return pluralize(death_to_dissociation_interval, death_to_dissociation_interval_units)

        intervals = {'collection': [], 'death': []}
        for df in derived_from:
            derfrObject = request.embed(df, '@@object')
            if derfrObject['@type'][0] == 'Tissue':
                if 'collection_to_preservation_interval' in derfrObject:
                    interval = derfrObject['collection_to_preservation_interval']
                    units = derfrObject['collection_to_preservation_interval_units']
                    intervals['collection'].append(pluralize(interval, units))
                else:
                    intervals['collection'].append('unknown')
                if 'death_to_preservation_interval' in derfrObject:
                    interval = derfrObject['death_to_preservation_interval']
                    units = derfrObject['death_to_preservation_interval_units']
                    intervals['death'].append(pluralize(interval, units))
                else:
                    intervals['death'].append('unknown')

            elif derfrObject['@type'][0] == 'Suspension':
                for dfdf in derfrObject['derived_from']:
                    doubleDerfrObject = request.embed(dfdf, '@@object')
                    if doubleDerfrObject['@type'][0] == 'Tissue':
                        if 'collection_to_preservation_interval' in doubleDerfrObject:
                            interval = doubleDerfrObject['collection_to_preservation_interval']
                            units = doubleDerfrObject['collection_to_preservation_interval_units']
                            intervals['collection'].append(pluralize(interval, units))
                        else:
                            intervals['collection'].append('unknown')
                        if 'death_to_preservation_interval' in doubleDerfrObject:
                            interval = doubleDerfrObject['death_to_preservation_interval']
                            units = doubleDerfrObject['death_to_preservation_interval_units']
                            intervals['death'].append(pluralize(interval, units))
                        else:
                            intervals['death'].append('unknown')
        if set(intervals['death']) == {'unknown'} and set(intervals['collection']) != {'unknown'}:
            return ','.join(set(intervals['collection']))
        if set(intervals['death']) != {'unknown'} and set(intervals['collection']) == {'unknown'}:
            return ','.join(set(intervals['death']))

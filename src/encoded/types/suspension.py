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
        intervals = []
        if collection_to_dissociation_interval:
            intervals.append((collection_to_dissociation_interval, collection_to_dissociation_interval_units))
        if death_to_dissociation_interval:
            intervals.append((death_to_dissociation_interval, death_to_dissociation_interval_units))

        derfrObject = request.embed(derived_from[0], '@@object')
        if derfrObject['@type'][0] == 'Tissue':
            if len(derived_from) == 1:
                if 'collection_to_preservation_interval' in derfrObject:
                    interval = derfrObject['collection_to_preservation_interval']
                    units = derfrObject['collection_to_preservation_interval_units']
                    intervals.append((interval, units))
                if 'death_to_preservation_interval' in derfrObject:
                    interval = derfrObject['death_to_preservation_interval']
                    units = derfrObject['death_to_preservation_interval_units']
                    intervals.append((interval, units))

        elif derfrObject['@type'][0] == 'Suspension':
            doubleDerfrObject = request.embed(derfrObject['derived_from'][0], '@@object')
            if doubleDerfrObject['@type'][0] == 'Tissue':
                all_derives = []
                for d in derived_from:
                    df_obj = request.embed(d, '@@object')
                    for dd in df_obj['derived_from']:
                        if dd not in all_derives:
                            all_derives.append(dd)
                if len(all_derives) == 1:
                    if 'collection_to_preservation_interval' in doubleDerfrObject:
                        interval = doubleDerfrObject['collection_to_preservation_interval']
                        units = doubleDerfrObject['collection_to_preservation_interval_units']
                        intervals.append((interval, units))
                    if 'death_to_preservation_interval' in doubleDerfrObject:
                        interval = doubleDerfrObject['death_to_preservation_interval']
                        units = doubleDerfrObject['death_to_preservation_interval_units']
                        intervals.append((interval, units))
        if len(intervals) == 1:
            return pluralize(intervals[0][0], intervals[0][1])

from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)
from .shared_calculated_properties import (
    CalculatedDonors,
    CalculatedBiosampleClassification,
    CalculatedBiosampleSummary,
)


@collection(
    name='tissue-sections',
    unique_key='accession',
    properties={
        'title': 'Tissue sections',
        'description': 'Listing of Tissue sections',
    })
class TissueSection(Item, 
                CalculatedDonors,
                CalculatedBiosampleClassification,
                CalculatedBiosampleSummary):
    item_type = 'tissue_section'
    schema = load_schema('encoded:schemas/tissue_section.json')
    name_key = 'accession'
    embedded = [
        'donors',
        'donors.organism',
        'donors.ethnicity',
        'donors.diseases'
    ]

from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)


@collection(
    name='cell-annotations',
    properties={
        'title': 'Cell annotations',
        'description': 'Listing of cell annotations',
    })
class CellAnnotation(Item):
    item_type = 'cell_annotation'
    schema = load_schema('encoded:schemas/cell_annotation.json')
    embedded = [
        'cell_ontology'
    ]
    audit_inherit = ['cell_ontology']

from snovault import (
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


def property_closure(request, propname, root_uuid):
    # Must avoid cycles
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen

@collection(
    name='libraries',
    unique_key='accession',
    properties={
        'title': 'Libraries',
        'description': 'Libraries used in the ENCODE project',
    })
class Library(Item):
    item_type = 'library'
    schema = load_schema('encoded:schemas/library.json')
    name_key = 'accession'
    rev = {}
    embedded = [
        'derived_from',
        'derived_from.biosample_ontology',
        'protocol',
        'dataset',
        'dataset.award',
        'lab'
    ]


    @calculated_property(condition='derived_from', schema={
        "title": "Assay",
        "type": "string"
    })
    def assay(self, request, derived_from, protocol):
        protocolObject = request.embed(protocol, '@@object')
        if protocolObject.get('library_type') in ['CITE-seq']:
            return protocolObject.get('library_type')
        else:
            derfrObject = request.embed(derived_from[0], '@@object')
            if derfrObject.get('suspension_type') == 'cell':
                mat_type = 'sc'
            elif derfrObject.get('suspension_type') == 'nucleus':
                mat_type = 'sn'
            else:
                mat_type = 'bulk '
            return mat_type + protocolObject.get('library_type')


    @calculated_property(condition='derived_from', schema={
        "title": "Donor accessions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Donor"
        },
    })
    def donor_accessions(self, request, registry, derived_from, status):
        conn = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid)
        obj_props = (conn.get_by_uuid(uuid).__json__(request) for uuid in derived_from_closure)
        # use organism as a proxy for donors because 'Donor in props['@type']' returned keyError
        donor_accs = {
            props['accession']
            for props in obj_props
            if 'organism' in props
        }
        return donor_accs

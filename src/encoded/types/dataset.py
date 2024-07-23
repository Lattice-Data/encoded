from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


def gather_urls(urls, start):
    links = []
    for u in urls:
        if u.startswith(start):
            links.append(u)
    return links


def item_is_revoked(request, path):
    return request.embed(path, '@@object?skip_calculated=true').get('status') == 'revoked'


@collection(
    name='datasets',
    unique_key='accession',
    properties={
        'title': 'Datasets',
        'description': 'Listing of Datasets',
    })
class Dataset(Item):
    item_type = 'dataset'
    schema = load_schema('encoded:schemas/dataset.json')
    name_key = 'accession'
    embedded = [
        'libraries',
        'award',
        'award.coordinating_pi',
        'references',
        'corresponding_contributors',
        'contributors',
        'internal_contact'
    ]
    rev = {
        'libraries': ('Library','dataset'),
        'original_files': ('DataFile','dataset')
    }
    audit_inherit = [
        'original_files',
        'original_files.derived_from',
        'libraries',
        'libraries.donors',
        'libraries.derived_from',
        'libraries.protocol'
    ]


    @calculated_property(schema={
        "title": "Libraries",
        "description": "The Libraries that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Library.dataset",
        },
        "notSubmittable": True,
    })
    def libraries(self, request, libraries=None):
        if libraries:
            return paths_filtered_by_status(request, libraries)


    @calculated_property(schema={
        "title": "Donor Count",
        "description": "The number of unique Donors that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def donor_count(self, request, libraries=None):
        if libraries:
            libraries = paths_filtered_by_status(request, libraries)
            donors = []
            for l in libraries:
                donors.extend(request.embed(l, '@@object').get('donors'))
            return(len(set(donors)))


    @calculated_property(schema={
        "title": "Library Count",
        "description": "The number of Libraries that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def library_count(self, request, libraries=None):
        if libraries:
            return len(paths_filtered_by_status(request, libraries))


    @calculated_property(schema={
        "title": "Read Count",
        "description": "The number of reads from the Libraries that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def read_count(self, request, libraries=None):
        if libraries:
            libraries = paths_filtered_by_status(request, libraries)
            reads = 0
            for l in libraries:
                reads += request.embed(l, '@@object').get('read_count',0)
            return reads


    @calculated_property(schema={
        "title": "Observation Count",
        "description": "The number of observations from the Libraries that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def observation_count(self, request, libraries=None):
        if libraries:
            libraries = paths_filtered_by_status(request, libraries)
            obs = 0
            for l in libraries:
                obs += request.embed(l, '@@object').get('observation_count',0)
            return obs


    @calculated_property(schema={
        "title": "Original files",
        "description": "The DataFiles that belong to this Dataset, regardless of status.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DataFile.dataset",
        },
        "notSubmittable": True,
    })
    def original_files(self, request, original_files=None):
        if original_files:
            return paths_filtered_by_status(request, original_files)


    @calculated_property(define=True, schema={
        "title": "CELLxGENE URLs",
        "description": "Links to the representation of this dataset in CZ CELLxGENE Discover.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cellxgene_urls(self, request, urls=None):
        if urls:
            return gather_urls(urls, 'https://cellxgene.cziscience.com/collections/')


    @calculated_property(define=True, schema={
        "title": "HCA Data Portal URLs",
        "description": "Links to the representation of this dataset in the HCA Data Portal.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def hca_portal_urls(self, request, urls=None):
        if urls:
            return gather_urls(urls, 'https://explore.data.humancellatlas.org/projects/')

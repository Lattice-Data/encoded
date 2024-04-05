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


def calculate_reference(request, files_list, ref_field):
    results = set()
    viewable_file_status = ['released','in progress']

    for path in files_list:
        properties = request.embed(path, '@@object?skip_calculated=true')
        if properties['status'] in viewable_file_status:
            if ref_field in properties:
                results.add(properties[ref_field])
    return list(results)


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


    @calculated_property(schema={
        "title": "Contributing files",
        "description": "The DataFiles that contribute to this Dataset's data products but do not belong to this Dataset, typically reference files.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def contributing_files(self, request, status, original_files=None):
        if original_files:
            derived_from = set()
            for f in original_files:
                f_obj = request.embed(f, '@@object?skip_calculated=true')
                f_df = f_obj.get('derived_from')
                if isinstance(f_df, str):
                    derived_from.add(f_df)
                else:
                    derived_from.update(f_df)

            outside_ids = list(derived_from.difference(original_files))
            outside_files = []
            for i in outside_ids:
                outsideObject = request.embed(i, '@@object')
                if 'File' in outsideObject.get('@type'):
                    outside_files.append(i)

            if status in ('released'):
                contributing = paths_filtered_by_status(
                    request, outside_files,
                    include=('released',),
                )
            else:
                contributing = paths_filtered_by_status(
                    request, outside_files,
                    exclude=('revoked', 'deleted', 'replaced'),
                )
            if contributing:
                return contributing


    @calculated_property(schema={
        "title": "Revoked files",
        "description": "The DataFiles that are revoked and belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def revoked_files(self, request, original_files=None):
        if original_files:
            revoked = [
                path for path in original_files
                if item_is_revoked(request, path)
            ]
            if revoked:
                return revoked


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


    @calculated_property(define=True, schema={
        "title": "Reference assembly",
        "description": "The Genome assemblies used for references in the data analysis in this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def reference_assembly(self, request, original_files=None):
        if original_files:
            return calculate_reference(request, original_files, "assembly")


    @calculated_property(define=True, schema={
        "title": "Reference annotation",
        "description": "The genome annotations used for references in the data analysis in this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def reference_annotation(self, request, original_files=None):
        if original_files:
            return calculate_reference(request, original_files, "genome_annotation")

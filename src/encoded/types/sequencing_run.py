from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


@collection(
    name='sequencing-runs',
    properties={
        'title': 'Sequencing Runs',
        'description': 'Listing Sequuencing runs',
    })
class SequencingRun(Item):
    item_type = 'sequencing_run'
    schema = load_schema('encoded:schemas/sequencing_run.json')
    rev = {
        'files': ('RawSequenceFile', 'derived_from')
    }


    @calculated_property(schema={
        "title": "Files",
        "description": "The DataFiles belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "RawSequenceFile",
        },
    })
    def files(self, request, files=None):
        if files:
            return paths_filtered_by_status(request, files)


    @calculated_property(schema={
        "title": "Dataset",
        "description": "The dataset the sequencing run belongs to.",
        "comment": "Do not submit. This is a calculated property.",
        "type": "string",
        "linkTo": "Dataset"
    })
    def dataset(self, request, derived_from):
        library_obj = request.embed(derived_from[0], '@@object?skip_calculated=true')
        return library_obj.get('dataset')


    @calculated_property(schema={
        "title": "Lab",
        "description": "The lab the sequencing run belongs to.",
        "comment": "Do not submit. This is a calculated property.",
        "type": "string",
        "linkTo": "Lab"
    })
    def lab(self, request, derived_from):
        library_obj = request.embed(derived_from[0], '@@object?skip_calculated=true')
        return library_obj.get('lab')


    @calculated_property(schema={
        "title": "Read count",
        "description": "The number of reads belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "integer",
        "notSubmittable": True,
    })
    def read_count(self, request, registry, files):
        count = set()
        for file_id in files:
            file_obj = request.embed(file_id, '@@object?skip_calculated=true')
            read_count = file_obj.get('read_count')
            count.add(read_count)
        if len(count) == 1:
            return count.pop()


    @calculated_property(schema={
        "title": "Platform",
        "description": "The device(s) used to sequence data.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "notSubmittable": True,
        "items": {
            "type": "string"
        }
    })
    def platform(self, request, registry, files):
        plats = set()
        for file_id in files:
            file_obj = request.embed(file_id, '@@object?skip_calculated=true')
            p = file_obj.get('platform', [])
            plats.update(p)
        return list(plats)


    @calculated_property(schema={
        "title": "Read 1 file",
        "description": "The Read 1 DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def read_1_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'Read 1':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']


    @calculated_property(schema={
        "title": "Read 2 file",
        "description": "The Read 2 DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def read_2_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'Read 2':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']


    @calculated_property(schema={
        "title": "Read 1N file",
        "description": "The Read 1N DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def read_1N_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'Read 1N':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']


    @calculated_property(schema={
        "title": "Read 2N file",
        "description": "The Read 2N DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def read_2N_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'Read 2N':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']


    @calculated_property(schema={
        "title": "i5 index file",
        "description": "The i5 index DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def i5_index_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'i5 index':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']


    @calculated_property(schema={
        "title": "i7 index file",
        "description": "The i7 index DataFile belonging to this sequencing run.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "linkFrom": "RawSequenceFile.derived_from",
        "notSubmittable": True,
    })
    def i7_index_file(self, request, registry, files=None):
        if files:
            for file_id in files:
                file_obj = request.embed(file_id, '@@object?skip_calculated=true')
                read_type = file_obj.get('read_type')
                if read_type == 'i7 index':
                    if 'accession' in file_obj:
                        return file_obj['accession']
                    else:
                        return file_obj['external_accession']

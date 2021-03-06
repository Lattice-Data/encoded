from snovault import (
    abstract_collection,
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from pyramid.httpexceptions import (
    HTTPTemporaryRedirect,
    HTTPNotFound,
)
from pyramid.settings import asbool
from pyramid.view import view_config
from urllib.parse import (
    parse_qs,
    urlparse,
)
from .shared_calculated_properties import (
    CalculatedAward,
)
import boto3
import datetime
import pytz


def inherit_protocol_prop(request, seqrun_id, propname, read_type):
    seqrun_obj = request.embed(seqrun_id, '@@object?skip_calculated=true')
    lib_id = seqrun_obj.get('derived_from')[0]
    lib_obj = request.embed(lib_id, '@@object?skip_calculated=true')
    libprot_id = lib_obj.get('protocol')
    libprot_obj = request.embed(libprot_id, '@@object?skip_calculated=true')
    if 'sequence_file_standards' in libprot_obj:
        standards = libprot_obj.get('sequence_file_standards')
        for s in standards:
            if s.get('read_type') == read_type:
                return s.get(propname)


RAW_OUTPUT_TYPES = ['reads', 'rejected reads', 'raw data', 'reporter code counts', 'intensity values', 'idat red channel', 'idat green channel']


def file_is_md5sum_constrained(properties):
    conditions = [
        properties.get('output_type') in RAW_OUTPUT_TYPES
    ]
    return any(conditions)


@abstract_collection(
    name='files',
    unique_key='title',
    properties={
        'title': 'Files',
        'description': 'Listing of all types of file.',
    })
class File(Item):
    base_types = ['File'] + Item.base_types
    embedded = []
    audit_inherit = []

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        if 'external_accession' in properties:
            return properties['external_accession']
        if properties.get('status') == 'replaced':
            return self.uuid
        return properties.get(self.name_key, None) or self.uuid


    def unique_keys(self, properties):
        keys = super(File, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'md5sum' in properties:
                value = 'md5:{md5sum}'.format(**properties)
                resource = self.registry[CONNECTION].get_by_unique_key('alias', value)
                if resource and resource.uuid != self.uuid:
                    if file_is_md5sum_constrained(properties):
                        keys.setdefault('alias', []).append(value)
                else:
                    keys.setdefault('alias', []).append(value)
            if 'external_accession' in properties:
                keys.setdefault('external_accession', []).append(
                    properties['external_accession'])
        return keys

    @calculated_property(schema={
        "title": "Title",
        "description": "The title of the file either the accession or the external_accession.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def title(self, accession=None, external_accession=None):
        return accession or external_accession


    @calculated_property(schema={
        "title": "Download URL",
        "description": "The download path for S3 to obtain the actual file.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def href(self, request, file_format, accession=None, external_accession=None, s3_uri=None, external_uri=None):
        uri = s3_uri or external_uri
        if uri:
            accession = accession or external_accession
            if uri.split('.')[-1] == 'gz':
                file_extension = uri.split('.')[-2] + '.gz'
            else:
                file_extension = uri.split('.')[-1]
            filename = '{}.{}'.format(accession, file_extension)
            return request.resource_path(self, '@@download', filename)


@view_config(name='download', context=File, request_method='GET',
             permission='view', subpath_segments=[0, 1])
def download(context, request):
    properties = context.upgrade_properties()
    uri = properties.get('s3_uri') or properties.get('external_uri')
    if uri:
        if uri.split('.')[-1] == 'gz':
            file_extension = uri.split('.')[-2] + '.gz'
        else:
            file_extension = uri.split('.')[-1]
        accession_or_external = properties.get('accession') or properties['external_accession']
        filename = '{}.{}'.format(accession_or_external, file_extension)
        if request.subpath:
            _filename, = request.subpath
            if filename != _filename:
                raise HTTPNotFound(_filename)

        if properties.get('external_uri'):
            raise HTTPTemporaryRedirect(location=properties.get('external_uri'))

        if properties.get('s3_uri'):
            conn = boto3.client('s3')

            parsed_href = urlparse(properties.get('s3_uri'), allow_fragments=False)
            bucket = parsed_href.netloc
            key    = parsed_href.path.lstrip('/')

            location = conn.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': key,
                    'ResponseContentDisposition': 'attachment; filename=' + filename
                },
                ExpiresIn=36*60*60
            )
        else:
            raise HTTPNotFound(
                detail='S3 URI not present'
            )
        if asbool(request.params.get('soft')):
            expires = int(parse_qs(urlparse(location).query)['Expires'][0])
            return {
                '@type': ['SoftRedirect'],
                'location': location,
                'expires': datetime.datetime.fromtimestamp(expires, pytz.utc).isoformat(),
            }
        raise HTTPTemporaryRedirect(location=location)


@abstract_collection(
    name='data-files',
    unique_key='accession',
    properties={
        'title': 'Data Files',
        'description': 'Listing of all types of data file.',
    })
class DataFile(File, CalculatedAward):
    item_type = 'data_file'
    base_types = ['DataFile'] + File.base_types
    name_key = 'accession'
    embedded = File.embedded + ['lab', 'award']
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']
    audit_inherit = File.audit_inherit + []


    @calculated_property(schema={
        "title": "Read length units",
        "description": "The units for read length.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "enum": [
            "nt"
        ]
    })
    def read_length_units(self, read_length=None, mapped_read_length=None):
        if read_length is not None or mapped_read_length is not None:
            return "nt"


@abstract_collection(
    name='analysis-files',
    unique_key='accession',
    properties={
        'title': "Analysis Files",
        'description': "",
    })
class AnalysisFile(DataFile):
    item_type = 'analysis_file'
    base_types = ['AnalysisFile'] + DataFile.base_types
    rev = {}
    schema = load_schema('encoded:schemas/analysis_file.json')
    embedded = DataFile.embedded + []


    @calculated_property(define=True,
                         schema={"title": "Libraries",
                                 "description": "The libraries the file was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string",
                                    "linkTo": "Library"
                                    }
                                })
    def libraries(self, request, derived_from):
        all_libs = set()
        for f in derived_from:
            obj = request.embed(f, '@@object')
            if obj.get('libraries'):
                all_libs.update(obj.get('libraries'))
            elif 'Library' in obj.get('@type'):
                all_libs.add(obj.get('@id'))
        return sorted(all_libs)


@collection(
    name='sequence-alignment-files',
    unique_key='accession',
    properties={
        'title': "Sequence Alignment Files",
        'description': "",
    })
class SequenceAlignmentFile(AnalysisFile):
    item_type = 'sequence_alignment_file'
    schema = load_schema('encoded:schemas/sequence_alignment_file.json')
    embedded = AnalysisFile.embedded + []


@collection(
    name='raw-sequence-files',
    unique_key='accession',
    properties={
        'title': "Raw Sequence Files",
        'description': "",
    })
class RawSequenceFile(DataFile):
    item_type = 'raw_sequence_file'
    schema = load_schema('encoded:schemas/raw_sequence_file.json')
    rev = {
        'raw_matrix_files': ('RawMatrixFile', 'derived_from')
    }
    embedded = DataFile.embedded + ['derived_from']
    audit_inherit = DataFile.audit_inherit + ['derived_from']


    @calculated_property(schema={
        "title": "Raw matrix files",
        "description": "The list raw matrix files that derive from this file.",
        "comment": "Do not submit.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "RawMatrixFile.derived_from",
        },
        "notSubmittable": True,
    })
    def raw_matrix_files(self, request, raw_matrix_files=None):
        if raw_matrix_files:
            return paths_filtered_by_status(request, raw_matrix_files)


    @calculated_property(define=True,
                         schema={"title": "Libraries",
                                 "description": "The library the file was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                     "type": "string",
                                     "linkTo": "Library"
                                 }
                                })
    def libraries(self, request, derived_from):
        seqrun_id = derived_from[0]
        seqrun_obj = request.embed(seqrun_id, '@@object?skip_calculated=true')
        lib_id = seqrun_obj.get('derived_from')[0]
        return [lib_id]


    @calculated_property(define=True,
                         schema={"title": "Sequence elements",
                                 "description": "The biological content of the sequence reads.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                 }
                                })
    def sequence_elements(self, request, derived_from, read_type=None):
        if read_type:
            return inherit_protocol_prop(request, derived_from[0], 'sequence_elements', read_type)


    @calculated_property(define=True,
                         schema={"title": "Demultiplexed type",
                                 "description": "The read assignment after sample demultiplexing for fastq files.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "string"
                                })
    def demultiplexed_type(self, request, derived_from, read_type=None):
        if read_type:
            return inherit_protocol_prop(request, derived_from[0], 'demultiplexed_type', read_type)


@collection(
    name='raw-matrix-files',
    unique_key='accession',
    properties={
        'title': "Raw Matrix Files",
        'description': "",
    })
class RawMatrixFile(AnalysisFile):
    item_type = 'raw_matrix_file'
    schema = load_schema('encoded:schemas/raw_matrix_file.json')
    embedded = AnalysisFile.embedded + []
    rev = {
        'quality_metrics': ('Metrics', 'quality_metric_of')
    }


    @calculated_property(schema={
        "title": "Quality metrics",
        "description": "The list of QC metric objects associated with this file.",
        "comment": "Do not submit. Values in the list are reverse links of a quality metric with this file in quality_metric_of field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Metrics.quality_metric_of",
        },
        "notSubmittable": True,
    })
    def quality_metrics(self, request, quality_metrics=None):
        if quality_metrics:
            return paths_filtered_by_status(request, quality_metrics)


    @calculated_property(schema={
        "title": "Assays",
        "description": "The list of assays used to generate data contained in this matrix.",
        "comment": "Do not submit. Values in the list are inherited from linked Library objects.",
        "type": "array",
        "items": {
            "type": 'string'
        },
        "notSubmittable": True,
    })
    def assays(self, request, libraries=None):
        assays = set()
        for l in libraries:
            l_obj = request.embed(l, '@@object')
            assays.add(l_obj['assay'])
        return assays


    @calculated_property(schema={
        "title": "Value scale",
        "description": "The factor by which the expression values have been scaled; linear if not scaled.",
        "comment": "Do not submit. Value is filled in by the system as it is expected to be consistent for all instances of this class.",
        "type": "string"
        })
    def value_scale(self):
        return "linear"


    @calculated_property(schema={
        "title": "Normalized",
        "description": "A flag to indicate whether the expression values have been normalized.",
        "comment": "Do not submit. Value is filled in by the system as it is expected to be consistent for all instances of this class.",
        "type": "boolean"
        })
    def normalized(self):
        return False


    @calculated_property(schema={
        "title": "Scaled",
        "description": "A flag to indicate whether the expression values have been scaled.",
        "comment": "Do not submit. Value is filled in by the system as it is expected to be consistent for all instances of this class.",
        "type": "boolean"
        })
    def scaled(self):
        return False


@collection(
    name='processed-matrix-files',
    unique_key='accession',
    properties={
        'title': "Processed Matrix Files",
        'description': "",
    })
class ProcessedMatrixFile(AnalysisFile):
    item_type = 'processed_matrix_file'
    schema = load_schema('encoded:schemas/processed_matrix_file.json')
    embedded = AnalysisFile.embedded + ['cell_annotations', 'cell_annotations.cell_ontology', 'experimental_variable_disease']
    rev = {
        'cell_annotations': ('CellAnnotation', 'matrix_files'),
        'quality_metrics': ('Metrics', 'quality_metric_of')
    }


    @calculated_property(schema={
        "title": "Quality metrics",
        "description": "The list of QC metric objects associated with this file.",
        "comment": "Do not submit. Values in the list are reverse links of a quality metric with this file in quality_metric_of field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Metrics.quality_metric_of",
        },
        "notSubmittable": True,
    })
    def quality_metrics(self, request, quality_metrics=None):
        if quality_metrics:
            return paths_filtered_by_status(request, quality_metrics)


    @calculated_property(schema={
        "title": "Assays",
        "description": "The list of assays used to generate data contained in this matrix.",
        "comment": "Do not submit. Values in the list are inherited from linked Library objects.",
        "type": "array",
        "items": {
            "type": 'string'
        },
        "notSubmittable": True,
    })
    def assays(self, request, libraries=None):
        assays = set()
        for l in libraries:
            l_obj = request.embed(l, '@@object')
            assays.add(l_obj['assay'])
        return assays


    @calculated_property(schema={
        "title": "Cell annotations",
        "description": "The cell annotations applied to this matrix.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "CellAnnotation.matrix_files",
        },
        "notSubmittable": True,
    })
    def cell_annotations(self, request, cell_annotations=None):
        if cell_annotations:
            return paths_filtered_by_status(request, cell_annotations)

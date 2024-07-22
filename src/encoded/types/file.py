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
from .shared_calculated_properties import (
    CalculatedAward,
)


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
    rev = {}


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
    rev = DataFile.rev.copy()


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
    rev = DataFile.rev.copy()
    rev.update({
        'raw_matrix_files': ('RawMatrixFile', 'derived_from')
    })
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
    rev = DataFile.rev.copy()
    rev.update({
        'quality_metrics': ('Metrics', 'quality_metric_of')
    })


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
        return list(assays)


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
    embedded = AnalysisFile.embedded + [
        'antibody_mappings',
        'antibody_mappings.antibody',
        'antibody_mappings.antibody.targets',
        'antibody_mappings.antibody.targets.organism',
        'cell_annotations',
        'cell_annotations.cell_ontology',
        'experimental_variable_disease'
        ]
    rev = DataFile.rev.copy()
    rev.update({
        'cell_annotations': ('CellAnnotation', 'matrix_files')
    })
    audit_inherit = DataFile.audit_inherit + [
        'cell_annotations',
        'cell_annotations.cell_ontology'
        ]


    @calculated_property(schema={
        "title": "Original S3 URI",
        "description": ".",
        "comment": "Do not submit. Values are calculated based on s3_uri.",
        "type": "string",
        "notSubmittable": True,
    })
    def s3_uri_original(self, request, s3_uri=None):
        if s3_uri:
            if s3_uri.endswith('_curated.h5ad'):
                ext = s3_uri.split('_')[-2]
                return s3_uri.replace(f'_{ext}_curated.h5ad', f'.{ext}')


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
    def assays(self, request, libraries=None, feature_keys=None, gene_activity_genome_annotation=None):
        assays = set()
        for l in libraries:
            l_obj = request.embed(l, '@@object')
            assays.add(l_obj['assay'])
        if ('Ensembl gene ID' not in feature_keys and 'gene symbol' not in feature_keys) or gene_activity_genome_annotation is not None:
            for a in ['scRNA-seq','snRNA-seq']:
                if a in assays:
                    assays.remove(a)
        if feature_keys != ['genomic coordinates'] and gene_activity_genome_annotation is None:
            for a in ['snATAC-seq','scMethyl-seq','snMethyl-seq']:
                if a in assays:
                    assays.remove(a)
        if 'antibody target' not in feature_keys:
            if 'CITE-seq' in assays:
                assays.remove('CITE-seq')
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


    @calculated_property(schema={
        "title": "Genome annotations",
        "description": "The genome annotations used as references during the generation of the data in this file.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": 'string'
        },
        "notSubmittable": True,
    })
    def genome_annotations(self, request, derived_from, gene_activity_genome_annotation=None):
        if not gene_activity_genome_annotation:
            refs = set()
            for f in derived_from:
                obj = request.embed(f, '@@object')
                if obj.get('genome_annotation'):
                    refs.add(obj.get('genome_annotation'))
                elif obj.get('genome_annotations'):
                    refs.update(obj.get('genome_annotations'))
            return sorted(refs)


    @calculated_property(schema={
        "title": "Assemblies",
        "description": "The genome assemblies used as references during the generation of the data in this file.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": 'string'
        },
        "notSubmittable": True,
    })
    def assemblies(self, request, derived_from):
        refs = set()
        for f in derived_from:
            obj = request.embed(f, '@@object')
            if obj.get('assembly'):
                refs.add(obj.get('assembly'))
            elif obj.get('assemblies'):
                refs.update(obj.get('assemblies'))
        return sorted(refs)

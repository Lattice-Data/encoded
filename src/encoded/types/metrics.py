from snovault import (
    collection,
    abstract_collection,
    load_schema,
)
from .base import (
    Item
)


@abstract_collection(
    name='metrics',
    properties={
        'title': 'Metrics',
        'description': 'Listing of all types of metrics.',
    })
class Metrics(Item):
    base_types = ['Metrics'] + Item.base_types
    embedded = []


@collection(
    name='antibody-capture-metrics',
    properties={
        'title': "Antibody Capture Metrics",
        'description': "",
    })
class AntibodyCaptureMetrics(Metrics):
    item_type = 'antibody_capture_metrics'
    schema = load_schema('encoded:schemas/antibody_capture_metrics.json')
    embedded = Metrics.embedded + []


@collection(
    name='rna-metrics',
    properties={
        'title': "RNA Metrics",
        'description': "",
    })
class RnaMetrics(Metrics):
    item_type = 'rna_metrics'
    schema = load_schema('encoded:schemas/rna_metrics.json')
    embedded = Metrics.embedded + []

@collection(
    name='atac-metrics',
    properties={
        'title': "ATAC Metrics",
        'description': "",
    })
class AtacMetrics(Metrics):
    item_type = 'atac_metrics'
    schema = load_schema('encoded:schemas/atac_metrics.json')
    embedded = Metrics.embedded + []

@collection(
    name='mulitome-metrics',
    properties={
        'title': "Multiome Metrics",
        'description': "",
    })
class MultiomeMetrics(Metrics):
    item_type = 'multiome_metrics'
    schema = load_schema('encoded:schemas/multiome_metrics.json')
    embedded = Metrics.embedded + []

@collection(
    name='spatial-metrics',
    properties={
        'title': "Spatial Metrics",
        'description': "",
    })
class SpatialMetrics(Metrics):
    item_type = 'spatial_metrics'
    schema = load_schema('encoded:schemas/spatial_metrics.json')
    embedded = Metrics.embedded + []

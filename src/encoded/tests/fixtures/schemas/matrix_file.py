import pytest


@pytest.fixture
def matrix_file_base(testapp, dataset_base, raw_sequence_file_base):
    item = {
        'dataset': dataset_base['@id'],
        'file_format': 'hdf5',
        'derivation_process': ['quantification'],
        'output_types': ['gene quantifications'],
        'derived_from': [raw_sequence_file_base['uuid'], reference_file_base['uuid']],
        'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
    }
    return testapp.post_json('/matrix_file', item).json['@graph'][0]
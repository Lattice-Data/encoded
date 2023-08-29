import pytest


@pytest.fixture
def processed_matrix_file_base(testapp, dataset_base, raw_matrix_file_base):
    item = {
        'dataset': dataset_base['@id'],
        'file_format': 'hdf5',
        'derivation_process': ['single cell analysis pipeline'],
        'output_types': ['gene quantifications'],
        'derived_from': [raw_matrix_file_base['uuid']],
        'is_primary_data': 'True',
        'X_normalized': False,
        'feature_keys': ['gene symbol'],
        'description': 'some final mx'
    }
    return testapp.post_json('/processed_matrix_file', item).json['@graph'][0]

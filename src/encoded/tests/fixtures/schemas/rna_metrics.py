import pytest


@pytest.fixture
def rna_metrics_base(testapp, raw_matrix_file_base):
    item = {
        'quality_metric_of': raw_matrix_file_base['uuid']
    }
    return testapp.post_json('/rna_metrics', item, status=201).json['@graph'][0]

import pytest


@pytest.fixture
def antibody_base(testapp, mouse):
    item = {
        'product_id': 'SAB2100398',
        'source': 'Acme',
        'host_organism': mouse['uuid']
    }
    return testapp.post_json('/antibody', item).json['@graph'][0]

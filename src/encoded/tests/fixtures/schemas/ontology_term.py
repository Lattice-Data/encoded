import pytest


@pytest.fixture
def heart_ontology(testapp):
    item = {
        'term_id': 'UBERON:0003498',
        'term_name': 'heart blood vessel'
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]

@pytest.fixture
def european_ontology(testapp):
    item = {
        'term_id': 'MONDO:17998',
        'term_name': 'European'
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]

@pytest.fixture
def adult_ontology(testapp):
    item = {
        'term_id': 'HsapDv:0000087',
        'term_name': 'human adult stage'
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]

@pytest.fixture
def asian_ontology(testapp):
    item = {
        'term_id': 'HANCESTRO:0008',
        'term_name': 'Asian'
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]

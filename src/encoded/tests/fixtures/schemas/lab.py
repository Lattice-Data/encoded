import pytest


@pytest.fixture
def lab_base(testapp):
    item = {
        'title': 'Other lab',
        'name': 'other-lab',
        'uuid': '32072c56-83af-4693-8545-0117fb9fa159'
    }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]

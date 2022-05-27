import pytest


def test_library_protocol_upgrade_1_2(upgrader, library_protocol_base):
	library_protocol_base['construction_platform'] = '10x'
	library_protocol_base['library_preparation_environment'] = 'plate'
	library_protocol_base['size_range'] = '500-3000'
	value = upgrader.upgrade('library_protocol', library_protocol_base, current_version='1', target_version='2')
	assert 'construction_platform' not in value
	assert 'library_preparation_environment' not in value
	assert 'size_range' not in value
	assert value['schema_version'] == '2'

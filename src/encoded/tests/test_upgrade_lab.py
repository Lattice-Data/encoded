import pytest


def test_user_upgrade_1_2(upgrader, lab_base):
	lab_base['address1'] = '555 5th Ave'
	lab_base['institute_label'] = 'SU'
	lab_base['url'] = 'https://www.lattice-data.org/'
	value = upgrader.upgrade('lab', lab_base, current_version='1', target_version='2')
	assert 'address1' not in value
	assert 'institute_label' not in value
	assert 'url' not in value
	assert value['schema_version'] == '2'

import pytest


def test_human_postnatal_donor_upgrade_1_2(upgrader, human_postnatal_donor_base):
	human_postnatal_donor_base['family_history_breast_cancer'] = ['sister', 'mother']
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='1', target_version='2')
	assert value['family_members_history_breast_cancer'] == ['sister', 'mother']
	assert 'family_history_breast_cancer' not in value
	assert value['schema_version'] == '2'


def test_human_postnatal_donor_upgrade_2_3(upgrader, human_postnatal_donor_base):
	human_postnatal_donor_base['height'] = 55
	human_postnatal_donor_base['body_mass_index'] = 22
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='2', target_version='3')
	assert value['height'] == '55'
	assert value['body_mass_index'] == '22'
	assert value['schema_version'] == '3'


def test_human_donor_upgrade_3_4(upgrader, human_postnatal_donor_base, asian_ontology):
	human_postnatal_donor_base['ancestry'] = [{'ancestry_group': asian_ontology, 'percentage': 75}]
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='3', target_version='4')
	assert value['schema_version'] == '4'
	assert value['ancestry'][0]['fraction'] == 0.75
	assert 'percentage' not in value['ancestry'][0]

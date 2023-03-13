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
	human_postnatal_donor_base['aliases'] = ['lattice:W09_donor','lattice:something_else']
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='3', target_version='4')
	assert value['schema_version'] == '4'
	assert value['ancestry'][0]['fraction'] == 0.75
	assert 'percentage' not in value['ancestry'][0]
	assert value['donor_id'] == 'W09'


def test_human_donor_upgrade_4_5(upgrader, human_postnatal_donor_base, asian_ontology):
	human_postnatal_donor_base['ethnicity'] = asian_ontology
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='4', target_version='5')
	assert value['schema_version'] == '5'
	assert value['ethnicity'] == [asian_ontology]


def test_human_donor_upgrade_5_6(upgrader, human_postnatal_donor_base):
	human_postnatal_donor_base['smoking_history'] = 'none'
	human_postnatal_donor_base['family_members_history_breast_cancer'] = ['sister', 'mother']
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='5', target_version='6')
	assert value['schema_version'] == '6'
	assert value['smoker'] == 'never'
	assert 'family_members_history_breast_cancer' not in value
	assert 'family_history_breast_cancer' not in value
	assert value['family_medical_history']['family_members'] == ['sister', 'mother']
	assert value['family_medical_history']['present'] == True
	assert value['family_medical_history']['diagnosis'] == 'ontology-terms/MONDO_0007254'

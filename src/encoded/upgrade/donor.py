from snovault import upgrade_step


@upgrade_step('human_postnatal_donor', '1', '2')
def human_postnatal_donor_1_2(value, system):
	if 'family_history_breast_cancer' in value:
		value['family_members_history_breast_cancer'] = value['family_history_breast_cancer']
		del value['family_history_breast_cancer']


@upgrade_step('human_postnatal_donor', '2', '3')
def human_postnatal_donor_2_3(value, system):
	if 'height' in value:
		value['height'] = str(value['height'])
	if 'body_mass_index' in value:
		value['body_mass_index'] = str(value['body_mass_index'])


@upgrade_step('human_postnatal_donor', '3', '4')
@upgrade_step('human_prenatal_donor', '1', '2')
def human_donor_ancestry(value, system):
	if 'ancestry' in value:
		for a in value['ancestry']:
			a['fraction'] = a['percentage'] / 100
			del a['percentage']
	donor_id = value['aliases'][0].split(':')[1]
	if donor_id.endswith('_donor'):
		donor_id = donor_id[:-6]
	value['donor_id'] = donor_id


@upgrade_step('human_postnatal_donor', '4', '5')
@upgrade_step('human_prenatal_donor', '2', '3')
def human_donor_ethnicity_array(value, system):
	if 'ethnicity' in value:
		value['ethnicity'] = [value['ethnicity']]


@upgrade_step('human_postnatal_donor', '5', '6')
def human_donor_smoker_family_history(value, system):
	if 'smoking_history' in value:
		if value['smoking_history'] == 'none':
			value['smoker'] = 'never'
	if 'family_members_history_breast_cancer' in value:
		if value['family_members_history_breast_cancer'] == ["none"]:
			value['family_medical_history'] = [{
				'present': False
			}]
		else:
			value['family_medical_history'] = [{
				'family_members': value['family_members_history_breast_cancer'],
				'present': True
			}]
		del value['family_members_history_breast_cancer']


@upgrade_step('human_postnatal_donor', '6', '7')
def human_donor_cause_of_death_removal(value, system):
	if 'cause_of_death' in value:
		del value['cause_of_death']

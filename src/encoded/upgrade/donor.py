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

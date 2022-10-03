from snovault import upgrade_step


@upgrade_step('suspension', '1', '2')
def suspension_1_2(value, system):
	if 'biosample_ontology' in value:
		del value['biosample_ontology']


@upgrade_step('suspension', '2', '3')
def suspension_2_3(value, system):
	if 'url' in value:
		value['urls'] = [value['url']]
		del value['url']


@upgrade_step('suspension', '3', '4')
def suspension_3_4(value, system):
	if 'dissociation_time' in value:
		value['dissociation_time'] = str(value['dissociation_time'])


@upgrade_step('suspension', '4', '5')
def suspension_4_5(value, system):
	if 'red_blood_cell_lysis' in value:
		value['red_blood_cell_removal'] = value['red_blood_cell_lysis']
		del value['red_blood_cell_lysis']

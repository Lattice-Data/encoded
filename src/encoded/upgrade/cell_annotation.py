from snovault import upgrade_step


@upgrade_step('cell_annotation', '1', '2')
def cell_annotation_1_2(value, system):
	if value['cell_ontology'] == '380b4b81-2036-4ee3-abe3-9db774e6185f':
		value['cell_ontology'] = '9ccb9d0b-1747-4ad1-969a-769286937021'

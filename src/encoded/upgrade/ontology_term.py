from snovault import upgrade_step


@upgrade_step('ontology_term', '1', '2')
def ontology_term_1_2(value, system):
	if 'human' in value['term_name']:
		value['term_name'] = value['term_name'].replace('human ','')

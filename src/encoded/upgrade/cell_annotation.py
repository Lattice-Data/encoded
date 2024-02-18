from snovault import upgrade_step


@upgrade_step('cell_annotation', '1', '2')
def cell_annotation_1_2(value, system):
	if value['cell_ontology']['term_id'] == 'CL:0000003':
		value['cell_ontology'] = '/ontology-terms/NCIT_C17998/'

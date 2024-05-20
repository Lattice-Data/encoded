from snovault import upgrade_step


@upgrade_step('sequencing_run', '1', '2')
def sequencing_run_1_2(value, system):
	if 'derived_from' in value:
		value['derived_from'] = [value['derived_from']]


@upgrade_step('sequencing_run', '2', '3')
def sequencing_run_2_3(value, system):
	if 'flowcell_details' in value:
		del value['flowcell_details']

@upgrade_step('sequencing_run', '3', '4')
def sequencing_run_3_4(value, system):
	if 'supersedes' in value:
		del value['supersedes']

@upgrade_step('sequencing_run', '4', '5')
def sequencing_run_4_5(value, system):
	if 'platform' in value:
		value['platform'] = [value['platform']]

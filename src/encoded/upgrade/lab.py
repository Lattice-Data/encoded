from snovault import upgrade_step


@upgrade_step('lab', '1', '2')
def lab_1_2(value, system):
	remove = ['address1', 'address2', 'city', 'country', 'institute_label',
		'institute_name', 'phone', 'postal_code', 'state', 'url',
		'principal_investigators']
	for p in remove:
		if p in value:
			del value[p]

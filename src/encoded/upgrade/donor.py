from snovault import upgrade_step


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


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


@upgrade_step('human_postnatal_donor', '7', '8')
def human_donor_living_at_sample_collection_stringify(value, system):
	if 'living_at_sample_collection' in value:
		value['living_at_sample_collection'] = str(value['living_at_sample_collection'])


@upgrade_step('human_postnatal_donor', '8', '9')
@upgrade_step('human_prenatal_donor', '3', '4')
def human_donor_set_organism(value, system):
	value['organism'] = 'd4499d6e-bf11-41be-84e3-9e42919721a1'

age_dv = {
	'<30 years': '6b94bf2b-e009-4864-8ff8-6bc168b5de4c', #HsapDv:0010000/postnatal stage
	'>13 years': '6b94bf2b-e009-4864-8ff8-6bc168b5de4c', #HsapDv:0010000/postnatal stage
	'>18 years': 'e7399eed-71f6-4336-8bc0-30c25fdd9ed6', #HsapDv:0000258/adult stage
	'>19 years': 'e7399eed-71f6-4336-8bc0-30c25fdd9ed6', #HsapDv:0000258/adult stage
	'>50 years': 'e7399eed-71f6-4336-8bc0-30c25fdd9ed6', #HsapDv:0000258/adult stage
	'>60 years': '2bfb340f-b7d9-44b9-98ca-827cede51d49', #HsapDv:0000227/late adult stage
	'15-30 years': '1ef63c6e-5c3d-4553-8574-8993ab74a8a9', #HsapDv:0000266/young adult stage
	'13-18 years': '6b94bf2b-e009-4864-8ff8-6bc168b5de4c', #HsapDv:0010000/postnatal stage
	'18-34 years': '1ef63c6e-5c3d-4553-8574-8993ab74a8a9', #HsapDv:0000266/young adult stage
	'18-49 years': 'a8e80fd2-5683-4a25-a8d1-3883d498c99c', #HsapDv:0000226/prime adult stage
	'19-24 years': '1ef63c6e-5c3d-4553-8574-8993ab74a8a9', #HsapDv:0000266/young adult stage
	'2-12 years': '26baa152-415b-4f45-a232-8f2a390aa4e3', #HsapDv:0000264/pediatric stage
	'30-60 years': 'a8e80fd2-5683-4a25-a8d1-3883d498c99c', #HsapDv:0000226/prime adult stage
	'50-80 years': 'e7399eed-71f6-4336-8bc0-30c25fdd9ed6', #HsapDv:0000258/adult stage
	'0-1 days': '0bfc892e-13ef-4cf3-a1ca-6a365c8ea880', #HsapDv:0000262/newborn stage (0-28 days)
	'2 days': '0bfc892e-13ef-4cf3-a1ca-6a365c8ea880', #HsapDv:0000262/newborn stage (0-28 days)
	'6 days': '0bfc892e-13ef-4cf3-a1ca-6a365c8ea880', #HsapDv:0000262/newborn stage (0-28 days)
	'7 days': '0bfc892e-13ef-4cf3-a1ca-6a365c8ea880', #HsapDv:0000262/newborn stage (0-28 days)
	'16 days': '0bfc892e-13ef-4cf3-a1ca-6a365c8ea880', #HsapDv:0000262/newborn stage (0-28 days)
	'1 month': 'b4a843f2-4401-4d56-9225-d4f429b5100a', #HsapDv:0000273/1-month-old stage
	'1-23 months': '26baa152-415b-4f45-a232-8f2a390aa4e3', #HsapDv:0000264/pediatric stage
	'>0 years': '6b94bf2b-e009-4864-8ff8-6bc168b5de4c' #HsapDv:0010000/postnatal stage
}

@upgrade_step('human_postnatal_donor', '9', '10')
def human_donor_dv_updates(value, system):
	age = value['age']
	age_units = value.get('age_units')
	#plucked from types/donor.py age_display calculation
	#only postnatal so removed conceptional_age logic
	if age == 'unknown':
		age_display = 'unknown'
	elif age == 'variable':
		age_display = 'variable'
	elif age != None:
		age_display = u'{}'.format(pluralize(age, age_units))
	else:
		age_display = None

	value['development_ontology'] = age_dv.get(age_display, value['development_ontology'])

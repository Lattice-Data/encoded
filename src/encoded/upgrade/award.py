from snovault import upgrade_step


@upgrade_step('award', '1', '2')
def award_1_2(value, system):
	mapping = {
		'adipose' : 'adipose, skin, breast',
		'skin' : 'adipose, skin, breast',
		'breast' : 'adipose, skin, breast',
		'gastrointestinal': 'digestive and respiratory systems',
		'liver': 'digestive and respiratory systems',
		'respiratory system': 'digestive and respiratory systems',
		'bone marrow': 'immune and lymphoreticular systems',
		'immune system': 'immune and lymphoreticular systems',
		'lymph nodes': 'immune and lymphoreticular systems',
		'thymus': 'immune and lymphoreticular systems',
		'central nervous system': 'nervous system',
		'testis': 'reproductive system',
		'female reproductive system': 'reproductive system',
		'prostate': 'reproductive system',
		'multi-organ': 'organ systems',
		'muscle': 'organ systems',
		'musculoskeletal': 'organ systems',
		'tendon': 'organ systems',
		'lung': 'organ systems',
		'methods': 'technology'
		}

	value['focus'] = mapping[value['focus']]

from snovault import upgrade_step


@upgrade_step('dataset', '1', '2')
def dataset_1_2(value, system):
	if 'corresponding_contributor' in value:
		value['corresponding_contributors'] = [value['corresponding_contributor']]
		del value['corresponding_contributor']


#never updated default version to 2
@upgrade_step('dataset', '1', '3')
def dataset_1_3(value, system):
	if 'urls' in value:
		new_urls = []
		for url in value['urls']:
			if url.startswith('https://data.humancellatlas.org/explore/projects/'):
				url = url.replace('data.humancellatlas.org/explore','explore.data.humancellatlas.org')
			new_urls.append(url)
		value['urls'] = new_urls

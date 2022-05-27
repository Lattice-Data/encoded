from snovault import upgrade_step


@upgrade_step('library_protocol', '1', '2')
def library_protocol_1_2(value, system):
	remove = ['construction_platform', 'construction_platform_version', 'depleted_in_term_name',
		'depleted_in_term_id', 'documents', 'extraction_method', 'fragmentation_method',
		'library_preparation_environment', 'library_size_selection_method', 'lysis_method',
		'polyA_selection', 'polyA_selection_method', 'second_strand_primer',
		'size_range', 'spatial_resolution', 'spatial_resolution_units', 'url']
	for p in remove:
		if p in value:
			del value[p]

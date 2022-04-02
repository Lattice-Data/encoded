from snovault import upgrade_step


rna_1_2_map = {
	'number_of_reads' : 'total_reads',
	'estimated_number_of_cells' : 'total_cells_detected'
}

rna_1_2_per_frac_map = {
	'percent_valid_barcodes' : 'frac_valid_barcodes',
	'percent_sequencing_saturation' : 'frac_sequencing_saturation',
	'percent_q30_bases_in_barcode' : 'frac_q30_bases_in_barcode',
	'percent_q30_bases_in_sample_index' : 'frac_q30_bases_in_sample_index',
	'percent_q30_bases_in_umi' : 'frac_q30_bases_in_umi',
	'percent_reads_in_cells' : 'frac_reads_in_cells',
	'percent_reads_mapped_to_genome' : 'frac_reads_mapped_to_genome',
	'percent_reads_mapped_confidently_to_genome' : 'frac_reads_mapped_confidently_to_genome',
	'percent_reads_mapped_antisense_to_gene' : 'frac_reads_mapped_antisense_to_gene',
	'percent_reads_mapped_confidently_to_transcriptome' : 'frac_reads_mapped_confidently_to_transcriptome',
	'percent_reads_mapped_confidently_to_exonic_regions' : 'frac_reads_mapped_confidently_to_exonic_regions',
	'percent_reads_mapped_confidently_to_intronic_regions' : 'frac_reads_mapped_confidently_to_intronic_regions',
	'percent_reads_mapped_confidently_to_intergenic_regions' : 'frac_reads_mapped_confidently_to_intergenic_regions',
	'percent_q30_bases_in_rna_read' : 'frac_q30_bases_in_rna_read',
	'percent_q30_bases_in_rna_read_2' : 'frac_q30_bases_in_rna_read2'
}

atac_1_2_map = {
	'frac_mapped_confidently' : 'frac_reads_mapped_confidently_to_genome',
	'number_fragments' : 'total_fragments',
	'cells_detected' : 'total_cells_detected',
	'bases_in_peaks' : 'total_bases_in_peaks',
	'bulk_unique_fragments_at_30000000_reads' : 'bulk_total_unique_fragments_at_30000000_reads',
	'estimated_cells_present' : 'estimated_total_cells_present',
	'frac_of_genome_within_2000bp_of_peaks' : 'frac_genome_within_2000bp_of_peaks',
	'number_reads' : 'total_reads',
	'number_of_low_targeting_barcodes' : 'total_low_targeting_barcodes',
	'putative_barcode_multiplets_found' : 'putative_total_barcode_multiplets_found',
	'putative_gelbead_doublets_found' : 'putative_total_gelbead_doublets_found'
}


@upgrade_step('rna_metrics', '1', '2')
def rna_metrics_lot_1_2(value, system):
	for o,n in rna_1_2_map.items():
		if o in value:
			value[n] = value[o]
			del value[o]
	for o,n in rna_1_2_per_frac_map.items():
		if o in value:
			v = value[o]
			dig = len(str(v).replace('.',''))
			if v < 10:
				v = round(v/100,dig+1)
			else:
				v = round(v/100,dig)
			value[n] = v
			del value[o]


@upgrade_step('atac_metrics', '1', '2')
def atac_metrics_lot_1_2(value, system):
	for o,n in atac_1_2_map.items():
		if o in value:
			value[n] = value[o]
			del value[o]

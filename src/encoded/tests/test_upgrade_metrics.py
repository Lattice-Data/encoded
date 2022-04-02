import pytest


def test_rna_metrics_upgrade_1_2(upgrader, rna_metrics_base):
	rna_metrics_base['percent_q30_bases_in_umi'] = 94.5
	rna_metrics_base['percent_sequencing_saturation'] = 4.3
	rna_metrics_base['number_of_reads'] = 9442345
	value = upgrader.upgrade('rna_metrics', rna_metrics_base, current_version='1', target_version='2')
	assert 'percent_q30_bases_in_umi' not in value
	assert 'percent_sequencing_saturation' not in value
	assert 'number_of_reads' not in value
	assert value['frac_q30_bases_in_umi'] == 0.945
	assert value['frac_sequencing_saturation'] == 0.043
	assert value['total_reads'] == 9442345
	assert value['schema_version'] == '2'


def test_atac_metrics_upgrade_1_2(upgrader, atac_metrics_base):
	atac_metrics_base['frac_mapped_confidently'] = 0.945
	atac_metrics_base['cells_detected'] = 9442345
	atac_metrics_base['frac_of_genome_within_2000bp_of_peaks'] = 0.5
	value = upgrader.upgrade('atac_metrics', atac_metrics_base, current_version='1', target_version='2')
	assert 'percent_q30_bases_in_umi' not in value
	assert 'percent_sequencing_saturation' not in value
	assert 'number_of_reads' not in value
	assert value['frac_reads_mapped_confidently_to_genome'] == 0.945
	assert value['total_cells_detected'] == 9442345
	assert value['frac_genome_within_2000bp_of_peaks'] == 0.5
	assert value['schema_version'] == '2'

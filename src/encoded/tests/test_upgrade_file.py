import pytest


def test_file_upgrade_1_2(upgrader, raw_sequence_file_base):
	raw_sequence_file_base['award'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('raw_sequence_file', raw_sequence_file_base, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert 'award' not in value


def test_processed_matrix_file_upgrade_4_5(upgrader, processed_matrix_file_base):
	processed_matrix_file_base['layers'] = [{
		'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
        'label': 'raw'}]
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='4', target_version='5')
	assert value['schema_version'] == '5'
	assert value['layers'][0]['is_primary_data'] == True


def test_processed_matrix_file_upgrade_5_6(upgrader, processed_matrix_file_base):
	processed_matrix_file_base['layers'] = [{
		'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
        'label': 'raw'}]
	processed_matrix_file_base['layers'][0]['is_primary_data'] = 'False'
	del processed_matrix_file_base['is_primary_data']
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='5', target_version='6')
	assert value['schema_version'] == '6'
	assert value['is_primary_data'] == 'False'


def test_processed_matrix_file_upgrade_6_7(upgrader, processed_matrix_file_base):
	processed_matrix_file_base['layers'] = [{
		'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
        'label': 'raw'}]
	processed_matrix_file_base['layers'][0]['is_primary_data'] = 'True'
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='6', target_version='7')
	assert value['schema_version'] == '7'
	assert 'is_primary_data' not in value['layers'][0]


def test_raw_matrix_file_upgrade_3_4(upgrader, raw_matrix_file_base):
	raw_matrix_file_base['value_units'] = 'UMI'
	value = upgrader.upgrade('raw_matrix_file', raw_matrix_file_base, current_version='3', target_version='4')
	assert value['schema_version'] == '4'
	assert value['value_units'] == ['UMI']


def test_processed_matrix_file_upgrade_7_8(upgrader, processed_matrix_file_base):
	processed_matrix_file_base['layers'] = [{
		'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
        'label': 'raw'}]
	processed_matrix_file_base['layers'][0]['scaled'] = True
	processed_matrix_file_base['layers'][0]['filtering_cutoffs'] = 'something'
	processed_matrix_file_base['software'] = 'Seurat'
	processed_matrix_file_base['cell_annotation_method'] = 'manual'
	processed_matrix_file_base['author_cluster_column'] = 'cluster'
	processed_matrix_file_base['derivation_process'] = ['doublet removal','batch correction','depth normalization']
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='7', target_version='8')
	assert value['schema_version'] == '8'
	assert 'scaled' not in value['layers'][0]
	assert 'filtering_cutoffs' not in value['layers'][0]
	assert 'software' not in value
	assert 'cell_annotation_method' not in value
	assert 'author_cluster_column' not in value
	assert value['derivation_process'] == ['single cell analysis pipeline']


def test_processed_matrix_file_upgrade_8_9(upgrader, processed_matrix_file_base):
	processed_matrix_file_base['layers'] = [{
		'normalized': False,
        'value_scale': 'linear',
        'value_units': 'RPKM',
        'label': 'raw',
        'feature_counts': [{
            "feature_type": "gene",
            "feature_count": 20919
            }]}]
	processed_matrix_file_base['author_donor_column'] = 'my_donors'
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='8', target_version='9')
	assert value['schema_version'] == '9'
	assert processed_matrix_file_base['demultiplexed_donor_column'] == 'my_donors'
	assert value['X_normalized'] == False
	assert value['feature_counts'] == [{"feature_type": "gene","feature_count": 20919}]
	assert 'layers' not in value

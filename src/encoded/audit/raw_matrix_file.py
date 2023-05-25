from snovault import (
	AuditFailure,
	audit_checker,
)
from .formatter import (
	audit_link,
	path_to_text,
)


def audit_complete_derived_from(value, system):
	if value['status'] in ['deleted']:
		return

	included = []
	should_be_included = []
	for df in value.get('derived_from'):
		if df['@type'][0] == 'RawSequenceFile':
			included.append(df['@id'])
			should_be_included.extend(df['derived_from'][0]['files'])
	missing = [f for f in should_be_included if f not in included]

	if missing:
		detail = ('File {} does not have all RawSequenceFiles from all SequencingRuns in derived_from. Missing:{}.'.format(
			audit_link(path_to_text(value['@id']), value['@id']),
			','.join(missing)
			)
		)
		yield AuditFailure('incomplete derived_from', detail, level='ERROR')


def audit_read_count_compare(value, system):
	'''
	We check fastq metadata against the expected values based on the
	library protocol used to generate the sequence data.
	'''
	if value['status'] in ['deleted']:
		return

	if value.get('quality_metrics'):
		input_reads = {
			'ATAC': {},
			'RNA': {},
			'AC': {}
		}
		for df in value.get('derived_from'):
			if df['@type'][0] != 'RawSequenceFile' or df.get('validated') != True:
				return
			seqrun = df['derived_from'][0]['uuid']
			in_reads = 0
			assay = df['libraries'][0]['assay']
			if assay in ['snATAC-seq']:
				if seqrun not in input_reads['ATAC'].keys():
					seqrun_reads = df.get('read_count')
					input_reads['ATAC'][seqrun] = seqrun_reads
			elif assay in ['scRNA-seq','snRNA-seq','spatial transcriptomics']:
				if seqrun not in input_reads['RNA'].keys():
					seqrun_reads = df.get('read_count')
					input_reads['RNA'][seqrun] = seqrun_reads
			elif assay in ['CITE-seq']:
				if seqrun not in input_reads['AC'].keys():
					seqrun_reads = df.get('read_count')
					input_reads['AC'][seqrun] = seqrun_reads

		for qc in value.get('quality_metrics'):
			if qc['@type'][0] == 'AtacMetrics' and 'total_fragments' in qc:
				out_reads = qc['total_fragments']
				read_counts = [i for i in input_reads['ATAC'].values()]
				in_reads = sum(read_counts)
				if in_reads != out_reads and out_reads !=0:
					detail = ('File {} has {} ATAC reads but input objects total {} reads.'.format(
						audit_link(path_to_text(value['@id']), value['@id']),
						out_reads,
						in_reads
						)
					)
					yield AuditFailure('inconsistent read counts', detail, level='ERROR')
			elif qc['@type'][0] == 'RnaMetrics' and 'total_reads' in qc:
				out_reads = qc['total_reads']
				read_counts = [i for i in input_reads['RNA'].values()]
				in_reads = sum(read_counts)
				if in_reads != out_reads and out_reads !=0:
					detail = ('File {} has {} RNA reads but input objects total {} reads.'.format(
						audit_link(path_to_text(value['@id']), value['@id']),
						out_reads,
						in_reads
						)
					)
					yield AuditFailure('inconsistent read counts', detail, level='ERROR')
			elif qc['@type'][0] == 'AntibodyCaptureMetrics' and 'total_reads' in qc:
				out_reads = qc['total_reads']
				read_counts = [i for i in input_reads['AC'].values()]
				in_reads = sum(read_counts)
				if in_reads != out_reads and out_reads !=0:
					detail = ('File {} has {} AntibodyCapture reads but input objects total {} reads.'.format(
						audit_link(path_to_text(value['@id']), value['@id']),
						out_reads,
						in_reads
						)
					)
					yield AuditFailure('inconsistent read counts', detail, level='ERROR')


def audit_validated(value, system):
	'''
	We check fastq metadata against the expected values based on the
	library protocol used to generate the sequence data.
	'''
	if value['status'] in ['deleted']:
		return

	if value.get('no_file_available') != True:
		if value.get('s3_uri') or value.get('external_uri'):
			if value.get('validated') != True and value.get('file_format') in ['hdf5']:
				detail = ('File {} has not been validated.'.format(
					audit_link(path_to_text(value['@id']), value['@id'])
					)
				)
				yield AuditFailure('file not validated', detail, level='ERROR')
				return
		else:
			detail = ('File {} has no s3_uri, external_uri, and is not marked as no_file_available.'.format(
				audit_link(path_to_text(value['@id']), value['@id'])
				)
			)
			yield AuditFailure('file access not specified', detail, level='WARNING')
			return


def audit_gene_count(value, system):
	'''
	We check fastq metadata against the expected values based on the
	library protocol used to generate the sequence data.
	'''
	if value['status'] in ['deleted']:
		return

	if value.get('feature_counts'):
		for fc in value['feature_counts']:
			if fc['feature_type'] == 'gene' and fc['feature_count'] < 16000:
				detail = ('File {} has {} gene count, we require more to improve reusability.'.format(
					audit_link(path_to_text(value['@id']), value['@id']),
					fc['feature_count']
					)
				)
				yield AuditFailure('low gene count', detail, level='ERROR')
				return


def metrics_types(value, system):
	assays = value['assays']

	all_types = []
	for qc in value.get('quality_metrics',[]):
		errors = []
		qc_type = qc['@type'][0]
		all_types.append(qc_type)

		if qc_type == 'RnaMetrics':
			req_assay = 'RNA-seq'
			if 'snRNA-seq' in assays or 'scRNA-seq' in assays or 'spatial transcriptomics' in assays:
				assays.append('RNA-seq')
		elif qc_type == 'MultiomeMetrics':
			if 'snATAC-seq' not in assays and ('snRNA-seq' not in assays and 'scRNA-seq' not in assays):
				req_assay = 'RNA-seq or snATAC-seq'
			elif 'snRNA-seq' not in assays and 'scRNA-seq' not in assays:
				req_assay = 'RNA-seq'
			else:
				req_assay = 'snATAC-seq'
		elif qc_type == 'AtacMetrics':
			req_assay = 'snATAC-seq'
		elif qc_type == 'AntibodyCaptureMetrics':
			req_assay = 'CITE-seq'
		elif qc_type == 'SpatialMetrics':
			req_assay = 'spatial transcriptomics'

		if req_assay not in assays:
			detail = ('File {} has {} but is not linked to any {} Library.'.format(
				audit_link(path_to_text(value['@id']), value['@id']),
				qc_type,
				req_assay
				)
			)
			yield AuditFailure('metrics, library inconsistency', detail, level='ERROR')

	for t in set(all_types):
		if all_types.count(t) > 1:
			detail = ('File {} has multiple metrics of type {}.'.format(
				audit_link(path_to_text(value['@id']), value['@id']),
				t
				)
			)
			yield AuditFailure('redundant metrics', detail, level='ERROR')


function_dispatcher = {
	'audit_complete_derived_from': audit_complete_derived_from,
	'audit_read_count_compare': audit_read_count_compare,
	'audit_validated': audit_validated,
	'audit_gene_count': audit_gene_count,
	'metrics_types': metrics_types
}

@audit_checker('RawMatrixFile',
			   frame=[
				   'derived_from',
				   'derived_from.derived_from',
				   'derived_from.libraries',
				   'quality_metrics'
			   ])
def audit_raw_matrix_file(value, system):
	for function_name in function_dispatcher.keys():
		for failure in function_dispatcher[function_name](value, system):
			yield failure

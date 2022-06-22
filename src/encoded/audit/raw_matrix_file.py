from snovault import (
	AuditFailure,
	audit_checker,
)
from .formatter import (
	audit_link,
	path_to_text,
)


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

function_dispatcher = {
	'audit_read_count_compare': audit_read_count_compare,
	'audit_validated': audit_validated
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

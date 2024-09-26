from snovault import (
	AuditFailure,
	audit_checker,
)
from .formatter import (
	audit_link,
	path_to_text,
)


def audit_analysis_library_types(value, system):
	'''
	An AnalysisFile should only have cellranger_assay_chemistry metadata
	if it is from an RNA-seq library.
	We expect CITE-seq libraries to be paired with RNA-seq libraries.
	'''
	lib_feature = {
		'RNA-seq': 'gene',
		'CITE-seq': 'antibody capture',
		'ATAC-seq': 'peak',
		'Methyl-seq': 'peak'
	}

	if value['status'] in ['deleted']:
		return

	lib_types = set()
	for l in value.get('libraries'):
		lib_types.add(l['protocol'].get('library_type'))

	if value['validated'] == True:
		peak_audit = False
		feature_types = [f['feature_type'] for f in value['feature_counts']]
		for k,v in lib_feature.items():
			if k in lib_types and v not in feature_types:
				detail = ('File {} derives from at least one {} library but does not contain {} features'.format(
					audit_link(path_to_text(value['@id']), value['@id']),
					k,
					v,
					)
				)
				yield AuditFailure('library, feature_type inconsistency', detail, level="ERROR")
			if k not in lib_types and v in feature_types:
				if v == 'peak':
					if 'ATAC-seq' in lib_types or 'Methyl-seq' in lib_types:
						return
					else:
						if peak_audit:
							return
						else:
							k = 'ATAC-seq or Methyl-seq'
							peak_audit = True
				detail = ('File {} contains {} features but does not derive from at least one {} library'.format(
					audit_link(path_to_text(value['@id']), value['@id']),
					v,
					k,
					)
				)
				yield AuditFailure('library, feature_type inconsistency', detail, level="ERROR")

	if 'RNA-seq' not in lib_types and value.get('cellranger_assay_chemistry'):
        detail = ('File {} has {} and does not derive from any RNA-seq library'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            'cellranger_assay_chemistry',
            )
        )
        yield AuditFailure('cellranger spec inconsistent with library_type', detail, level="ERROR")


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


def audit_gene_count(value, system):
	'''
	We check fastq metadata against the expected values based on the
	library protocol used to generate the sequence data.
	'''
	if value['status'] in ['deleted']:
		return

	cellranger_ref_feature_counts = {
		32738: 'GENCODE 19',
		33694: 'GENCODE 24',
		33538: 'GENCODE 28',
		36601: 'GENCODE 32',
		38606: 'GENCODE 44'
	}

	if value.get('feature_counts'):
		for fc in value['feature_counts']:
			if fc['feature_type'] == 'gene':
				if fc['feature_count'] < 16000:
					detail = ('File {} has {} gene count, we require more to improve reusability.'.format(
						audit_link(path_to_text(value['@id']), value['@id']),
						fc['feature_count']
						)
					)
					yield AuditFailure('low gene count', detail, level='ERROR')
					return
				tenx_software = [s for s in value.get('software', []) if s.startswith('Cell Ranger') or s.startswith('Space Ranger')]
				if tenx_software and fc['feature_count'] in cellranger_ref_feature_counts:
					if value.get('genome_annotation','') != cellranger_ref_feature_counts[fc['feature_count']]:
						detail = ('File {} has genome_annotation {}, expecting {} based on {} genes using 10x software.'.format(
							audit_link(path_to_text(value['@id']), value['@id']),
							value['genome_annotation'],
							cellranger_ref_feature_counts[fc['feature_count']],
							fc['feature_count']
							)
						)
						yield AuditFailure('10x reference inconsistency', detail, level='ERROR')
						return


def metrics_types(value, system):
	if value['status'] in ['deleted']:
		return

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


def annotation_not_genes(value, system):
	if value['status'] in ['deleted']:
		return

	if value.get('genome_annotation'):
		if 'gene quantifications' not in value.get('output_types') and 'transcript quantifications' not in value.get('output_types'):
			detail = ('File {} has genome_annotation but does not have gene/transcript quantifications.'.format(
				audit_link(path_to_text(value['@id']), value['@id'])
				)
			)
			yield AuditFailure('annotation without gene quantifications', detail, level='ERROR')
			return


def audit_Visium_h5s(value, system):
	if value['status'] in ['deleted']:
		return

	for l in value['libraries']:
		if l['protocol']['title'] == 'Visium 10x GE' and value.get('s3_uri'):
			file_ext = value['s3_uri'].split('.')[-1]
			if file_ext != 'h5':
				detail = ('File {} is from Visium and a .h5 is needed, not {}.'.format(
					audit_link(path_to_text(value['@id']), value['@id']),
					file_ext
					)
				)
				yield AuditFailure('Visium raw matrix format error', detail, level='ERROR')
				return


function_dispatcher = {
	'audit_analysis_library_types': audit_analysis_library_types,
	'audit_complete_derived_from': audit_complete_derived_from,
	'audit_read_count_compare': audit_read_count_compare,
	'audit_gene_count': audit_gene_count,
	'metrics_types': metrics_types,
	'annotation_not_genes': annotation_not_genes,
	'audit_Visium_h5s': audit_Visium_h5s
}

@audit_checker('RawMatrixFile',
			   frame=[
				   'derived_from',
				   'derived_from.derived_from',
				   'derived_from.libraries',
				   'quality_metrics',
				   'libraries',
				   'libraries.protocol'
			   ])
def audit_raw_matrix_file(value, system):
	for function_name in function_dispatcher.keys():
		for failure in function_dispatcher[function_name](value, system):
			yield failure

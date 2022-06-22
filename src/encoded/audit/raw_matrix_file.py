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
        input_reads = {}
        for df in value.get('derived_from'):
            if df['@type'][0] != 'RawSequenceFile' or df.get('validated') != True:
                return
            seqrun = df['derived_from'][0]['uuid']
            if seqrun not in input_reads.keys():
                seqrun_reads = df.get('read_count')
                input_reads[seqrun] = seqrun_reads
        in_reads = 0
        for v in input_reads.values():
            in_reads += v

        out_reads = 0
        for qc in value.get('quality_metrics'):
            if qc['@type'][0] == 'AtacMetrics' and 'total_fragments' in qc:
                out_reads += qc['total_fragments']
            elif qc['@type'][0] == 'RnaMetrics' and 'total_reads' in qc:
                out_reads += qc['total_reads']

        if in_reads != out_reads and out_reads !=0:
            detail = ('File {} has {} reads but input objects total {} reads.'.format(
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
	               'quality_metrics'
               ])
def audit_raw_matrix_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

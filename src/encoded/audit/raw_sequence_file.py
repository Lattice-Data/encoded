from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def no_read_type(value, system):
    if value['status'] in ['deleted']:
        return

    if value.get('no_file_available') != True and not value.get('read_type'):
        detail = ('File {} does not have a read_type.'.format(
            audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('no read_type', detail, level='ERROR')


def no_file_stats(value, system):
    if value['status'] in ['deleted']:
        return

    if value.get('no_file_available') != True and value.get('validated') == True:
        missing = []
        for stat in ['file_size','sha256','crc32c']:
            if not value.get(stat):
                missing.append(stat)
        if missing:
            detail = ('File {} does not have {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ','.join(missing)
                )
            )
            yield AuditFailure('missing file stats', detail, level='ERROR')
            return


def not_validated(value, system):
    if value['status'] in ['deleted']:
        return

    if value.get('no_file_available') != True and value.get('validated') != True:
        detail = ('File {} has not been validated.'.format(
            audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('file not validated', detail, level='ERROR')
        return


def no_uri(value, system):
    if value['status'] in ['deleted']:
        return

    if value.get('no_file_available') != True:
        if not (value.get('s3_uri') or value.get('external_uri')):
            detail = ('File {} has no s3_uri, external_uri, and is not marked as no_file_available.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('file access not specified', detail, level='ERROR')
            return


def audit_library_protocol_standards(value, system):
    '''
    We check fastq metadata against the expected values based on the
    library protocol used to generate the sequence data.
    '''
    if value['status'] in ['deleted']:
        return

    if value.get('no_file_available') != True and value.get('validated') == True:
        prot = value['libraries'][0]['protocol']
        stds_flag = False
        for standard in prot.get('sequence_file_standards',[]):
            if standard['read_type'] == value.get('read_type'):
                my_standard = standard
                stds_flag = True
        if not stds_flag:
            detail = ('File {} derives from Library Protocol {} with no noted standards for read_type {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(prot['@id']), prot['@id']),
                value.get('read_type')
                )
            )
            yield AuditFailure('no protocol standards', detail, level='ERROR')
            return

        for k in ['sequence_elements', 'demultiplexed_type']:
            if my_standard[k] != value.get(k):
                detail = ('{} of file {} should be {} but is {}'.format(
                    k,
                    audit_link(path_to_text(value['@id']), value['@id']),
                    my_standard[k],
                    value.get(k)
                    )
                )
                yield AuditFailure('does not meet protocol standards', detail, level='INTERNAL_ACTION')
        if my_standard['read_length'] != value.get('read_length'):
            fail_flag = False
            rl_spec = my_standard['read_length_specification']
            if not value.get('read_length'):
                audit_level = 'ERROR'
                fail_flag = True
            elif rl_spec == 'exact':
                rl_spec = 'exactly'
                audit_level = 'ERROR'
                fail_flag = True
            elif rl_spec == 'minimum' and value.get('read_length') < my_standard['read_length']:
                audit_level = 'ERROR'
                fail_flag = True
            elif rl_spec == 'ideal' and value.get('read_length') < my_standard['read_length']:
                rl_spec = 'ideally'
                audit_level = 'WARNING'
                fail_flag = True
            if fail_flag == True:
                detail = ('{} of file {} is {}, should be {} {} based on standards for {}'.format(
                    'read_length',
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value.get('read_length'),
                    rl_spec,
                    my_standard['read_length'],
                    audit_link(path_to_text(prot['@id']), prot['@id'])
                    )
                )
                yield AuditFailure('does not meet protocol standards', detail, level=audit_level)


function_dispatcher = {
    'no_read_type': no_read_type,
    'no_file_stats': no_file_stats,
    'not_validated': not_validated,
    'no_uri': no_uri,
    'audit_library_protocol_standards': audit_library_protocol_standards
}


@audit_checker('RawSequenceFile',
               frame=['libraries',
                      'libraries.protocol'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure


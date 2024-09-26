from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


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

        if my_standard['read_length'] != value.get('read_length'):
            fail_flag = False
            rl_spec = my_standard['read_length_specification']
            if not value.get('read_length'):
                audit_level = 'ERROR'
                fail_flag = True
            elif rl_spec == 'exact' and value.get('read_length') > my_standard['read_length']:
                rl_spec = 'exactly'
                audit_level = 'WARNING'
                fail_flag = True
            elif rl_spec in ['minimum','exact'] and value.get('read_length') < my_standard['read_length']:
                audit_level = 'ERROR'
                fail_flag = True
                if rl_spec == 'exact':
                    rl_spec = 'exactly'
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
    'no_file_stats': no_file_stats,
    'audit_library_protocol_standards': audit_library_protocol_standards
}


@audit_checker('RawSequenceFile',
               frame=[
                    'libraries',
                    'libraries.protocol']
                )
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure


from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_read_types_counts_platform(value, system):
    '''
    All sequence files belonging to a SequencingRun
    should have the same number of reads.
    '''
    if value['status'] in ['deleted','archived']:
        return

    read_types = {}
    read_count_lib = set()
    plat_lib = set()
    for f in value.get('files'):
        if f.get('validated') != True:
            return
        if f.get('read_type'):
            if f['read_type'] in read_types.keys():
                read_types[f['read_type']].append(f['uuid'])
            else:
                read_types[f['read_type']] = [f['uuid']]
        read_count_lib.add(f.get('read_count'))
        if 'platform' in f:
            plat_lib.add(','.join(f['platform']))
    for k,v in read_types.items():
        if len(v) > 1:
            detail = ('SequencingRun {} has multiple {} files: {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                k,
                ','.join(v)
                )
            )
            yield AuditFailure('duplicated read type', detail, level='ERROR')
    if len(read_count_lib) != 1:
        detail = ('SequencingRun {} has files of variable read counts - {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            read_count_lib
            )
        )
        yield AuditFailure('variable read counts', detail, level='ERROR')
    if len(plat_lib) != 1:
        detail = ('SequencingRun {} has files of variable platforms - {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            plat_lib
            )
        )
        yield AuditFailure('variable platforms', detail, level='ERROR')
        return


def audit_required_files(value, system):
    '''
    All sequence files belonging to a SequencingRun
    should have the same number of reads.
    '''
    if value['status'] in ['deleted','archived']:
        return

    not_found = []
    protocol = value['derived_from'][0].get('protocol')
    if protocol.get('required_files'):
        for f in protocol['required_files']:
            prop_name = f.replace(' ','_').replace('Read','read') + '_file'
            if not value.get(prop_name):
                not_found.append(f)
        if not_found:
            detail = ('SequencingRun {} is missing {}, required based on standards for {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ','.join(not_found),
                audit_link(path_to_text(protocol['@id']), protocol['@id'])
                )
            )
            yield AuditFailure('missing required file', detail, level='ERROR')
            return


function_dispatcher = {
    'audit_read_types_counts_platform': audit_read_types_counts_platform,
    'audit_required_files': audit_required_files
}


@audit_checker('SequencingRun',
               frame=[
                    'derived_from',
                    'derived_from.protocol',
                    'files'
                ])
def audit_sequencing_run(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

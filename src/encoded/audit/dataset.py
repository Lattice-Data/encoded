from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_contributor_email(value, system):
    if value['status'] in ['deleted']:
        return

    need_email = []
    if 'corresponding_contributors' in value:
        for user in value['corresponding_contributors']:
            if not user.get('email'):
                need_email.append(user.get('uuid'))
    if need_email:
        detail = ('Dataset {} contains corresponding_contributors {} that do not have an email.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(need_email)
            )
        )
        yield AuditFailure('no corresponding email', detail, level='ERROR')
    return


def audit_contributor_lists(value, system):
    if value['status'] in ['deleted']:
        return

    duplicates = []
    if 'contributors' in value and 'corresponding_contributors' in value:
        for user in value['corresponding_contributors']:
            if user in value.get('contributors'):
                duplicates.append(user.get('uuid'))
    if duplicates:
        detail = ('Dataset {} contains duplicated contributors {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(duplicates)
            )
        )
        yield AuditFailure('duplicated contributors', detail, level='ERROR')
    return


def audit_dataset_raw_files(value, system):
    if value['status'] in ['deleted']:
        return

    raw_data = False
    file_names = []
    if 'original_files' in value:
        for f in value['original_files']:
            if f['@type'][0] == 'RawSequenceFile' and f['no_file_available'] != True and f['status'] != 'archived':
                raw_data = True
                if 's3_uri' in f:
                    file_names.append(f['s3_uri'].split('/')[-1])
                elif 'external_uri' in f:
                    file_names.append(f['external_uri'].split('/')[-1])
    if raw_data == False:
        detail = ('Dataset {} does not contain any raw sequence files.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('no raw data', detail, level='ERROR')
    else:
        redundant = []
        for f in file_names:
            if file_names.count(f) > 1 and f not in redundant:
                redundant.append(f)
        if redundant:
            detail = ('Dataset {} contains multiple raw sequence files named {}.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ','.join(redundant)
                )
            )
            yield AuditFailure('redundant raw data file names', detail, level='ERROR')
    return


def audit_dataset_dcp_required_properties(value, system):
    if value['status'] in ['deleted']:
        return

    dcp_reqs = ['dataset_title', 'description', 'funding_organizations']
    for req in dcp_reqs:
        if req not in value:
            detail = ('Dataset {} does not have {}, required by the DCP.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    req
                )
            )
            yield AuditFailure('missing DCP-required field', detail, level='ERROR')
    dcp_optional = ['corresponding_contributors', 'contributors']
    for opt in dcp_optional:
        if opt not in value:
            detail = ('Dataset {} does not have {}, strongly encouraged by the DCP.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    opt
                )
            )
            yield AuditFailure('missing DCP-encouraged field', detail, level='ERROR')
    return


function_dispatcher_with_files = {
    'audit_contributor_email': audit_contributor_email,
    'audit_contributor_lists': audit_contributor_lists,
    'audit_dataset_raw_files': audit_dataset_raw_files,
    'audit_dataset_dcp_required_properties': audit_dataset_dcp_required_properties
}

@audit_checker('Dataset',
               frame=[
                    'original_files',
                    'corresponding_contributors',
                    'contributors'
                ])
def audit_experiment(value, system):
    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system)
    return

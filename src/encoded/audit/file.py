from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL


def audit_file_assembly(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('assembly') and value.get('assembly') and \
           f.get('assembly') != value.get('assembly'):
            detail = ('Processed file {} assembly {} '
                'does not match assembly {} of the file {} '
                'it was derived from.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['assembly'],
                    f['assembly'],
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('inconsistent assembly',
                               detail, level='WARNING')
            return


def audit_file_genome_annotation(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('genome_annotation') and value.get('genome_annotation') and \
           f.get('genome_annotation') != value.get('genome_annotation'):
            detail = ('Processed file {} genome_annotation {} '
                'does not match genome_annotation {} of the file {} '
                'it was derived from.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['genome_annotation'],
                    f['genome_annotation'],
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('inconsistent genome_annotation',
                               detail, level='WARNING')
            return


function_dispatcher = {
    'audit_file_assembly': audit_file_assembly,
    'audit_file_genome_annotation': audit_file_genome_annotation
}


@audit_checker('File',
               frame=['derived_from',
                      'libraries'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure


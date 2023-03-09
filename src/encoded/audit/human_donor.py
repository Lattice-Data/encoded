from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ordinalize(number):
    n = int(number.split('.')[0])
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


def audit_bmi(value,system):
    if value['status'] in ['deleted']:
        return
    if 'body_mass_index' not in value:
        if value.get('height') and value.get('weight'):
            detail = ('Donor {} BMI can be calculated from reported height and weight.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('missing BMI', detail, level='ERROR')
            return


def audit_donor_age(value, system):
    if value.get('age'):
        age = value['age']
    else:
        age = value['conceptional_age']

    if value['status'] in ['deleted'] or age in ['unknown', 'variable', '>89'] or '>' in age or '<' in age:
        return

    if '-' in age:
        range_min = float(age.split('-')[0])
        range_max = float(age.split('-')[1])
        if range_min >= range_max:
            detail = ('Donor {} has inconsistent age range {}.'.format(
                audit_link(value['accession'], value['@id']),
                age
                )
            )
            yield AuditFailure('inconsistent age range', detail, level='ERROR')
            return
    else:
        range_min = float(age)

    years = 0
    if value.get('age_units') == 'month':
        years = range_min/12
    elif value.get('age_units') == 'year':
        years = range_min

    if years >= 90:
        detail = ('Donor {} has age {}, HIPAA requires no age 90 yr or older be reported, should be ">89".'.format(
            audit_link(value['accession'], value['@id']),
            value['age_display']
            )
        )
        yield AuditFailure('age in violation of HIPAA', detail, level='ERROR')
        return

def audit_donor_dev_stage(value, system):
    if value['status'] in ['deleted']:
        return

    dev = value['development_ontology']['term_name']
    post_term_end_mo = '-month-old human stage'
    post_term_end_yr = '-year-old human stage'
    pre_term_end_wk = ' week post-fertilization human stage'

    if '>' in value['age_display'] or '<' in value['age_display']:
        return
    elif dev == 'variable' and value['age_display'] != 'variable':
        detail = ('Donor {} of development_ontology variable expected age variable.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('inconsistent age, development', detail, level='ERROR')
        return
    elif value['age_display'] == 'unknown' or '-' in value.get('age','') or '-' in value.get('conceptional_age',''):
        if dev.endswith(post_term_end_yr) or dev.endswith(pre_term_end_wk):
            detail = ('Donor {} of age {} not expected age-specific development_ontology ({}).'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
        else:
            return
    elif value.get('conceptional_age_units'):
        conc_age = float(value['conceptional_age'])
        if value.get('conceptional_age_units') == 'week' and conc_age <= 8 or \
            value.get('conceptional_age_units') == 'day' and conc_age <= 56:
            if 'embryonic human stage' not in value['development_ontology']['development_slims']:
                detail = ('Donor {} of age 56 days (8 wk) or less should be embryonic, not {}.'.format(
                    audit_link(value['accession'], value['@id']),
                    value['development_ontology']['development_slims']
                    )
                )
                yield AuditFailure('inconsistent age, development', detail, level='ERROR')
                return
            else:
                return
        elif value.get('conceptional_age_units') == 'week' and conc_age > 8:
            week = conc_age
            if week %1 != 0:
                week += 1
            week = int(week//1)
            expected = ordinalize(str(week)) + pre_term_end_wk
        elif value.get('conceptional_age_units') == 'day' and conc_age > 56:
            days = conc_age
            week = days//7
            if days%7 != 0:
                week += 1
            expected = ordinalize(str(week)) + pre_term_end_wk
        else:
            return
    elif value.get('age_units') == 'year':
        if value['age'] == '>89':
            expected = '80 year-old and over human stage'
        else:
            if 'month' in dev:
                expected = str(int(float(value['age'])*12)) + post_term_end_mo
            else:
                expected = value['age'].split('.')[0] + post_term_end_yr
    elif value.get('age_units') == 'month':
        if float(value['age']) <= 23:
            expected = str(int(float(value['age']))) + post_term_end_mo
        else:
            years = int(value['age'])//12
            expected = str(years) + post_term_end_yr
    elif value['age_display'] == 'variable':
        expected = 'variable'

    if dev != expected:
        detail = ('Donor {} of age {} expected development_ontology {}, not {}.'.format(
            audit_link(value['accession'], value['@id']),
            value.get('age_display'),
            expected,
            dev
            )
        )
        yield AuditFailure('inconsistent age, development', detail, level='ERROR')
        return


def ontology_check_dev(value, system):
    field = 'development_ontology'
    dbs = ['HsapDv']
    terms = ['NCIT:C17998','NCIT:C54166']

    term = value[field]['term_id']
    ont_db = term.split(':')[0]
    if ont_db not in dbs and term not in terms:
        detail = ('Donor {} {} {} not from {} or {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            term,
            ','.join(dbs),
            ','.join(terms)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def ontology_check_eth(value, system):
    field = 'ethnicity'
    dbs = ['HANCESTRO']
    terms = ['NCIT:C17998']

    for e in value[field]:
        term = e['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs and term not in terms:
            detail = ('Donor {} {} {} not from {} or {}.'.format(
                audit_link(value['accession'], value['@id']),
                field,
                term,
                ','.join(dbs),
                ','.join(terms)
                )
            )
            yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def ontology_check_dis(value, system):
    field = 'diseases'
    dbs = ['MONDO']

    invalid  = []
    for d in value.get(field, []):
        term = d['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Donor {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def ontology_check_anc(value, system):
    field = 'ancestry'
    dbs = ['HANCESTRO', 'NTR']

    invalid = []
    for d in value.get(field, []):
        term = d['ancestry_group']['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Donor {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def audit_ancestry(value, system):
    if 'ancestry' in value:
        total_frac = sum([a['fraction'] for a in value['ancestry']])
        if round(total_frac,2) != 1:
            detail = ('Donor {} ancestry fractions total {}, expecting 1.'.format(
                audit_link(value['accession'], value['@id']),
                str(total_frac)
                )
            )
            yield AuditFailure('ancestry error', detail, 'ERROR')


        dup_groups = []
        anc_groups = [a['ancestry_group']['term_id'] for a in value['ancestry']]
        for a in anc_groups:
            if anc_groups.count(a) > 1 and a not in dup_groups:
                dup_groups.append(a)
        if dup_groups:
            detail = ('Donor {} ancestry has duplicate groups: {}.'.format(
                audit_link(value['accession'], value['@id']),
                ','.join(dup_groups)
                )
            )
            yield AuditFailure('ancestry error', detail, 'ERROR')


function_dispatcher = {
    'audit_bmi': audit_bmi,
    'audit_donor_age': audit_donor_age,
    'audit_donor_dev_stage': audit_donor_dev_stage,
    'ontology_check_dev': ontology_check_dev,
    'ontology_check_eth': ontology_check_eth,
    'ontology_check_dis': ontology_check_dis,
    'ontology_check_anc': ontology_check_anc,
    'audit_ancestry': audit_ancestry
}

@audit_checker('HumanDonor',
               frame=[
                'development_ontology',
                'ethnicity',
                'ancestry.ancestry_group',
                'diseases'
                ])
def audit_donor(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

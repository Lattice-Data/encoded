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


def family_med_history(value, system):
    if value['status'] in ['deleted']:
        return

    if 'family_medical_history' in value:
        terms = []
        for h in value['family_medical_history']:
            terms.append(h['diagnosis'])
            if 'family_members' in h and h['present'] == False:
                detail = ('Donor {} has specified family_members with a history of {} but is marked as present False.'.format(
                    audit_link(value['accession'], value['@id']),
                    h['diagnosis']
                    )
                )
                yield AuditFailure('inconsistent family medical history', detail, level='ERROR')
                return
        for t in terms:
            if terms.count(t) > 1:
                detail = ('Donor {} has duplicate family_medical_history.diagnosis of {}.'.format(
                    audit_link(value['accession'], value['@id']),
                    t
                    )
                )
                yield AuditFailure('duplicate family medical history', detail, level='ERROR')
                return



def audit_bmi(value,system):
    if value['status'] in ['deleted']:
        return

    if value.get('height') and value.get('weight') and not value.get('body_mass_index'):
        detail = ('Donor {} BMI can be calculated from reported height and weight.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing BMI', detail, level='ERROR')
        return


def audit_donor_age(value, system):
    if value['status'] in ['deleted']:
        return

    if value.get('age'):
        age = value['age']
    else:
        age = value['conceptional_age']

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

def audit_donor_dev_stage(value, system):
    if value['status'] in ['deleted']:
        return

    dev = value['development_ontology']['term_name']
    post_term_end_mo = '-month-old stage'
    post_term_end_yr = '-year-old stage'
    pre_term_end_wk = ' week post-fertilization stage'

    if dev == 'variable' and value['age_display'] != 'variable':
        detail = ('Donor {} of development_ontology variable expected age variable.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('inconsistent age, development', detail, level='ERROR')
        return
    elif value['age_display'] == 'unknown' or '-' in value['age_display'].replace('post-conception','') or '>' in value['age_display'] or '<' in value['age_display']:
        if dev.endswith(post_term_end_yr) or dev.endswith(post_term_end_mo) or dev.endswith(pre_term_end_wk):
            detail = ('Donor {} of age {} not expected age-specific development_ontology ({}).'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
        return
    elif value.get('conceptional_age_units'):
        conc_age = float(value['conceptional_age'])
        if value.get('conceptional_age_units') == 'week' and conc_age <= 8 or \
            value.get('conceptional_age_units') == 'day' and conc_age <= 56:
            if 'embryonic stage' not in value['development_ontology']['development_slims']:
                detail = ('Donor {} of age 56 days (8 wk) or less should be embryonic, not {}.'.format(
                    audit_link(value['accession'], value['@id']),
                    value['development_ontology']['development_slims']
                    )
                )
                yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
        elif value.get('conceptional_age_units') == 'week' and conc_age > 8:
            week = conc_age
            week += 1
            week = int(week//1)
            expected = ordinalize(str(week)) + pre_term_end_wk
        elif value.get('conceptional_age_units') == 'day' and conc_age > 56:
            days = conc_age
            week = days//7
            week += 1
            expected = ordinalize(str(week)) + pre_term_end_wk
        else:
            return
    elif value.get('age_units') == 'year':
        if value['age'] == '>89':
            expected = '80 year-old and over stage'
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
    elif value.get('age_units') == 'day':
        if float(value['age']) <= 30:
            expected = 'newborn stage (0-28 days)'
        else:
            months = value['age'] //30
            if months <= 23:
                expected = str(months) + post_term_end_mo
            else:
                years = months//12
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
    if value['status'] in ['deleted'] or field not in value:
        return

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
    if value['status'] in ['deleted'] or field not in value:
        return

    dbs = ['HANCESTRO', 'AfPO']
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
    if value['status'] in ['deleted'] or field not in value:
        return

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


def audit_ancestry(value, system):
    field = 'ancestry'
    if value['status'] in ['deleted'] or field not in value:
        return

    dbs = ['HANCESTRO', 'AfPO', 'NTR']

    invalid = []
    for d in value.get(field):
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


    total_frac = sum([a['fraction'] for a in value[field]])
    if round(total_frac,2) != 1:
        detail = ('Donor {} ancestry fractions total {}, expecting 1.'.format(
            audit_link(value['accession'], value['@id']),
            str(total_frac)
            )
        )
        yield AuditFailure('ancestry error', detail, 'ERROR')


    dup_groups = []
    anc_groups = [a['ancestry_group']['term_id'] for a in value[field]]
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


def qa_cause_of_death(value, system):
    if value['status'] in ['deleted']:
        return

    if 'causes_of_death' in value:
        need = ['Cause of Death','Disease, Disorder or Finding','Suicide','Dead']
        for c in value['causes_of_death']:
            qa_terms_incl = [e for e in c.get('qa_slims', []) if e in need]
            if qa_terms_incl == [] and c['term_name'] != 'Unknown':
                detail = ('Donor {} causes_of_death {} neither NCIT:C17998 (Unknown) nor a descendant of NCIT:C81239, NCIT:C7057, NCIT:C82465, or NCIT:C3394.'.format(
                    audit_link(value['accession'], value['@id']),
                    c['term_name']
                    )
                )
                yield AuditFailure('causes_of_death error', detail, 'ERROR')


function_dispatcher = {
    'family_med_history': family_med_history,
    'audit_bmi': audit_bmi,
    'audit_donor_age': audit_donor_age,
    'audit_donor_dev_stage': audit_donor_dev_stage,
    'ontology_check_dev': ontology_check_dev,
    'ontology_check_eth': ontology_check_eth,
    'ontology_check_dis': ontology_check_dis,
    'audit_ancestry': audit_ancestry,
    'qa_cause_of_death': qa_cause_of_death
}

@audit_checker('HumanDonor',
               frame=[
                    'family_medical_history',
                    'development_ontology',
                    'ethnicity',
                    'ancestry.ancestry_group',
                    'diseases',
                    'causes_of_death'
                ])
def audit_donor(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    CONNECTION,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


def property_closure(request, propname, root_uuid):
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen


@abstract_collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Listing of all types of biosample.',
    })
class Biosample(Item):
    base_types = ['Biosample'] + Item.base_types
    name_key = 'accession'
    rev = {}
    embedded = []
    audit_inherit = []
    set_status_up = [
        'genetic_modifications',
        'treatments',
        'documents',
        'source'
    ]
    set_status_down = []

    @calculated_property(define=True,
                         schema={"title": "Donors",
                                 "type": "array",
                                 "items": {
                                    "type": 'string',
                                    "linkTo": "Donor"
                                    }
                                })
    def donors(self, request, registry, accession=None):
        connection = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid) - {str(self.uuid)}
        obj_props = (request.embed(uuid, '@@object') for uuid in derived_from_closure)
        all_donors = {
            props['accession']
            for props in obj_props
            if 'Donor' in props['@type']
        }
        return sorted(all_donors)


    @calculated_property(define=True,
                         schema={"title": "Sex",
                                 "type": "string"})
    def sex(self, request, donor=None, model_organism_sex=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the sex from the donor
                donorObject = request.embed(donor, '@@object')
                if 'sex' in donorObject:
                    return donorObject['sex']
                else:
                    return 'unknown'
            else:
                return 'unknown'
        else:
            if model_organism_sex is not None:
                return model_organism_sex
            else:
                return 'unknown'

    @calculated_property(define=True,
                         schema={"title": "Age",
                                 "type": "string"})
    def age(self, request, donor=None, model_organism_age=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the age from the donor
                donorObject = request.embed(donor, '@@object')
                if 'age' in donorObject:
                    return donorObject['age']
                else:
                    return 'unknown'
            else:
                return 'unknown'
        else:
            if model_organism_age is not None:
                return model_organism_age
            else:
                return 'unknown'

    @calculated_property(define=True,
                         schema={"title": "Age units",
                                 "type": "string"})
    def age_units(self, request, donor=None, model_organism_age_units=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the age_units from the donor
                donorObject = request.embed(donor, '@@object')
                if 'age_units' in donorObject:
                    return donorObject['age_units']
                else:
                    return None
            else:
                return None
        else:
            return model_organism_age_units

    @calculated_property(define=True,
                         schema={"title": "Health status",
                                 "type": "string"})
    def health_status(self, request, donor=None, model_organism_health_status=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True and donor is not None:
            donorObject = request.embed(donor, '@@object')
            if 'health_status' in donorObject:
                return donorObject['health_status']
            else:
                return None
        else:
            if humanFlag is False:
                return model_organism_health_status
            return None

    @calculated_property(define=True,
                         schema={"title": "Life stage",
                                 "type": "string"})
    def life_stage(self, request, donor=None, mouse_life_stage=None, fly_life_stage=None,
                   worm_life_stage=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True and donor is not None:
            donorObject = request.embed(donor, '@@object')
            if 'life_stage' in donorObject:
                return donorObject['life_stage']
            else:
                return 'unknown'
        else:
            if humanFlag is False:
                if mouse_life_stage is not None:
                    return mouse_life_stage
                if fly_life_stage is not None:
                    return fly_life_stage
                if worm_life_stage is not None:
                    return worm_life_stage
            return 'unknown'

    @calculated_property(schema={
        "title": "Applied modifications",
        "description": "All genetic modifications made in either the model organism and/or biosample.",
        "type": "array",
        "items": {
            "title": "Applied modification",
            "description": "Genetic modification made in either the model organism and/or biosample.",
            "comment": "See genetic_modification.json for available identifiers.",
            "type": "string",
            "linkTo": "GeneticModification",
        }
    }, define=True)
    def applied_modifications(self, request, genetic_modifications=None, model_organism_donor_modifications=None):
        return get_applied_modifications(genetic_modifications, model_organism_donor_modifications)


    @calculated_property(schema={
        "title": "Age display",
        "type": "string",
    })
    def age_display(self, request, donor=None, model_organism_age=None,
                    model_organism_age_units=None, post_synchronization_time=None,
                    post_synchronization_time_units=None):
        if post_synchronization_time is not None and post_synchronization_time_units is not None:
            return u'{}'.format(
                pluralize(post_synchronization_time, post_synchronization_time_units)
                )
        if donor is not None:
            donor = request.embed(donor, '@@object')
            if 'age' in donor and 'age_units' in donor:
                if donor['age'] == 'unknown':
                    return ''
                return u'{}'.format(pluralize(donor['age'], donor['age_units']))
        if model_organism_age is not None and model_organism_age_units is not None:
            return u'{}'.format(
                pluralize(model_organism_age, model_organism_age_units)
            )
        return None

    @calculated_property(schema={
        "title": "Summary",
        "type": "string",
    })
    def summary(self, request,
                organism=None,
                donor=None,
                age=None,
                age_units=None,
                life_stage=None,
                sex=None,
                biosample_ontology=None,
                starting_amount=None,
                starting_amount_units=None,
                depleted_in_term_name=None,
                phase=None,
                synchronization=None,
                subcellular_fraction_term_name=None,
                post_synchronization_time=None,
                post_synchronization_time_units=None,
                post_treatment_time=None,
                post_treatment_time_units=None,
                treatments=None,
                part_of=None,
                originated_from=None,
                transfection_method=None,
                transfection_type=None,
                preservation_method=None,
                genetic_modifications=None,
                model_organism_donor_modifications=None):

        sentence_parts = [
            'organism_name',
            'genotype_strain',
            'sex_stage_age',
            'synchronization',
            'term_phrase',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'preservation_method',
            'depleted_in',
            'phase',
            'fractionated'
        ]
        organismObject = None
        donorObject = None
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
        if donor is not None:
            donorObject = request.embed(donor, '@@object')

        treatment_objects_list = None
        if treatments is not None and len(treatments) > 0:
            treatment_objects_list = []
            for t in treatments:
                treatment_objects_list.append(request.embed(t, '@@object'))

        part_of_object = None
        if part_of is not None:
            part_of_object = request.embed(part_of, '@@object')

        originated_from_object = None
        if originated_from is not None:
            originated_from_object = request.embed(originated_from, '@@object')

        modifications_list = None

        applied_modifications = get_applied_modifications(
            genetic_modifications, model_organism_donor_modifications)

        if applied_modifications:
            modifications_list = []
            for gm in applied_modifications:
                gm_object = request.embed(gm, '@@object')
                modification_dict = {'category': gm_object.get('category')}
                if gm_object.get('modified_site_by_target_id'):
                    modification_dict['target'] = request.embed(
                        gm_object.get('modified_site_by_target_id'),
                                      '@@object').get('label')
                if gm_object.get('introduced_tags'):
                    modification_dict['tags'] = []
                    for tag in gm_object.get('introduced_tags'):
                        tag_dict = {'location': tag['location'], 'name': tag['name']}
                        if tag.get('promoter_used'):
                            tag_dict['promoter'] = request.embed(
                                tag.get('promoter_used'),
                                        '@@object').get('label')
                        modification_dict['tags'].append(tag_dict)

                modifications_list.append((gm_object['method'], modification_dict))

        if biosample_ontology:
            biosample_type_object = request.embed(biosample_ontology, '@@object')
            biosample_term_name = biosample_type_object['term_name']
            biosample_type = biosample_type_object['classification']
        else:
            biosample_term_name = None
            biosample_type = None

        biosample_dictionary = generate_summary_dictionary(
            request,
            organismObject,
            donorObject,
            age,
            age_units,
            life_stage,
            sex,
            biosample_term_name,
            biosample_type,
            starting_amount,
            starting_amount_units,
            depleted_in_term_name,
            phase,
            subcellular_fraction_term_name,
            synchronization,
            post_synchronization_time,
            post_synchronization_time_units,
            post_treatment_time,
            post_treatment_time_units,
            treatment_objects_list,
            preservation_method,
            part_of_object,
            originated_from_object,
            modifications_list)

        return construct_biosample_summary([biosample_dictionary],
                                           sentence_parts)

    @calculated_property(schema={
        "title": "Perturbed",
        "description": "A flag to indicate whether the biosample has been perturbed with a treatment or genetic modification.",
        "type": "boolean",
        "notSubmittable": True,
    })
    def perturbed(
        self,
        request,
        applied_modifications,
        treatments=None,
    ):
        return bool(treatments) or any(
            (
                request.embed(m, '@@object').get('perturbation', False)
                for m in applied_modifications
            )
        )


def generate_summary_dictionary(
        request,
        organismObject=None,
        donorObject=None,
        age=None,
        age_units=None,
        life_stage=None,
        sex=None,
        biosample_term_name=None,
        biosample_type=None,
        starting_amount=None,
        starting_amount_units=None,
        depleted_in_term_name=None,
        phase=None,
        subcellular_fraction_term_name=None,
        synchronization=None,
        post_synchronization_time=None,
        post_synchronization_time_units=None,
        post_treatment_time=None,
        post_treatment_time_units=None,
        treatment_objects_list=None,
        preservation_method=None,
        part_of_object=None,
        originated_from_object=None,
        modifications_list=None,
        experiment_flag=False):
    dict_of_phrases = {
        'organism_name': '',
        'genotype_strain': '',
        'term_phrase': '',
        'phase': '',
        'fractionated': '',
        'sex_stage_age': '',
        'synchronization': '',
        'originated_from': '',
        'treatments_phrase': '',
        'depleted_in': '',
        'modifications_list': '',
        'strain_background': '',
        'preservation_method': '',
        'experiment_term_phrase': ''
    }

    if organismObject is not None:
        if 'scientific_name' in organismObject:
            dict_of_phrases['organism_name'] = organismObject['scientific_name']
            if organismObject['scientific_name'] != 'Homo sapiens':  # model organism
                if donorObject is not None:
                    if 'strain_name' in donorObject and donorObject['strain_name'].lower() != 'unknown':
                        dict_of_phrases['genotype_strain'] = 'strain ' + \
                                                                donorObject['strain_name']
                    if 'genotype' in donorObject and donorObject['genotype'].lower() != 'unknown':
                        d_genotype = donorObject['genotype']
                        if organismObject['scientific_name'].find('Drosophila') == -1:
                            if d_genotype[-1] == '.':
                                dict_of_phrases['genotype_strain'] += ' (' + \
                                                                        d_genotype[:-1] + ')'
                            else:
                                dict_of_phrases['genotype_strain'] += ' (' + \
                                                                        d_genotype + ')'
                    if 'strain_background' in donorObject and \
                        donorObject['strain_background'].lower() != 'unknown':
                        dict_of_phrases['strain_background'] = donorObject['strain_background']
                    else:
                        dict_of_phrases['strain_background'] = dict_of_phrases['genotype_strain']
    if age is not None and age_units is not None:
        dict_of_phrases['age_display'] = pluralize(age, age_units)

    if life_stage is not None and life_stage != 'unknown':
        dict_of_phrases['life_stage'] = life_stage

    if sex is not None and sex != 'unknown':
        if experiment_flag is True:
            if sex != 'mixed':
                dict_of_phrases['sex'] = sex

        else:
            dict_of_phrases['sex'] = sex   
    if preservation_method is not None:
        dict_of_phrases['preservation_method'] = 'preserved by ' + \
                                                            preservation_method
    if biosample_term_name is not None:
        dict_of_phrases['sample_term_name'] = biosample_term_name

    if biosample_type is not None and \
        biosample_type not in ['whole organisms', 'whole organism']:
        dict_of_phrases['sample_type'] = biosample_type

    term_name = ''

    if 'sample_term_name' in dict_of_phrases:
        if dict_of_phrases['sample_term_name'] == 'multi-cellular organism':
            term_name += 'whole organisms'
        else:
            term_name += dict_of_phrases['sample_term_name']

    dict_of_phrases['experiment_term_phrase'] = term_name

    term_type = ''

    if 'sample_type' in dict_of_phrases:
        term_type += dict_of_phrases['sample_type']

    term_dict = {}
    for w in term_type.split(' '):
        if w not in term_dict:
            term_dict[w] = 1

    term_phrase = ''
    for w in term_name.split(' '):
        if w not in term_dict and (w+'s') not in term_dict:
            term_dict[w] = 1
            term_phrase += ' ' + w

    term_phrase += ' ' + term_type
    if term_phrase.startswith(' of'):
        term_phrase = ' ' + term_phrase[3:]

    if len(term_phrase) > 0:
        dict_of_phrases['term_phrase'] = term_phrase[1:]

    if starting_amount is not None and starting_amount_units is not None:
        if starting_amount_units[-1] != 's':
            dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                str(starting_amount_units) + 's'
        else:
            dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                str(starting_amount_units)

    if depleted_in_term_name is not None and len(depleted_in_term_name) > 0:
        dict_of_phrases['depleted_in'] = 'depleted in ' + \
                                            str(depleted_in_term_name).replace('\'', '')[1:-1]

    if phase is not None:
        dict_of_phrases['phase'] = phase + ' phase'

    if subcellular_fraction_term_name is not None:
        if subcellular_fraction_term_name == 'nucleus':
            dict_of_phrases['fractionated'] = 'nuclear fraction'
        if subcellular_fraction_term_name == 'cytosol':
            dict_of_phrases['fractionated'] = 'cytosolic fraction'
        if subcellular_fraction_term_name == 'chromatin':
            dict_of_phrases['fractionated'] = 'chromatin fraction'
        if subcellular_fraction_term_name == 'membrane':
            dict_of_phrases['fractionated'] = 'membrane fraction'
        if subcellular_fraction_term_name == 'mitochondria':
            dict_of_phrases['fractionated'] = 'mitochondrial fraction'
        if subcellular_fraction_term_name == 'nuclear matrix':
            dict_of_phrases['fractionated'] = 'nuclear matrix fraction'
        if subcellular_fraction_term_name == 'nucleolus':
            dict_of_phrases['fractionated'] = 'nucleolus fraction'
        if subcellular_fraction_term_name == 'nucleoplasm':
            dict_of_phrases['fractionated'] = 'nucleoplasmic fraction'
        if subcellular_fraction_term_name == 'polysome':
            dict_of_phrases['fractionated'] = 'polysomic fraction'
        if subcellular_fraction_term_name == 'insoluble cytoplasmic fraction':
            dict_of_phrases['fractionated'] = 'insoluble cytoplasmic fraction'

    if post_synchronization_time is not None and \
        post_synchronization_time_units is not None:
        dict_of_phrases['synchronization'] = '{} post synchronization'.format(
            pluralize(post_synchronization_time, post_synchronization_time_units)
            )
    if synchronization is not None:
        if synchronization.startswith('puff'):
            dict_of_phrases['synchronization'] += ' at ' + synchronization
        elif synchronization == 'egg bleaching':
            dict_of_phrases['synchronization'] += ' using ' + synchronization
        else:
            dict_of_phrases['synchronization'] += ' at ' + synchronization + ' stage'

    if post_treatment_time is not None and \
        post_treatment_time_units is not None:
        dict_of_phrases['post_treatment'] = '{} after the sample was '.format(
            pluralize(post_treatment_time, post_treatment_time_units)
            )

    if ('sample_type' in dict_of_phrases and
        dict_of_phrases['sample_type'] != 'cell line') or \
        ('sample_type' not in dict_of_phrases):
        phrase = ''

        if 'sex' in dict_of_phrases:
            if dict_of_phrases['sex'] == 'mixed':
                phrase += dict_of_phrases['sex'] + ' sex'
            else:
                phrase += dict_of_phrases['sex']

        stage_phrase = ''
        if 'life_stage' in dict_of_phrases:
            stage_phrase += ' ' + dict_of_phrases['life_stage']

        phrase += stage_phrase.replace("embryonic", "embryo")

        if 'age_display' in dict_of_phrases:
            phrase += ' (' + dict_of_phrases['age_display'] + ')'
        dict_of_phrases['sex_stage_age'] = phrase

    if treatment_objects_list is not None and len(treatment_objects_list) > 0:
        treatments_list = []
        for treatment_object in treatment_objects_list:
            to_add = ''
            amt = treatment_object.get('amount', '')
            amt_units = treatment_object.get('amount_units', '')
            treatment_term_name = treatment_object.get('treatment_term_name', '')
            dur = treatment_object.get('duration', '')
            dur_units = treatment_object.get('duration_units', '')
            to_add = "{}{}{}".format(
                (str(amt) + ' ' + amt_units + ' ' if amt and amt_units else ''),
                (treatment_term_name + ' ' if treatment_term_name else ''),
                ('for ' + pluralize(dur, dur_units) if dur and dur_units else '')
            )
            if to_add != '':
                treatments_list.append(to_add)

        if len(treatments_list) > 0:
            dict_of_phrases['treatments'] = treatments_list

    if 'treatments' in dict_of_phrases:
        if 'post_treatment' in dict_of_phrases:
            dict_of_phrases['treatments_phrase'] = dict_of_phrases['post_treatment']

        if len(dict_of_phrases['treatments']) == 1:
            dict_of_phrases['treatments_phrase'] += 'treated with ' + \
                                                    dict_of_phrases['treatments'][0]
        else:
            if len(dict_of_phrases['treatments']) > 1:
                dict_of_phrases[
                    'treatments_phrase'] += 'treated with ' + \
                                            ', '.join(map(str, dict_of_phrases['treatments']))

    if part_of_object is not None:
        dict_of_phrases['part_of'] = 'separated from biosample '+part_of_object['accession']

    if originated_from_object is not None:
        if 'biosample_ontology' in originated_from_object:
            biosample_object = request.embed(
                originated_from_object['biosample_ontology'],
                '@@object'
            )
            dict_of_phrases['originated_from'] = 'originated from {}'.format(
                biosample_object['term_name']
            )

    if modifications_list is not None and len(modifications_list) > 0:
        gm_methods = set()
        gm_summaries = set()
        for (gm_method, gm_object) in modifications_list:
            gm_methods.add(gm_method)
            gm_summaries.add(generate_modification_summary(gm_method, gm_object))
        if experiment_flag is True:
            dict_of_phrases['modifications_list'] = 'genetically modified using ' + \
                ', '.join(map(str, list(gm_methods)))
        else:
            dict_of_phrases['modifications_list'] = ', '.join(sorted(list(gm_summaries)))

    return dict_of_phrases


def generate_modification_summary(method, modification):

    modification_summary = ''
    if method in ['stable transfection', 'transient transfection'] and modification.get('target'):
        modification_summary = 'stably'
        if method == 'transient transfection':
            modification_summary = 'transiently'
        modification_summary += ' expressing'

        if modification.get('tags'):
            tags_list = []

            for tag in modification.get('tags'):
                addition = ''
                if tag.get('location') in ['N-terminal', 'C-terminal', 'internal']:
                    addition += ' ' + tag.get('location') + ' ' + tag.get('name') + '-tagged'
                addition += ' ' + modification.get('target')
                if tag.get('promoter'):
                    addition += ' under ' + tag.get('promoter') + ' promoter'
                tags_list.append(addition)
            modification_summary += ' ' + ', '.join(map(str, list(set(tags_list)))).strip()
        else:
            modification_summary += ' ' + modification.get('target')
    else:
        modification_summary = \
            'genetically modified (' + modification.get('category') + ') using ' + method
        if method == 'RNAi':
            modification_summary = 'expressing RNAi'

        if modification.get('target'):
            modification_summary += ' targeting ' + modification.get('target')
    return modification_summary.strip()


def generate_sentence(phrases_dict, values_list):
    sentence = ''
    for key in values_list:
        if phrases_dict[key] != '':
            if 'preservation_method' in key:
                sentence = sentence.strip() + ', ' + \
                                    phrases_dict[key].strip() + ' '
            else:
                sentence += phrases_dict[key].strip() + ' '
    return sentence.strip()


def is_identical(list_of_dicts, key):
    initial_value = list_of_dicts[0][key]
    for d in list_of_dicts:
        if d[key] != initial_value:
            return False
    return True


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


def get_applied_modifications(genetic_modifications=None, model_organism_donor_modifications=None):
    if genetic_modifications is not None and model_organism_donor_modifications is not None:
        return list(set(genetic_modifications + model_organism_donor_modifications))
    elif genetic_modifications is not None and model_organism_donor_modifications is None:
        return genetic_modifications
    elif genetic_modifications is None and model_organism_donor_modifications is not None:
        return model_organism_donor_modifications
    else:
        return []


def construct_biosample_summary(phrases_dictionarys, sentence_parts):
    negations_dict = {
        'phase': 'unspecified phase',
        'fractionated': 'unspecified fraction',
        'synchronization': 'not synchronized',
        'treatments_phrase': 'not treated',
        'depleted_in': 'not depleted',
        'genetic_modifications': 'not modified'
    }
    if len(phrases_dictionarys) > 1:
        index = 0
        min_index = len(sentence_parts)
        max_index = -1
        for part in sentence_parts:
            if is_identical(phrases_dictionarys, part) is False:
                if min_index > index:
                    min_index = index
                if max_index < index:
                    max_index = index
            index += 1

        if max_index == -1:
            sentence_to_return = generate_sentence(phrases_dictionarys[0], sentence_parts)
        else:
            if min_index == 0:
                prefix = ''
            else:
                prefix = generate_sentence(phrases_dictionarys[0], sentence_parts[0:min_index])
            if (max_index+1) == len(sentence_parts):
                suffix = ''
            else:
                suffix = generate_sentence(phrases_dictionarys[0], sentence_parts[max_index+1:])
            middle = []
            for d in phrases_dictionarys:
                part_to_add = generate_sentence(d, sentence_parts[min_index:max_index+1])
                if part_to_add != '':
                    middle.append(part_to_add)
                else:
                    constructed_middle = []
                    for x in range(min_index, max_index+1):
                        if sentence_parts[x] in negations_dict:
                            constructed_middle.append(negations_dict[sentence_parts[x]])
                    if len(constructed_middle) == 0:
                        middle.append('NONE')
                    elif len(constructed_middle) == 1:
                        middle.append(constructed_middle[0])
                    else:
                        middle.append(', '.join(map(str, constructed_middle)))
            sentence_middle = sorted(list(set(middle)))
            if prefix == '':
                sentence_to_return = ' and '.join(map(str, sentence_middle))
            else:
                sentence_to_return = prefix.strip() + ' ' + \
                    ' and '.join(map(str, sentence_middle))
            if suffix != '':
                sentence_to_return += ', ' + suffix
    else:
        sentence_to_return = generate_sentence(phrases_dictionarys[0], sentence_parts)

    words = sentence_to_return.split(' ')
    if words[-1] in ['transiently', 'stably']:
        sentence_to_return = ' '.join(words[:-1])

    rep = {
        ' percent': '%',
        '.0 ': ' ',
    }
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], sentence_to_return)


@abstract_collection(
    name='cultures',
    unique_key='accession',
    properties={
        'title': 'Cultures',
        'description': 'Listing of all types of culture.',
    })
class Culture(Biosample):
    base_types = ['Culture'] + Item.base_types
    embedded = Biosample.embedded + []


@collection(
    name='cell-cultures',
    unique_key='accession',
    properties={
        'title': 'Cell cultures',
        'description': 'Listing of Cell cultures',
    })
class CellCulture(Culture):
    item_type = 'cell_culture'
    schema = load_schema('encoded:schemas/cell_culture.json')
    embedded = Culture.embedded + []


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Biosample):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    embedded = Biosample.embedded + []


@collection(
    name='organoids',
    unique_key='accession',
    properties={
        'title': 'Organoids',
        'description': 'Listing of Organoids',
    })
class Organoid(Culture):
    item_type = 'organoid'
    schema = load_schema('encoded:schemas/organoid.json')
    embedded = Culture.embedded + []


@collection(
    name='tissues',
    unique_key='accession',
    properties={
        'title': 'Tissues',
        'description': 'Listing of Tissues',
    })
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('encoded:schemas/tissue.json')
    embedded = Biosample.embedded + []

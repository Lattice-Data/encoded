from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
    pluralize,
)
from .shared_calculated_properties import (
    CalculatedTreatmentSummary,
)


@abstract_collection(
    name='donors',
    unique_key='accession',
    properties={
        'title': "Donors",
        'description': 'Listing of all types of donor.',
    })
class Donor(Item, CalculatedTreatmentSummary):
    base_types = ['Donor'] + Item.base_types
    embedded = [
        'diseases',
        'organism',
        'development_ontology'
    ]
    name_key = 'accession'

    def unique_keys(self, properties):
        keys = super(Donor, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'external_ids' in properties:
                keys.setdefault('alias', []).extend(properties['external_ids'])
        return keys


    @calculated_property(define=True,
                        schema={
                        "title": "Age display",
                        "description": "The age and age units of the donor.",
                        "comment": "Do not submit. This is a calculated property",
                        "type": "string"})
    def age_display(self, request, age=None, age_units=None, conceptional_age=None, conceptional_age_units=None):
        if age == 'unknown' or conceptional_age == 'unknown':
            return 'unknown'
        elif age == 'variable':
            return 'variable'
        elif age != None:
            return u'{}'.format(pluralize(age, age_units))
        elif conceptional_age != None:
            return u'{} (post-conception)'.format(pluralize(conceptional_age, conceptional_age_units))
        else:
            return None


@abstract_collection(
    name='human-donors',
    unique_key='accession',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    base_types = ['HumanDonor'] + Donor.base_types
    schema = load_schema('encoded:schemas/human_donor.json')
    embedded = Donor.embedded + [
        'ethnicity',
        'family_medical_history',
        'family_medical_history.diagnosis']


    @calculated_property(schema={
        "title": "Summary ethnicity",
        "description": "A single ethnicity term until CELLxGENE enables an array.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "string"
    })
    def summary_ethnicity(self, request, ethnicity):
        if len(ethnicity) == 1:
            e = ethnicity[0].replace(':','_')
            term = request.embed(e, '@@object')['term_id']
            if term == 'NCIT:C17998':
                return 'unknown'
            else:
                return term
        else:
            all_slims = []
            for e in ethnicity:
                e = e.replace(':','_')
                slims = request.embed(e, '@@object').get('ethnicity_slims')
                if not slims:
                    return 'multiethnic'
                all_slims.append(slims)

            unpacked = [i for e in all_slims for i in e]
            for s in all_slims[0]:
                if unpacked.count(s) == len(all_slims):
                    return s

            return 'multiethnic'


@collection(
    name='human-prenatal-donors',
    unique_key='accession',
    properties={
        'title': 'Human prenatal donors',
        'description': 'Listing Biosample Donors'
    })
class HumanPrenatalDonor(HumanDonor):
    item_type = 'human_prenatal_donor'
    schema = load_schema('encoded:schemas/human_prenatal_donor.json')
    embedded = HumanDonor.embedded + []


    @calculated_property(schema={
        "title": "Age development stage redunancy",
        "description": "If true, the development_ontology term exactly defines the age.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "boolean"
    })
    def age_development_stage_redundancy(self, request, development_ontology, conceptional_age, conceptional_age_units=None):
        dev_stage = request.embed(development_ontology, '@@object?skip_calculated=true').get('term_name')
        if conceptional_age_units == 'week' and '.' not in conceptional_age and '-' not in conceptional_age:
            return True
        return False


@collection(
    name='human-postnatal-donors',
    unique_key='accession',
    properties={
        'title': 'Human postnatal donors',
        'description': 'Listing Biosample Donors'
    })
class HumanPostnatalDonor(HumanDonor):
    item_type = 'human_postnatal_donor'
    schema = load_schema('encoded:schemas/human_postnatal_donor.json')
    embedded = HumanDonor.embedded + ['causes_of_death']
    rev = {}


    @calculated_property(schema={
        "title": "Age development stage redunancy",
        "description": "If true, the development_ontology term exactly defines the age.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "boolean"
    })
    def age_development_stage_redundancy(self, request, development_ontology, age, age_units=None):
        decades = {
            'third decade human stage': '20-30 years',
            'fourth decade human stage': '30-40 years',
            'fifth decade human stage': '40-50 years',
            'sixth decade human stage': '50-60 years',
            'seventh decade human stage': '60-70 years',
            'eighth decade human stage': '70-80 years'

        }
        dev_stage = request.embed(development_ontology, '@@object?skip_calculated=true').get('term_name')
        if dev_stage == f'{age}-{str(age_units)}-old human stage':
            return True
        elif decades.get(dev_stage) == age + ' ' + str(age_units) + 's':
            return True

        return False

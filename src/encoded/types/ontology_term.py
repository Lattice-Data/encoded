from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
)


system_slim_terms = {
    'UBERON:0000363': 'reticuloendothelial system', #subclass of UBERON:0002405
    'UBERON:0002405': 'immune system',
    'UBERON:0004535': 'cardiovascular system', #subclass of UBERON:0001009
    'UBERON:0001009': 'circulatory system',
    'UBERON:0001017': 'central nervous system', #subclass of UBERON:0001016
    'UBERON:0000010': 'peripheral nervous system', #subclass of UBERON:0001016
    'UBERON:0001016': 'nervous system',
    'UBERON:0000383': 'musculature of body', #subclass of UBERON:0002204
    'UBERON:0001434': 'skeletal system', #subclass of UBERON:0002204
    'UBERON:0002204': 'musculoskeletal system',
    'UBERON:0001032': 'sensory system', #subclass of UBERON:0004456
    'UBERON:0004456': 'entire sense organ system',
    'UBERON:0001007': 'digestive system',
    'UBERON:0000949': 'endocrine system',
    'UBERON:0002330': 'exocrine system',
    'UBERON:0002390': 'hematopoietic system',
    'UBERON:0002416': 'integumental system',
    'UBERON:0001008': 'renal system',
    'UBERON:0000990': 'reproductive system',
    'UBERON:0001004': 'respiratory system'
}

organ_slim_terms = {
    'UBERON:0001155': 'colon', #subclass of UBERON:0000059,UBERON:0000160,UBERON:0001555
    'UBERON:0000059': 'large intestine', #subclass of UBERON:0000160,UBERON:0001555
    'UBERON:0002108': 'small intestine', #subclass of UBERON:0000160,UBERON:0001555
    'UBERON:0000160': 'intestine', #subclass of UBERON:0001555
    'UBERON:0001723': 'tongue', #subclass of UBERON:0000165,UBERON:0001555
    'UBERON:0001829': 'major salivary gland', #subclass of UBERON:0000165,UBERON:0002365,UBERON:0001555
    'UBERON:0000165': 'mouth', #subclass of UBERON:0001555
    'UBERON:0001043': 'esophagus', #subclass of UBERON:0001555
    'UBERON:0000945': 'stomach', #subclass of UBERON:0001555
    'UBERON:0006562': 'pharynx', #subclass of UBERON:0001555
    'UBERON:0001350': 'coccyx', #subclass of UBERON:0001474,UBERON:0004288
    'UBERON:0004288': 'skeleton',
    'UBERON:0002371': 'bone marrow', #subclass of UBERON:0001474
    'UBERON:0001474': 'bone element',
    'UBERON:0000007': 'pituitary gland', #subclass of UBERON:0000955,UBERON:0002368
    'UBERON:0003547': 'brain meninx', #subclass of UBERON:0000955
    'UBERON:0000955': 'brain',
    'UBERON:0002182': 'main bronchus', #subclass of UBERON:0002185
    'UBERON:0002185': 'bronchus',
    'UBERON:0000998': 'seminal vesicle', #subclass of UBERON:0000991,UBERON:0000473
    'UBERON:0000473': 'testis', #subclass of UBERON:0000991
    'UBERON:0000992': 'ovary', #subclass of UBERON:0000991
    'UBERON:0000991': 'gonad',
    'UBERON:0002073': 'hair follicle', #subclass of UBERON:0002097,UBERON:0000483
    'UBERON:0001820': 'sweat gland', #subclass of UBERON:0002097,UBERON:0000483,UBERON:0002365
    'UBERON:0001821': 'sebaceous gland', #subclass of UBERON:0002097,UBERON:0000483,UBERON:0002365
    'UBERON:0002097': 'skin of body',
    'UBERON:0001817': 'lacrimal gland', #subclass of UBERON:0000970,UBERON:0002365
    'UBERON:0000970': 'eye',
    'UBERON:0000029': 'lymph node', #subclass of UBERON:0005057
    'UBERON:0002106': 'spleen', #subclass of UBERON:0005057
    'UBERON:0002370': 'thymus', #subclass of UBERON:0002368,UBERON:0005057
    'UBERON:0002107': 'liver', #subclass of UBERON:0002368,UBERON:0002365
    'UBERON:0002369': 'adrenal gland', #subclass of UBERON:0002368
    'UBERON:0002046': 'thyroid gland', #subclass of UBERON:0002368
    'UBERON:0001132': 'parathyroid gland', #subclass of UBERON:0002368
    'UBERON:0002368': 'endocrine gland',
    'UBERON:0001911': 'mammary gland', #subclass of UBERON:0002365
    'UBERON:0000414': 'mucous gland', #subclass of UBERON:0002365
    'UBERON:0002365': 'exocrine gland',
    'UBERON:0000178': 'blood', #subclass of UBERON:0006314
    'UBERON:0006314': 'bodily fluid',
    'UBERON:0003509': 'arterial blood vessel', #subclass of UBERON:0001981,UBERON:0002049
    'UBERON:0001638': 'vein', #subclass of UBERON:0001981,UBERON:0002049
    'UBERON:0001981': 'blood vessel', #subclass of UBERON:0002049
    'UBERON:0001473': 'lymphatic vessel', #subclass of UBERON:0002049
    'UBERON:0000043': 'tendon', #subclass of UBERON:0002384
    'UBERON:0001013': 'adipose tissue', #subclass of UBERON:0002384
    'UBERON:0001987': 'placenta', #subclass of UBERON:0016887
    'UBERON:0000310': 'breast',
    'UBERON:0001103': 'diaphragm',
    'UBERON:0001690': 'ear',
    'UBERON:0000922': 'embryo',
    'UBERON:0003889': 'fallopian tube',
    'UBERON:0002110': 'gallbladder',
    'UBERON:0000948': 'heart',
    'UBERON:0002113': 'kidney',
    'UBERON:0001737': 'larynx',
    'UBERON:0002101': 'limb',
    'UBERON:0002048': 'lung',
    'UBERON:0001744': 'lymphoid tissue',
    'UBERON:0001021': 'nerve',
    'UBERON:0000004': 'nose',
    'UBERON:0001264': 'pancreas',
    'UBERON:0000989': 'penis',
    'UBERON:0002407': 'pericardium',
    'UBERON:0002367': 'prostate gland',
    'UBERON:0002240': 'spinal cord',
    'UBERON:0003126': 'trachea',
    'UBERON:0000056': 'ureter',
    'UBERON:0000057': 'urethra',
    'UBERON:0001255': 'urinary bladder',
    'UBERON:0000995': 'uterus',
    'UBERON:0000996': 'vagina',
    'UBERON:0001555': 'digestive tract',
    'UBERON:0002049': 'vasculature',
    'UBERON:0002384': 'connective tissue',
    'UBERON:0005057': 'immune organ',
    'UBERON:0007844': 'cartilage element',
    'UBERON:0016887': 'entire extraembryonic component',
    'UBERON:0000483': 'epithelium'
}

cell_slim_terms = {
    'CL:0000236': 'B cell', #subclass of CL:0000542,CL:0000738,CL:0000988
    'CL:0000084': 'T cell', #subclass of CL:0000542,CL:0000738,CL:0000988
    'CL:0000542': 'lymphocyte', #subclass of CL:0000763,CL:0000738,CL:0000988
    'CL:0000094': 'granulocyte', #subclass of CL:0000763,CL:0000738,CL:0000988
    'CL:0000576': 'monocyte', #subclass of CL:0000763,CL:0000738,CL:0000988
    'CL:0000763': 'myeloid cell', #subclass of CL:0000988
    'CL:0000738': 'leukocyte', #subclass of CL:0000988
    'CL:0000988': 'hematopoietic cell',
    'CL:0000312': 'keratinocyte', #subclass of CL:0000066
    'CL:0000115': 'endothelial cell', #subclass of CL:0000066
    'CL:0000066': 'epithelial cell',
    'CL:0000057': 'fibroblast', #subclass of CL:0002320
    'CL:0000669': 'pericyte', #subclass of CL:0002320
    'CL:0002320': 'connective tissue cell',
    'CL:0002321': 'embryonic cell (metazoa)',
    'CL:0002494': 'cardiocyte',
    'CL:0000148': 'melanocyte',
    'CL:0000056': 'myoblast',
    'CL:0002319': 'neural cell',
    'CL:0000192': 'smooth muscle cell',
    'CL:0000034': 'stem cell',
    'EFO:0004905': 'induced pluripotent stem cell', #subclass of CL:0000034
    'EFO:0002886': 'stem cell derived cell line' #subclass of CL:0000034
}

disease_slim_terms = {
    'MONDO:0005015': 'diabetes mellitus', #subclass of MONDO:0004335,MONDO:0005066
    'MONDO:0004335': 'digestive system disorder',
    'MONDO:0005066': 'metabolic disease',
    'MONDO:0002280': 'anemia',
    'MONDO:0005578': 'arthritic joint disease',
    'MONDO:0005113': 'bacterial infectious disease',
    'MONDO:0004992': 'cancer',
    'MONDO:0005044': 'hypertensive disorder',
    'MONDO:0005240': 'kidney disorder',
    'MONDO:0005084': 'mental disorder',
    'MONDO:0100081': 'sleep disorder',
    'MONDO:0007179': 'autoimmune disease'
}

development_slim_terms = {
    "HsapDv:0000002": "embryonic stage",
    "HsapDv:0000037": "fetal stage",
    "HsapDv:0000262": "newborn stage (0-28 days)",
    "HsapDv:0000260": "nursing stage (0-11 months)",
    "HsapDv:0000265": "child stage (1-4 yo)",
    "HsapDv:0000271": "juvenile stage (5-14 yo)",
    "HsapDv:0000258": "adult stage"
}

ethnicity_slim_terms = {
    "HANCESTRO:0009": "East Asian",
    "HANCESTRO:0006": "South Asian",
    "HANCESTRO:0007": "South East Asian",
    "HANCESTRO:0008": "Asian",
    "HANCESTRO:0005": "European",
    "HANCESTRO:0014": "Hispanic or Latin American",
    "HANCESTRO:0010": "African",
    "HANCESTRO:0017": "Oceanian",
    "HANCESTRO:0016": "African American or Afro-Caribbean",
    "HANCESTRO:0015": "Greater Middle Eastern (Middle Eastern, North African or Persian)",
    "HANCESTRO:0013": "Native American"
}

qa_slim_terms = {
    "CL:0000000": "cell",
    "EFO:0010183": "single cell library construction",
    'NCIT:C81239': 'Cause of Death',
    'NCIT:C7057': 'Disease, Disorder or Finding',
    'NCIT:C3394': 'Suicide',
    'NCIT:C28554': 'Dead'
}


@collection(
    name='ontology-terms',
    unique_key='ontology_term:name',
    properties={
        'title': 'Ontology term',
        'description': 'Ontology terms in the Lattice metadata.',
    })
class OntologyTerm(SharedItem):
    item_type = 'ontology_term'
    schema = load_schema('encoded:schemas/ontology_term.json')

    def unique_keys(self, properties):
        keys = super(OntologyTerm, self).unique_keys(properties)
        keys.setdefault('ontology_term:name', []).append(self.name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "description": "The name used for the system to identify this object.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def name(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        return properties['term_id'].replace(':', '_')


    @property
    def __name__(self):
        return self.name()


    @staticmethod
    def _get_ontology_slims(registry, term_id, slimTerms, list_ids=False):
        if term_id in registry['ontology']:
            ancestor_list = registry['ontology'][term_id]['ancestors']
            slims = []
            for slimTerm in slimTerms:
                if slimTerm in ancestor_list:
                    if list_ids:
                        slims.append(slimTerm)
                    else:
                        slims.append(slimTerms[slimTerm])
            if slims:
                return slims


    @calculated_property(condition='term_id', schema={
        "title": "Organ",
        "description": "The organs that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, organ_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "Cell",
        "description": "The cell types that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cell_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, cell_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "System slims",
        "description": "The biological systems that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, system_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "Disease slims",
        "description": "The diseases that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def disease_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, disease_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "Development slims",
        "description": "The development stages that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def development_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, development_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "Ethncitiy slims",
        "description": "The ethnicities that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def ethnicity_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, ethnicity_slim_terms, list_ids=True)


    @calculated_property(condition='term_id', schema={
        "title": "QA slims",
        "description": "The quality assurance-related slims that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def qa_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, qa_slim_terms)


    @calculated_property(condition='term_id', schema={
        "title": "Synonyms",
        "description": "The synonyms of this term, as listed by the ontology database.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_id):
        if term_id in registry['ontology']:
            syns = list(set(
                slim for slim in registry['ontology'][term_id]['synonyms']
            ))
            if syns:
                return syns


    @calculated_property(condition='term_id', schema={
        "title": "Ontology DB",
        "description": "The ontology database for which this term belongs.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def ontology_database(self, registry, term_id):
        return term_id.split(':')[0]

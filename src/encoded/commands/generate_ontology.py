import json
import requests

EPILOG = __doc__

# ont_dbs = ['UBERON', 'CL', 'EFO', 'MONDO', 'HANCESTRO']
ont_dbs = ['UBERON']


def pull_terms(obj, ancestors):
    for term in obj['_embedded']['terms']:
        term_id = term['obo_id']
        if term_id and term_id.split(':')[0] in ont_dbs:
            ancestors.append(term_id)


def get_ancs(ancs_url, ancestors):
    ancs_obj = requests.get(ancs_url).json()
    pull_terms(ancs_obj, ancestors)
    while ancs_obj['_links'].get('next'):
        ancs_url = ancs_obj['_links']['next']['href']
        ancs_obj = requests.get(ancs_url).json()
        pull_terms(ancs_obj, ancestors)


def process_terms(terms_obj, terms, db):
    for t in terms_obj['_embedded']['terms']:
        term_id = str(t['obo_id'])
        if term_id.split(':')[0] == db and t['is_defining_ontology'] == True:
            terms[term_id] = {}
            terms[term_id]['synonyms'] = t['synonyms']
            terms[term_id]['label'] = t['label']
            ancestors = [term_id]
            if t['_links'].get('hierarchicalAncestors'):
                get_ancs(t['_links']['hierarchicalAncestors']['href'], ancestors)
            terms[term_id]['ancestors'] = ancestors


def main():
    terms = {}
    for db in ont_dbs:
        terms_url = 'https://www.ebi.ac.uk/ols/api/ontologies/{}/terms?size=1000'.format(db.lower())
        terms_obj = requests.get(terms_url).json()
        process_terms(terms_obj, terms, db)
        while terms_obj['_links'].get('next'):
            terms_url = terms_obj['_links']['next']['href']
            terms_obj = requests.get(terms_url).json()
            process_terms(terms_obj, terms, db)


    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)


if __name__ == '__main__':
    main()

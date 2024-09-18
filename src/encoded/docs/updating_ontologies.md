Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use |
|:--|:--|:--|
| [Cell Ontology (CL)] | `cl.owl` from [CL] | v2024-08-16 |
| [Experimental Factor Ontology (EFO)] | `efo.owl` from [EFO] | v3.69.0 |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [HANCESTRO] | 3.0 |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [OLS-HsapDv] | 2024-05-28 |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | 2024-08-06 |
| [Uber-anatomy ontology (UBERON)] | `uberon.owl` from [UBERON] | v2024-08-07 |
| [NCI Thesaurus (NCIT)] | `ncit.owl` from [OLS-NCIT] | 2024-05-07 |

**Current ontology.json:** `ontology-2024-09-18.json`

How to update the ontology versions
---------------- 

1. Update the `*_url` variables in [generate_ontology.py] based on the corresponding .owl **Download** links found in the current [CELLxGENE schema]. NCIT is not a part of the CELLxGENE schema so use the version found at OLS, which will have a stable URL.

2. Run `python src/encoded/commands/generate_ontology.py` to generate a file named `ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/ --acl public-read`

4. Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5. Update the links for **File used**, **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://obophenotype.github.io/uberon/
[UBERON]: https://github.com/obophenotype/uberon/releases/tag/v2024-01-18
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[CL]: https://github.com/obophenotype/cell-ontology/releases/tag/v2024-01-04
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[EFO]: https://github.com/EBISPOT/efo/releases/tag/v3.62.0
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[MONDO]: https://github.com/monarch-initiative/mondo/releases/tag/v2024-01-03
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[HANCESTRO]: https://github.com/EBISPOT/hancestro/tree/2.6
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[OLS-HsapDv]: https://www.ebi.ac.uk/ols4/ontologies/hsapdv
[NCI Thesaurus (NCIT)]: https://github.com/NCI-Thesaurus/thesaurus-obo-edition
[OLS-NCIT]: https://www.ebi.ac.uk/ols4/ontologies/ncit
[generate_ontology.py]: ../commands/generate_ontology.py#L302
[CELLxGENE schema]: https://github.com/chanzuckerberg/single-cell-curation/tree/main/schema
[buildout.cfg]: ../../../buildout.cfg#L202

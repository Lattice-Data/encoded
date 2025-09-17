Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use |
|:--|:--|:--|
| [Cell Ontology (CL)] | `cl.owl` from [CL] | v2025-07-30 |
| [Experimental Factor Ontology (EFO)] | `efo.owl` from [EFO] | v3.82.0 |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [HANCESTRO] | v2025-04-01 |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [HsapDv] | v2025-01-23 |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | v2025-09-02 |
| [Uber-anatomy ontology (UBERON)] | `uberon.owl` from [UBERON] | v2025-08-15 |
| [NCI Thesaurus (NCIT)] | `ncit.owl` from [NCIT] | v2024-05-07 |

**Current ontology.json:** `ontology-2025-07-07.json`

How to update the ontology versions
---------------- 

1. Update the `*_url` variables in [generate_ontology.py] based on the corresponding .owl **Download** links found in the current [CELLxGENE schema].

2. Run `python src/encoded/commands/generate_ontology.py` to generate a file named `ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/ --acl public-read`

4. Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5. Update the links for **File used**, **Version in use** and **Current ontology.json:** above


[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[CL]: https://github.com/obophenotype/cell-ontology/releases/tag/v2025-07-30
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[EFO]: https://github.com/EBISPOT/efo/releases/tag/v3.82.0
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[HANCESTRO]: https://github.com/EBISPOT/hancestro/releases/tag/v2025-04-01
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[HsapDv]: https://github.com/obophenotype/developmental-stage-ontologies/releases/tag/v2025-01-23
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[MONDO]: https://github.com/monarch-initiative/mondo/releases/tag/v2025-09-02
[Uber-anatomy ontology (UBERON)]: http://obophenotype.github.io/uberon/
[UBERON]: https://github.com/obophenotype/uberon/releases/tag/v2025-08-15
[NCI Thesaurus (NCIT)]: https://github.com/NCI-Thesaurus/thesaurus-obo-edition
[NCIT]: https://github.com/NCI-Thesaurus/thesaurus-obo-edition/releases/tag/v2024-05-07
[generate_ontology.py]: ../commands/generate_ontology.py#L302
[CELLxGENE schema]: https://github.com/chanzuckerberg/single-cell-curation/tree/main/schema
[buildout.cfg]: ../../../buildout.cfg#L202

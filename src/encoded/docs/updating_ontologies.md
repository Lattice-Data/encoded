Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use |
|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `uberon.owl` from [UBERON] | 2023-06-28 |
| [Cell Ontology (CL)] | `cl.owl` from [CL] | 2023-06-22 |
| [Experimental Factor Ontology (EFO)] | `efo.owl` from [EFO] | 3.56.0 |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | 2023-07-03 |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [HANCESTRO] | 2023-07-08 |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [OLS-HsapDv] | 2020-03-10 |
| [Mouse Developmental Stage Ontology (MmusDv)] | `mmusdv.owl` from [OLS-MmusDv] | 2020-03-10 |
| [NCI Thesaurus (NCIT)] | `ncit.owl` from [OLS-NCIT] | 2022-08-19 |

**Current ontology.json:** `ontology-2023-08-15.json`

How to update the ontology versions
---------------- 

1. Update the `*_url` variables in `src/encoded/commands/generate_ontology.py` (starting Ln302) based on corresponding .owl **Download** links found in the [current CELLxGENE schema]. NCIT is not a part of the CELLxGENE schema so use the version found at OLS, which will have a stable URL.

2. Run `python src/encoded/commands/generate_ontology.py` to generate a file named `ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/ --acl public-read`

4. Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5. Update the **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://uberon.org
[UBERON]: https://github.com/obophenotype/uberon/releases/tag/v2023-06-28
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[CL]: https://github.com/obophenotype/cell-ontology/releases/tag/v2023-06-22
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[EFO]: https://github.com/EBISPOT/efo/releases/tag/v3.56.0
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[MONDO]: https://github.com/monarch-initiative/mondo/releases/tag/v2023-07-03
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[HANCESTRO]: https://github.com/EBISPOT/hancestro/tree/2.6
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[OLS-HsapDv]: https://www.ebi.ac.uk/ols4/ontologies/hsapdv
[Mouse Developmental Stage Ontology (MmusDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv
[OLS-MmusDv]: https://www.ebi.ac.uk/ols4/ontologies/mmusdv
[NCI Thesaurus (NCIT)]: https://github.com/NCI-Thesaurus/thesaurus-obo-edition
[OLS-NCIT]: https://www.ebi.ac.uk/ols4/ontologies/ncit
[CELLxGENE schema]: https://github.com/chanzuckerberg/single-cell-curation/tree/main/schema
[buildout.cfg]: ../../../buildout.cfg

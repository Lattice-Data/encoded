Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use |
|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `uberon.owl` from [OLS-UBERON] | 2023-04-19 |
| [Cell Ontology (CL)] | `cl.ow` from [OLS-CL] | 2023-04-20 |
| [Experimental Factor Ontology (EFO)] | `efo.owl` from [OLS-EFO] | 3.54.0 |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [OLS-MONDO] | 2023-05-01 |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [OLS-HANCESTRO] | 2023-02-16 |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [OLS-HsapDv] | 2020-03-10 |
| [Mouse Developmental Stage Ontology (MmusDv)] | `mmusdv.owl` from [OLS-MmusDv] | 2020-03-10 |
| [NCI Thesaurus (NCIT)] | `ncit.owl` from [OLS-NCIT] | 2022-08-19 |

**Current ontology.json:** `ontology-2023-05-17.json`

How to update the ontology versions
---------------- 

1. Run src/encoded/commands/generate_ontology.py to generate a file named `ontology-YYYY-MM-DD.json`

2. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/ --acl public-read`

3.  Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

4.  Update the **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://uberon.org
[OLS-UBERON]: https://www.ebi.ac.uk/ols4/ontologies/uberon
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[OLS-CL]: https://www.ebi.ac.uk/ols4/ontologies/cl
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[OLS-EFO]: https://www.ebi.ac.uk/ols4/ontologies/efo
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[OLS-MONDO]: https://www.ebi.ac.uk/ols4/ontologies/mondo
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[OLS-HANCESTRO]: https://www.ebi.ac.uk/ols4/ontologies/hancestro
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[OLS-HsapDv]: https://www.ebi.ac.uk/ols4/ontologies/hsapdv
[Mouse Developmental Stage Ontology (MmusDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv
[OLS-MmusDv]: https://www.ebi.ac.uk/ols4/ontologies/mmusdv
[NCI Thesaurus (NCIT)]: https://github.com/NCI-Thesaurus/thesaurus-obo-edition
[OLS-NCIT]: https://www.ebi.ac.uk/ols4/ontologies/ncit
[buildout.cfg]: ../../../buildout.cfg

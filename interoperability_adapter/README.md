# SEC POC Interoperability Adapter

WARNING: INCOMPLETE WORK-IN-PROGRESS CODE

The name "Interoperability Adapter" seems to have stuck, even though I'm not sure that is the best architecture.  The original idea was to have a proxy in front of the CTS API that passed through requests that the latter currently supports, but decorates the API with new functionality.  This new functionality would be taking EHR data in FHIR format and using that to find matching trials.  It may just end up being a standalone server, with its own simple API, that calls the CTS API behind the scenes.

The hardest part of this project is to map different medical ontologies and coding systems onto the NCI Thesaurus.  My initial attempt at this was going to use [NLM UMLS](https://www.nlm.nih.gov/research/umls/index.html) but another approach would be to use machine learning and/or LLMs.

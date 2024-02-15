# Synthea Synthetic Cancer Patient Generation

A hodgepodge of scripts related to generating synthetic patient data using the [Synthea](https://github.com/synthetichealth/synthea) tool.

[synthea_gen](synthea_gen): wrapper scripts for running Synthea and pulling out patient cohorts with specific types of cancer.

[lfh_fhir](lfh_fhir): a docker image for the [Linux for Health FHIR Server](https://linuxforhealth.github.io/FHIR/) and associated scripts.

[fhir_etl](fhir_etl): ETL that pulls out certain cancer-relevant data from a patient's FHIR bundle and prepares it for display in the SEC POC admin app.  Should probably live in the [sec_poc_admin repo](https://github.com/CBIIT/sec_admin/) instead, or just get deleted and replaced by a better visualization tool.

[interoperability_adapter](interoperability_adapter): a work-in-progress that should probably live in its own repo.  See the README in that directory.

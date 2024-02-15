# Synthea patient generation

1. Have a look at https://github.com/synthetichealth/synthea/wiki/Basic-Setup-and-Running and download the .jar file referred to there.

2. Customize the synthea.properties and arguments in the run.sh script, if desired.

3. ./run.sh

4. ./postprocess.sh to select patients having certain cancers.

5. ./load_fhir.sh to load the patients from step #4 into a FHIR server.

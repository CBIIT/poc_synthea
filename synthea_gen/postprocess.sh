#!/bin/bash

for F in `\ls output/fhir/*.json`
do
    egrep -li -e 162573006 -e 254637007 -e 424132000 $F > /dev/null
    if [ $? -eq 0 ]
    then
        ls -lah $F
    fi
done

# For example
#curl -X POST -H 'Content-Type: application/fhir+json' -H 'Accept: application/fhir+json' -k -i -u 'fhiruser:test' 'https://localhost:9443/fhir-server/api/v4/Bundle' -d @output/fhir/Calvin845_Feest103_d05d14b6-f991-e75a-a1fe-33d6a789892c.json

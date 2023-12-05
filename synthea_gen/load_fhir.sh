#!/bin/bash
#
# Loads FHIR Bundles (generated by Synthea) into a local FHIR server.

set -e

for F in `\ls selected/*.json`
do
    echo $F
    curl --fail-with-body -X POST -H 'Content-Type: application/fhir+json' -H 'Accept: application/fhir+json' -k -i -u 'fhiruser:test' 'https://localhost:9443/fhir-server/api/v4/Bundle' -d @$F
done

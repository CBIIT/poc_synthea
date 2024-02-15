#!/bin/bash

set -e

docker build -t sec_poc/fhir .
docker run -v ~/Dev/CTRP/poc_synthea/docker/config:/opt/LFH_FHIR/wlp/usr/servers/defaultServer/configDropins/defaults -p 9443:9443 sec_poc/fhir

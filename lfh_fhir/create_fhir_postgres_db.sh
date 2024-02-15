#!/bin/bash

set -e

#psql postgres -c "create user fhirserver with password 'test'"
psql postgres -c "create database fhirdb"
psql postgres -c "grant all privileges on database fhirdb to fhirserver"
java -jar fhir-persistence-schema-5.1.1-cli.jar --db-type postgresql --prop-file postgres.properties --schema-name fhirdata --create-schemas
java -jar fhir-persistence-schema-5.1.1-cli.jar --db-type postgresql --prop-file postgres.properties --schema-name fhirdata --update-schema --grant-to fhirserver --pool-size 1

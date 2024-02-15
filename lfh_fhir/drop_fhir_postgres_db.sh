# DIDN'T WORK
#java -jar fhir-persistence-schema-5.1.1-cli.jar --db-type postgresql --prop-file postgres.properties --schema-name fhirdata --drop-schema-fhir --confirm-drop
psql postgres -c "drop database fhirdb"

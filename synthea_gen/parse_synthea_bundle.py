#!/usr/bin/python3

import datetime
import json
import sys


def print_condition(condition):
    date = condition["recordedDate"][:10]
    clinical_status = condition["clinicalStatus"]["coding"][0]["code"]
#    verification_status = condition["verificationStatus"]["coding"][0]["code"]
#    category = condition["category"][0]["coding"][0]["code"]
    if condition["code"]["coding"][0]["system"] == "http://snomed.info/sct":
        code = "SNOMED CT " + condition["code"]["coding"][0]["code"]
    else:
        code = "%s (%s)" % (condition["code"]["coding"][0]["code"], condition["code"]["coding"][0]["system"])
    name = condition["code"]["coding"][0]["display"]

    print("%s %s, %s, %s" % (date, name, code, clinical_status))



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_synthe_bundle.py <synthea_bundle.json>", file=sys. stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        parsed = json.load(f)

    patient = parsed["entry"][0]["resource"]
    patient_id = patient["id"]
    gender = patient["gender"]
    name = "%s %s" % (patient["name"][0]["given"][0], patient["name"][0]["family"])
    dob = patient["birthDate"]
    parsed_dob = datetime.datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.date.today()
    age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
    marital_status = patient["maritalStatus"]["text"]
    extensions = patient["extension"]
    for extension in extensions:
        if extension["url"] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
            race = extension["extension"][0]["valueCoding"]["display"]
        elif extension["url"] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
            ethnicity = extension["extension"][0]["valueCoding"]["display"]

    print("%s, ID %s" % (name, patient_id))
    print("DOB %s, age %d, %s, %s" % (dob, age, gender, marital_status))
    print("%s, %s" % (race, ethnicity))
    print()

    for resource in parsed["entry"]:
        if resource["resource"]["resourceType"] == "Condition":
            print_condition(resource["resource"])

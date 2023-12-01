#!/usr/bin/python3

import argparse
import datetime
import psycopg2
import requests


CANCER_SNOMED_CODES = {
        "162573006",  # lung cancer
        "254637007",  # lung cancer
        "424132000",  # lung cancer
        "254837009",  # breast cancer
        }


CANCER_TERMS = (
        "cancer",
        "neoplasm",
        "malignan",
        "metast",
        "her2",
        )


def process_patient(cursor, patient):
    patient_id = patient["id"]
    gender = patient["gender"].lower() == "female" and "F" or "M"
    name = "%s %s" % (patient["name"][0]["given"][0], patient["name"][0]["family"])
    dob = patient["birthDate"]
    parsed_dob = datetime.datetime.strptime(dob, "%Y-%m-%d")
#    today = datetime.date.today()
#    age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
    marital_status_s = patient["maritalStatus"]["text"].lower()
    if marital_status_s == "never married":
        marital_status = "S"
    elif marital_status_s == "married":
        marital_status = "M"
    else:
        marital_status = "D"
    extensions = patient["extension"]
    for extension in extensions:
        if extension["url"] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
            race = extension["extension"][0]["valueCoding"]["display"]
        elif extension["url"] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
            ethnicity = extension["extension"][0]["valueCoding"]["display"]

#    print("%s, ID %s" % (name, patient_id))
#    print("DOB %s, age %d, %s, %s" % (dob, age, gender, marital_status))
#    print("%s, %s" % (race, ethnicity))
#    print()

    print("%s: %s" % (patient_id, name))

    cursor.execute("""insert into patient(fhir_id, name, gender, dob, marital_status, race, ethnicity)
                    values(%s, %s, %s, %s, %s, %s, %s) returning id""",
                    (patient_id, name, gender, parsed_dob, marital_status, race, ethnicity))

    return cursor.fetchone()[0]


def is_cancer_related(code, code_scheme, name):
    if code_scheme == "http://snomed.info/sct" and code in CANCER_SNOMED_CODES:
        return True
    else:
        for term in CANCER_TERMS:
            if name.lower().find(term) >= 0:
                return True
    return False


def process_condition(cursor, patient_id, condition):
    date = datetime.datetime.fromisoformat(condition["recordedDate"])
    clinical_status = condition["clinicalStatus"]["coding"][0]["code"]
#    verification_status = condition["verificationStatus"]["coding"][0]["code"]
#    category = condition["category"][0]["coding"][0]["code"]
    code = condition["code"]["coding"][0]["code"]
    code_scheme = condition["code"]["coding"][0]["system"]
    name = condition["code"]["coding"][0]["display"]
    cancer_related = is_cancer_related(code, code_scheme, name)

    cursor.execute("""insert into condition(patient_id, name, condition_date, code, code_scheme, clinical_status, cancer_related)
            values(%s, %s, %s, %s, %s, %s, %s)""", (patient_id, name, date, code, code_scheme, clinical_status, cancer_related))


def process_observation(cursor, patient_id, observation):
    date = datetime.datetime.fromisoformat(observation["effectiveDateTime"])
    category = observation["category"][0]["coding"][0]["code"]
    code = observation["code"]["coding"][0]["code"]
    code_scheme = observation["code"]["coding"][0]["system"]
    display = observation["code"]["coding"][0]["display"]
    value = None
    unit = None
    if "valueQuantity" in observation:
        value = observation["valueQuantity"]["value"]
        unit = observation["valueQuantity"]["unit"]
    cancer_related = is_cancer_related(code, code_scheme, display)

    cursor.execute("""insert into observation(patient_id, observation_date, category, code, code_scheme, display,
            value, unit, cancer_related)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (patient_id, date, category, code, code_scheme, display, value, unit, cancer_related))


def process_procedure(cursor, patient_id, procedure):
    date = datetime.datetime.fromisoformat(procedure["performedPeriod"]["end"])
    code = procedure["code"]["coding"][0]["code"]
    code_scheme = procedure["code"]["coding"][0]["system"]
    display = procedure["code"]["coding"][0]["display"]
    cancer_related = is_cancer_related(code, code_scheme, display)

    cursor.execute("""insert into procedure(patient_id, procedure_date, code, code_scheme, display, cancer_related)
            values(%s, %s, %s, %s, %s, %s)""", (patient_id, date, code, code_scheme, display, cancer_related))


def process_bundle(conn, bundle):
    entries = bundle["entry"]
    print("    Processing %d entries in Bundle..." % len(entries))
    with conn:
        with conn.cursor() as cursor:
            patient_id = None
            for resource_r in entries:
                resource = resource_r["resource"]
                if resource["resourceType"] == "Patient":
                    patient_id = process_patient(cursor, resource)
                elif patient_id:
                    if resource["resourceType"] == "Condition":
                        process_condition(cursor, patient_id, resource)
                    elif resource["resourceType"] == "Observation":
                        process_observation(cursor, patient_id, resource)
                    elif resource["resourceType"] == "Procedure":
                        process_procedure(cursor, patient_id, resource)


def parse_args():
    parser = argparse.ArgumentParser(description="Retrieves Bundle resources from FHIR server, and loads into DB tables")
    parser.add_argument("--db_host", type=str, default="localhost", help="Source postgres DB host")
    parser.add_argument("--db_port", type=int, default=5432, help="Source postgres DB port")
    parser.add_argument("--db_name", type=str, default="fhir_etl", help="Source postgres DB name")
    parser.add_argument("--db_user", type=str, default="secapp", help="Source postgres username")
    parser.add_argument("--db_password", type=str, default="", help="Source postgres username")
    parser.add_argument("--fhir_server", type=str, default="https://localhost:9443/fhir-server/api/v4", help="FHIR server URL")
    parser.add_argument("--fhir_user", type=str, default="fhiruser", help="FHIR server user")
    parser.add_argument("--fhir_password", type=str, required=True, help="FHIR server password")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    conn = psycopg2.connect(host=args.db_host, port=args.db_port, database=args.db_name, user=args.db_user,
            password=args.db_password)

    count = 0
    url = args.fhir_server + "/Bundle"
    while url:
        print("Making request to FHIR server (%s)..." % url)
        response = requests.get(url, auth=(args.fhir_user, args.fhir_password), verify=False)
        if not str(response.status_code).startswith("20"):
            raise RuntimeError("FHIR server returned code %d\n\n%s" % (response.status_code, response.text))

        response_j = response.json()

        # paging
        url = None
        for link in response_j["link"]:
            if link["relation"] == "next":
                url = link["url"]

        bundles = response_j["entry"]
        print("Processing %d bundles..." % len(bundles))
        for bundle_r in bundles:
            bundle = bundle_r["resource"]
            assert bundle["resourceType"] == "Bundle"
            process_bundle(conn, bundle)
            count += 1

    print("Loaded %d Bundles." % count)

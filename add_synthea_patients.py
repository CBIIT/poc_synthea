import argparse
import datetime
import os
import psycopg2
import requests

from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.patient import Patient


IDENTIFIER_TEMPLATE = {"use": "usual", "system": "https://github.com/synthetichealth/synthea"}

HEADERS = {"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}


def create_patient(ptnum, gender, birth_date, marital_status):
    identifier = IDENTIFIER_TEMPLATE.copy()
    identifier["value"] = ptnum
    m_text = marital_status == "m" and "Married" or "Never Married"
    m_coding = Coding(system="http://hl7.org/fhir/ValueSet/marital-status", code=marital_status.upper(), display=m_text)
    m_status = CodeableConcept(coding=[m_coding], text=m_text)
    return Patient(id=ptnum, identifier=[identifier], active=True, gender=gender, birthDate=birth_date,
            deceasedBoolean=False, maritalStatus=m_status)


def query_patients(cursor):
    sql = """select ptnum, raw_concept_code, raw_value
            from testdata.synthea_test_data
            where raw_concept_code in ('C-125680007', 'C-424144002', 'C-263495000')
            order by ptnum;"""
    cursor.execute(sql)
    last_ptnum = None
    marital_status = None
    birth_date = None
    gender = None
    results = []
    for row in cursor.fetchall():
        ptnum = row[0]
        if ptnum != last_ptnum:
            if last_ptnum:
                results.append(create_patient(last_ptnum, gender, birth_date, marital_status))
            last_ptnum = ptnum
            
        if row[1] == "C-125680007":
            marital_status = row[2]
        elif row[1] == "C-424144002":
            birth_date = datetime.date.today() - relativedelta(years=float(row[2]))
        else:
            gender = row[2] == "m" and "male" or "female"
    results.append(create_patient(last_ptnum, gender, birth_date, marital_status))

    return results


def create_patient_in_fhir(fhir_server, fhir_auth, patient):
    url = "%s/Patient/%s" % (fhir_server, patients[i].identifier[0].value)

    # Use PUT so we can assign the id instead of having the server do it.
    response = requests.put(url, data=patient.json(), headers=HEADERS, auth=fhir_auth, verify=False)
    if not str(response.status_code).startswith("20"):
        raise RuntimeError("FHIR server returned response code %d\n\n%s" % (response.status_code, response.text))
    print(response.text)


def parse_args():
    parser = argparse.ArgumentParser(description="Adds synthea patient info to FHIR server")
    parser.add_argument("--db_host", type=str, required=True, help="DB host")
    parser.add_argument("--db_port", type=int, default=5432, help="DB port")
    parser.add_argument("--db_name", type=str, default="sec", help="DB name")
    parser.add_argument("--db_user", type=str, default="secapp", help="DB user")
    parser.add_argument("--fhir_server", type=str, default="https://localhost:9443/fhir-server/api/v4",
            help="Base URL of FHIR server")
    parser.add_argument("--fhir_user", type=str, default="fhiruser", help="Username for FHIR server")
    parser.add_argument("--limit", type=int, default=65536, help="If specified, only this many patients will be populated")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_pw = os.environ.get("DB_PASSWD")
    fhir_pw = os.environ.get("FHIR_PASSWD")
    fhir_auth = HTTPBasicAuth(args.fhir_user, fhir_pw)
    conn = psycopg2.connect(host=args.db_host, port=args.db_port, database=args.db_name, user=args.db_user, password=db_pw)
    cursor = conn.cursor()

    patients = query_patients(cursor)
    i = 0
    while i < args.limit and i < len(patients):
        print(patients[i].json())
        print()
        create_patient_in_fhir(args.fhir_server, fhir_auth, patients[i])
        i += 1


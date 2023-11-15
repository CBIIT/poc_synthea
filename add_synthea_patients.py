import argparse
import datetime
import os
import psycopg2

from dateutil.relativedelta import relativedelta

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.patient import Patient


IDENTIFIER_TEMPLATE = {"use": "usual", "system": "https://github.com/synthetichealth/synthea"}


def create_patient(ptnum, gender, birth_date, marital_status):
    identifier = IDENTIFIER_TEMPLATE.copy()
    identifier["value"] = ptnum
    m_text = marital_status == "m" and "Married" or "Never Married"
    m_coding = Coding(system="http://hl7.org/fhir/ValueSet/marital-status", code=marital_status.upper(), display=m_text)
    m_status = CodeableConcept(coding=[m_coding], text=m_text)
    return Patient(identifier=[identifier], active=True, gender=gender, birthDate=birth_date,
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


def parse_args():
    parser = argparse.ArgumentParser(description="Adds synthea patient info to FHIR server")
    parser.add_argument("--db_host", type=str, required=True, help="DB host")
    parser.add_argument("--db_port", type=int, default=5432, help="DB port")
    parser.add_argument("--db_name", type=str, default="sec", help="DB name")
    parser.add_argument("--db_user", type=str, default="secapp", help="DB user")
    parser.add_argument("--limit", type=int, default=65536, help="If specified, only this many patients will be populated")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_pw = os.environ.get("DB_PASSWD")
    conn = psycopg2.connect(host=args.db_host, port=args.db_port, database=args.db_name, user=args.db_user, password=db_pw)
    cursor = conn.cursor()

    patients = query_patients(cursor)
    i = 0
    while i < args.limit and i < len(patients):
        print(patients[i].json())
        i += 1


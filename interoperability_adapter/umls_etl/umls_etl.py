'''Extracts information about the NCI thesaurus and other ontologies from the
UMLS DB, and saves to another, more aggregated DB.

Currently, the UMLS DB is MySQL and the other DB is Postgres.
'''
import argparse
import collections
import mysql.connector
import os
import psycopg2
import psycopg2.extras
import sys


def populate_ncit(umls_cursor, sec_cursor, delete):
    if delete:
        sec_cursor.execute("delete from co.umls_ncit")

    inserted = 0

    def save(row):
        sql = "insert into co.umls_ncit(umls_cui, is_umls_preferred, ncit_code, is_ncit_preferred) values(%s, %s, %s, %s)"
        is_umls_preferred = row[3] == 'P' or row[4] == 'Y'
        is_ncit_preferred = row[2].startswith('PT')
        sec_cursor.execute(sql, (row[1], is_umls_preferred, row[0], is_ncit_preferred))
        inserted += 1

    umls_cursor.execute("select code, cui, tty, ts, ispref from mrconso where sab='NCI' order by code, cui")
    last_row = [None, None, None, None]
    for row in umls_cursor.fetchall():
        if row[0] != last_row[0] or row[1] != last_row[1]:  # different code or cui
            if last_row[0] and last_row[1]:
                save(last_row)
            last_row = row

    if row[0] != last_row[0] or row[1] != last_row[1]:
        save(last_row)

    print('Inserted %d rows into umls_ncit.' % inserted)


def populate_other(code_scheme, umls_cursor, sec_cursor, delete):
    umls_cursor.execute("select code, cui, tty, ts, ispref from mrconso where sab='SNOMEDCT_US' and lat='ENG'")
    cui_to_snomed = collections.defaultdict(set)
    for row in umls_cursor.fetchall():
        cui_to_snomed[row[1]].add(row[0])
    cuis_with_multiple_snomeds = 0
    cuis_with_no_snomeds = 0
    total_cuis = 0
    for _, sno_set in cui_to_snomed.items():
        total_cuis += 1
        if len(sno_set) > 1:
            cuis_with_multiple_snomeds += 1
        elif not sno_set:
            cuis_with_no_snomeds += 1
    print('%d total cuis (for SNOMEDCT_US rows); %d have no snomed code; %d have more than 1 snomed codes' % (total_cuis, cuis_with_no_snomeds, cuis_with_multiple_snomeds))


def parse_args():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('--sec_db_host', type=str, default='localhost', help='postgres DB host')
    parser.add_argument('--sec_db_port', type=int, default=5432, help='ostgres DB port')
    parser.add_argument('--sec_db_name', type=str, default='sec', help='postgres DB name')
    parser.add_argument('--sec_db_user', type=str, default='secapp', help='postgres username')
    parser.add_argument('--umls_db_host', type=str, default='localhost', help='postgres DB host')
    parser.add_argument('--umls_db_name', type=str, default='umls', help='postgres DB name')
    parser.add_argument('--umls_db_user', type=str, default='umls', help='postgres username')
    parser.add_argument('--code_scheme', type=str, default='SNOMEDCT_US', help='Ontology to import')
    parser.add_argument('--delete', action=argparse.BooleanOptionalAction,
            help='If present, rows will be deleted first')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    sec_pw = os.environ.get('SEC_DB_PASSWORD')
    umls_pw = os.environ.get('UMLS_DB_PASSWORD')
    if sec_pw is None or not umls_pw:
        print("Must specify DB passwords with SEC_DB_PASSWORD and UMLS_DB_PASSWORD environment variables", file=sys. stderr)
        sys.exit(1)

    umls_conn = mysql.connector.connect(host=args.umls_db_host, user=args.umls_db_user, password=umls_pw, database=args.umls_db_name)
    umls_cursor = umls_conn.cursor()
    with psycopg2.connect(host=args.sec_db_host, port=args.sec_db_port, database=args.sec_db_name, user=args.sec_db_user,
                          password=sec_pw) as sec_conn:
        with sec_conn.cursor() as sec_cursor:
            populate_ncit(umls_cursor, sec_cursor, args.delete)
#            populate_other(args.code_scheme, umls_cursor, sec_cursor, args.delete)

    umls_conn.close()

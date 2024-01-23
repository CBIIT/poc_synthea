'''Loads the NLM Unified Medical Language System (UMLS) MRCONSO.RRF file,
looks for codes matching a given scheme, and loads the corresponding
NCIT (NCI Thesaurus) matching those terms into a relational table.

TODO: use temporary tables if this in-memory approach hits limits.
'''

import argparse
import collections
import psycopg2
import psycopg2.extras


def remove_dups(field_dict):
    result = {}
    for umls_id, field_list in field_dict.items():
        final_list = []
        if len(field_list) == 1:
            final_list.append((field_list[0][13], field_list[0][14]))
        else:

            # I'm not sure how important this really is, since the code's I've
            # looked at that are cancer-related always have exactly one PT (field 12)
            # row, but there are definitely other instances where there are dups.
            has_both = []
            has_one = []
            for fields in field_list:
                if fields[6] == 'Y' and fields[2] == 'P':
                    has_both.append((fields[13], fields[14]))
                elif fields[6] == 'Y' or fields[2] == 'P':
                    has_one.append((fields[13], fields[14]))
            if has_both:
                final_list.extend(has_both)
            elif has_one:
                final_list.extend(has_one)
            else:
                final_list.append((field_list[0][13], field_list[0][14]))  # default to the first in the file
        result[umls_id] = final_list

    return result


def read_file(umls_file, code_scheme):
    ncit_entries = collections.defaultdict(list)
    other_entries = collections.defaultdict(list)
    print('Reading %s...' % args.umls_file)
    total_lines = 0
    with open(args.umls_file) as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            fields = line.split('|')
            if len(fields) >= 15:
                if fields[11] == code_scheme or fields[11] == 'NCI':
                    if fields[1] == 'ENG':
                        if fields[12] == 'PT':  # Preferred term, as opposed to synonym
                            umls_id = fields[0]
                            code = fields[13]
                            if fields[11] == args.code_scheme:
                                other_entries[umls_id].append(fields)
                            elif fields[11] == 'NCI':
                                ncit_entries[umls_id].append(fields)

    print('Removing duplicates...')
    ncit_entries = remove_dups(ncit_entries)
    other_entries = remove_dups(other_entries)

    print('Processed %d lines in file.  %d NCIT entries, %d %s entries.'
            % (total_lines, len(ncit_entries), len(other_entries), code_scheme))
    return ncit_entries, other_entries


def parse_args():
    parser = argparse.ArgumentParser(description='Loads the MRCONSO.RRF UMLS file')
    parser.add_argument('--umls_file', type=str, default='MRCONSO.RRF', help='MRCONSO.RRF file location')
    parser.add_argument('--db_host', type=str, default='localhost', help='postgres DB host')
    parser.add_argument('--db_port', type=int, default=5432, help='ostgres DB port')
    parser.add_argument('--db_name', type=str, default='sec', help='postgres DB name')
    parser.add_argument('--db_user', type=str, default='secapp', help='postgres username')

    # TODO: add DB password.

    parser.add_argument('--code_scheme', type=str, default='SNOMEDCT_US', help='Ontology to import and convert to NCIT')
    parser.add_argument("--delete", action=argparse.BooleanOptionalAction,
            help='If present, other code scheme rows will be deleted first')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    ncit_entries, other_entries = read_file(args.umls_file, args.code_scheme)

    ncit_total = len(ncit_entries)
    with_dups = 0
    insert_tuples = []
    for umls_code, ncit_values in ncit_entries.items():
        for ncit_value in ncit_values:
            if umls_code in other_entries:
                ncit_total -= 1
                if len(other_entries[umls_code]) > 1:
                    with_dups += 1
                for other_value in other_entries[umls_code]:
                    insert_tuples.append((ncit_value[0], umls_code, other_value[0], other_value[1], args.code_scheme))
                del(other_entries[umls_code])

    print('%d NCIT codes not found in %s; %d %s codes not found in NCIT; %d NCIT codes have %s duplicates.'
            % (ncit_total, args.code_scheme, len(other_entries), args.code_scheme, with_dups, args.code_scheme))

    print('Inserting %d rows into DB...' % len(insert_tuples))
    with psycopg2.connect(host=args.db_host, port=args.db_port, database=args.db_name, user=args.db_user,
            password='') as conn:
        with conn.cursor() as cursor:
            if args.delete:
                cursor.execute("delete from jcallaway.umls_to_ncit where other_scheme = %s", (args.code_scheme,))
            sql = """insert into jcallaway.umls_to_ncit(ncit_code, umls_code, other_code, other_description, other_scheme)
                    values(%s, %s, %s, %s, %s)"""
            psycopg2.extras.execute_batch(cursor, sql, insert_tuples)
    print('Done.')

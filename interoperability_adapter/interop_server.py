'''Server that consumes FHIR Bundles and matches the patient's data with clinical trials.
'''
import argparse
import flask
import os
import sys

from fhir.resources.bundle import Bundle
from flask import request

import trial_search


app = flask.Flask(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('--db_host', type=str, default='localhost', help='postgres DB host')
    parser.add_argument('--db_port', type=int, default=5432, help='postgres DB port')
    parser.add_argument('--db_name', type=str, default='sec', help='postgres DB name')
    parser.add_argument('--db_user', type=str, default='secapp', help='postgres username')
    parser.add_argument('--db_password', type=str, default='', help='postgres password')
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    postgres_pw = os.environ.get("DB_PASSWD")
    if postgres_pw is None:
        print('Postgres DB password must be provided as DB_PASSWD', file=sys.stderr)
        sys.exit(1)

    search = trial_search.TrialSearch(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)

    @app.post('/')
    def consume_bundle():
        bundle = Bundle(request.json)
        trials = search.search(bundle)
        return({'num': len(trials), 'trials': trials})

    app.config.update(dict(DEBUG=args.debug))
    app.run(host='127.0.0.1', port=5000, threaded=False)

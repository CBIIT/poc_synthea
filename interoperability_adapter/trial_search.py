
import datetime
import psycopg2
import requests


CANCER_TERMS = (
        "cancer",
        "neoplasm",
        "malignan",
        "metast",
        "tumor",
        )


class TrialSearch:
    '''
    Class that encapsulates the matching logic.
    '''

#    def __init__(self, db_host, db_port, db_name, db_user, db_password):
    def __init__(self, cts_api_key):
#        conn = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_password)
#        self._cursor = conn.cursor()
        self._cts_headers = {
                'Accept': 'application/json',
                'x-api-key': cts_api_key,
                }


    def _parse_patient(self, patient):
        dob = patient.birthDate.isostring
        parsed_dob = datetime.datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.date.today()
        age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
        return age, patient.gender, ''


    def _convert_snomed_to_ncit(self, code):
        '''
        TODO: this table does not appear to work correctly.
        converted = set()
        for snomed_code in codes:
            self._cursor.execute("select cui from umls.mrconso where code = %s and tty = 'PT' and sab = 'SNOMEDCT_US'",
                    (snomed_code,))
            rows = self._cursor.fetchall()
            if len(rows) != 1:
                raise RuntimeError('Expected one mrconso row for SNOMET CT %s, got %d' % (snomed_code, len(rows)))
            converted.add(rows[0][0])
        return converted
        '''
        assert code == '254837009', code
        return 'C9335'


    def _get_cancer_diagnoses(self, fhir_bundle):
        '''Returns the first and last cancer-related diagnoses, if present, for the given patient.
        '''
        dates_and_codes = []
        for entry in fhir_bundle.entry:
            resource = entry.resource
            if resource.resource_type == 'Condition':
                if resource.category[0].coding[0].code == 'encounter-diagnosis':
                    assert resource.code.coding[0].system == 'http://snomed.info/sct'
                    for term in CANCER_TERMS:
                        if resource.code.coding[0].display.lower().find(term) >= 0:
                            '''
                            print()
                            import json
                            print(json.dumps(resource.as_json(), indent=4))
                            print()
                            '''
                            dates_and_codes.append((resource.code.coding[0].code, resource.recordedDate.isostring))

        # Sort ascending by date
        dates_and_codes.sort(key=lambda x: datetime.datetime.fromisoformat(x[1]).timestamp())

        first = dates_and_codes[0]
        first_idx = 0
        last_idx = len(dates_and_codes) - 1
        last = dates_and_codes[last_idx]
        
        # There are often duplicates for diagnosis codes, for some reason.
        while first[0] == last[0] and last_idx >= 1:
            last_idx -= 1
            last = dates_and_codes[last_idx]


        if first[0] == last[0]:
            codes = [dates_and_codes[0]]
        else:
            codes = [first[0], last[0]]
        return [self._convert_snomed_to_ncit(code[0]) for code in codes]


    def _get_trials_for_diseases(self, gender, age, disease_codes):
        start = 0
        total = -1
        total_retrieved = 0
        trials = []
        while start == 0 or (total_retrieved < total):
            params = {
                    'current_trial_status': 'Active',
                    'primary_purpose': ['TREATMENT', 'SCREENING'],
                    'eligibility.structured.min_age_in_years_lte': age,
                    'eligibility.structured.max_age_in_years_gte': age,
                    'eligibility.structured.gender': ['BOTH', gender.upper()],
                    'diseases.nci_thesaurus_concept_id': disease_codes,
                    'size': 50,
                    'from': start,
                    }
            print('Calling CTS API, offset %d (%d total)...' % (start, total))
            response = requests.get('https://clinicaltrialsapi.cancer.gov/api/v2/trials', params=params,
                    headers=self._cts_headers)
            if response.status_code != 200:
                raise RuntimeError('Received %d from CTS API:\n%s' % (response.status_code, response.text))
            start += 50
            data = response.json()
            if total == -1:
                total = data['total']
            total_retrieved += len(data['data'])
            trials.extend(data['data'])

        print('Fetched %d trials total' % len(trials))
        return trials


    def search(self, fhir_bundle):
        disease_codes = self._get_cancer_diagnoses(fhir_bundle)
        if not disease_codes:

            # No cancer diagnoses; no need to search.
            return []

        age, gender, zip_code = self._parse_patient(fhir_bundle.entry[0].resource)
        return self._get_trials_for_diseases(gender, age, disease_codes)

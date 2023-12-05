
drop table if exists fhir_etl.patient cascade;
create table fhir_etl.patient(
    id serial primary key,
    fhir_id character varying(64) not null unique,
    name character varying(256) not null,
    gender character(1),
    dob timestamp without time zone,
    marital_status character(1),
    race character varying(256),
    ethnicity character varying(256)
);

drop table if exists fhir_etl.condition;
create table fhir_etl.condition(
    id serial primary key,
    patient_id integer not null,
    name text not null,
    condition_date timestamp without time zone,
    code character varying(256),
    code_scheme character varying(256),
    clinical_status text,
    cancer_related boolean,
    constraint condition_patient_fk foreign key (patient_id) references fhir_etl.patient(id) on delete cascade
);
create index condition_patient_id_idx on fhir_etl.condition(patient_id);
create index condition_date_idx on fhir_etl.condition(condition_date);

drop table if exists fhir_etl.procedure;
create table fhir_etl.procedure(
    id serial primary key,
    patient_id integer not null,
    procedure_date timestamp without time zone,
    code character varying(256),
    code_scheme character varying(256),
    display text,
    cancer_related boolean,
    constraint procedure_patient_fk foreign key (patient_id) references fhir_etl.patient(id) on delete cascade
);
create index procedure_patient_id_idx on fhir_etl.procedure(patient_id);
create index procedure_date_idx on fhir_etl.procedure(procedure_date);

drop table if exists fhir_etl.observation;
create table fhir_etl.observation(
    id serial primary key,
    patient_id integer not null,
    observation_date timestamp without time zone,
    category character varying(256),
    code character varying(256),
    code_scheme character varying(256),
    display text,
    value character varying(256),
    unit character varying(64),
    cancer_related boolean,
    constraint observation_patient_fk foreign key (patient_id) references fhir_etl.patient(id) on delete cascade
);
create index observation_patient_id_idx on fhir_etl.observation(patient_id);
create index observation_date_idx on fhir_etl.observation(observation_date);

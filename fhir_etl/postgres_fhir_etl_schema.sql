
drop table if exists patient cascade;
create table patient(
    id serial primary key,
    fhir_id character varying(64) not null unique,
    name character varying(256) not null,
    gender character(1),
    dob timestamp without time zone,
    marital_status character(1),
    race character varying(256),
    ethnicity character varying(256)
);

drop table if exists condition;
create table condition(
    id serial primary key,
    patient_id integer not null,
    name text not null,
    condition_date timestamp without time zone,
    code character varying(256),
    code_scheme character varying(256),
    clinical_status text,
    cancer_related boolean,
    constraint condition_patient_fk foreign key (patient_id) references patient(id) on delete cascade
);

drop table if exists observation;
create table observation(
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
    constraint observation_patient_fk foreign key (patient_id) references patient(id) on delete cascade
);

drop table if exists procedure;
create table procedure(
    id serial primary key,
    patient_id integer not null,
    procedure_date timestamp without time zone,
    code character varying(256),
    code_scheme character varying(256),
    display text,
    cancer_related boolean,
    constraint procedure_patient_fk foreign key (patient_id) references patient(id) on delete cascade
);

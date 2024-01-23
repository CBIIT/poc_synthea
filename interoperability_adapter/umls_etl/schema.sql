--TODO: rename schema once this is finalized.
--create schema jcallaway;

drop table if exists jcallaway.umls_to_ncit;
create table jcallaway.umls_to_ncit(
    id serial primary key,
    ncit_code character varying(64),
    umls_code character varying(64),
    other_code character varying(64),
    other_description text,
    other_scheme character varying(64)
);
create index umls_to_ncit_ncit_code_idx on jcallaway.umls_to_ncit(ncit_code);
create index umls_to_ncit_other_code_idx on jcallaway.umls_to_ncit(other_code);
create index umls_to_ncit_other_scheme_idx on jcallaway.umls_to_ncit(other_scheme);

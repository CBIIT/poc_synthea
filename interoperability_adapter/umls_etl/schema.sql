--create schema co;

--In general, there is a many-to-many relationship between UMLS IDs (CUIs)
--and codes in other schemes, so there may be multiple rows in these tables
--with the same cui or the same code in another scheme.

--CREATE TYPE co.status as enum ('exact_match', etc);

drop table if exists co.umls_ontologies;
create table co.umls_ontologies(
    id serial primary key,
    umls_cui character varying(16) not null,
    is_umls_preferred boolean not null,         --is CUI UMLS preferred concept or synonym?
    scheme character varying(64) not null,
    code character varying(64) not null,
    is_other_scheme_preferred boolean not null, --is code preferred concept or synonym in other scheme?
    description text
);
create index umls_ontologies_cui_idx on co.umls_ontologies(umls_cui);
create index umls_ontologies_scheme_idx on co.umls_ontologies(scheme);
create index umls_ontologies_code_idx on co.umls_ontologies(code);
create unique index umls_ontologies_cui_code on co.umls_ontologies(umls_cui, code);

drop table if exists co.umls_ncit;
create table co.umls_ncit(
    id serial primary key,
    umls_cui character varying(16),
    is_umls_preferred boolean not null,    --is CUI UMLS preferred concept or synonym?
    ncit_code character varying(16),
    is_ncit_preferred boolean not null     --is ncit_code preferred concept or synonym?
);
create index umls_ncit_cui_idx on co.umls_ncit(umls_cui);
create index umls_ncit_code_idx on co.umls_ncit(ncit_code);
create unique index umls_ncit_cui_code on co.umls_ncit(umls_cui, ncit_code);

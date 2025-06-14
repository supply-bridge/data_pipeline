-- Table: public.offering_load

-- DROP TABLE IF EXISTS public.offering_load;

CREATE TABLE IF NOT EXISTS public.offering_load
(
    id bigint NOT NULL,
    pid bigint,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    name_de character varying COLLATE pg_catalog."default",
    "order" integer NOT NULL DEFAULT 0,
    is_searchable boolean,
    is_priority boolean,
    created_at timestamp without time zone NOT NULL DEFAULT now(),
    updated_at timestamp without time zone NOT NULL DEFAULT now(),
    thomasnet character varying COLLATE pg_catalog."default",
    part_type sb_offering_part_type_enum,
    icon character varying(255) COLLATE pg_catalog."default",
    synonym_group_id bigint,
    description character varying COLLATE pg_catalog."default",
    creator_id bigint,
    key character varying COLLATE pg_catalog."default",
    original_name text COLLATE pg_catalog."default",
    embedding vector(1536),
    path_embedding vector(1536),
    source character varying(255) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.offering_load
    OWNER to sbadmintest;
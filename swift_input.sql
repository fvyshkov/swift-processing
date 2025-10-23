
-- Table: public.swift_input

-- DROP TABLE IF EXISTS public.swift_input;

CREATE TABLE IF NOT EXISTS public.swift_input
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    file_name text COLLATE pg_catalog."default" NOT NULL,
    state text COLLATE pg_catalog."default" NOT NULL,
    content text COLLATE pg_catalog."default",
    imported timestamp without time zone DEFAULT now(),
    error text COLLATE pg_catalog."default",
    msg_id text COLLATE pg_catalog."default",
    msg_def_idr text COLLATE pg_catalog."default",
    msg_type text COLLATE pg_catalog."default",
    cre_dt_tm timestamp without time zone,
    stmt_id text COLLATE pg_catalog."default",
    elctrnc_seq_nb numeric,
    acct_id text COLLATE pg_catalog."default",
    acct_ccy text COLLATE pg_catalog."default",
    amount numeric,
    currency_code text COLLATE pg_catalog."default",
    dval timestamp without time zone,
    message text COLLATE pg_catalog."default",
    code text COLLATE pg_catalog."default",
    snd_acc text COLLATE pg_catalog."default",
    snd_name text COLLATE pg_catalog."default",
    snd_bank text COLLATE pg_catalog."default",
    snd_bank_name text COLLATE pg_catalog."default",
    snd_mid_bank text COLLATE pg_catalog."default",
    snd_mid_bank_name text COLLATE pg_catalog."default",
    snd_mid_bank_acc text COLLATE pg_catalog."default",
    rcv_acc text COLLATE pg_catalog."default",
    rcv_name text COLLATE pg_catalog."default",
    rcv_bank text COLLATE pg_catalog."default",
    rcv_bank_name text COLLATE pg_catalog."default",
    pk text COLLATE pg_catalog."default",
    snd_mid_bank_acc_val text COLLATE pg_catalog."default",
    CONSTRAINT swift_input_pkey PRIMARY KEY (id),
    CONSTRAINT swift_input_msg_type_check CHECK (msg_type = ANY (ARRAY['pacs.008'::text, 'pacs.009'::text, 'camt.053'::text, 'camt.054'::text, 'camt.056'::text, NULL::text]))
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.swift_input
    OWNER to postgres;

GRANT ALL ON TABLE public.swift_input TO apng;

GRANT ALL ON TABLE public.swift_input TO postgres;

COMMENT ON TABLE public.swift_input
    IS 'Parent table for incoming SWIFT ISO 20022 messages (pacs.008, pacs.009, camt.053, camt.054, camt.056)';
-- Index: idx_swift_input_dval

-- DROP INDEX IF EXISTS public.idx_swift_input_dval;

CREATE INDEX IF NOT EXISTS idx_swift_input_dval
    ON public.swift_input USING btree
    (dval ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_swift_input_imported

-- DROP INDEX IF EXISTS public.idx_swift_input_imported;

CREATE INDEX IF NOT EXISTS idx_swift_input_imported
    ON public.swift_input USING btree
    (imported ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_swift_input_msg_id

-- DROP INDEX IF EXISTS public.idx_swift_input_msg_id;

CREATE INDEX IF NOT EXISTS idx_swift_input_msg_id
    ON public.swift_input USING btree
    (msg_id COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_swift_input_msg_type

-- DROP INDEX IF EXISTS public.idx_swift_input_msg_type;

CREATE INDEX IF NOT EXISTS idx_swift_input_msg_type
    ON public.swift_input USING btree
    (msg_type COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_swift_input_state

-- DROP INDEX IF EXISTS public.idx_swift_input_state;

CREATE INDEX IF NOT EXISTS idx_swift_input_state
    ON public.swift_input USING btree
    (state COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_swift_input_stmt_id

-- DROP INDEX IF EXISTS public.idx_swift_input_stmt_id;

CREATE INDEX IF NOT EXISTS idx_swift_input_stmt_id
    ON public.swift_input USING btree
    (stmt_id COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
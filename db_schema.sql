-- ============================================================================
-- SWIFT ISO 20022 Message Storage Schema
-- Parent table: swift_input (incoming SWIFT messages)
-- Child tables: balances, entries, transaction details
-- Additional tables: settings, output fields
-- ============================================================================

-- Drop existing tables (in correct order due to FK constraints)
DROP TABLE IF EXISTS public.swift_entry_tx_dtls CASCADE;
DROP TABLE IF EXISTS public.swift_stmt_ntry CASCADE;
DROP TABLE IF EXISTS public.swift_stmt_bal CASCADE;
DROP TABLE IF EXISTS public.swift_out_fields CASCADE;
DROP TABLE IF EXISTS public.swift_settings CASCADE;
DROP TABLE IF EXISTS public.swift_input CASCADE;

-- ============================================================================
-- Parent Table: swift_input
-- Stores incoming SWIFT messages (pacs.008, pacs.009, camt.053, camt.054, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_input
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    file_name text COLLATE pg_catalog."default" NOT NULL,
    state text COLLATE pg_catalog."default" NOT NULL,
    content text COLLATE pg_catalog."default",
    imported timestamp without time zone DEFAULT now(),
    error text COLLATE pg_catalog."default",

    -- Message identification
    msg_id text COLLATE pg_catalog."default",
    msg_def_idr text COLLATE pg_catalog."default",
    msg_type text COLLATE pg_catalog."default",
    cre_dt_tm timestamp without time zone,

    -- Statement identification (for camt.053/054)
    stmt_id text COLLATE pg_catalog."default",
    elctrnc_seq_nb numeric,

    -- Account information
    acct_id text COLLATE pg_catalog."default",
    acct_ccy text COLLATE pg_catalog."default",

    -- Transaction summary
    amount numeric,
    currency_code text COLLATE pg_catalog."default",
    dval timestamp without time zone,

    -- Payment details
    message text COLLATE pg_catalog."default",
    code text COLLATE pg_catalog."default",

    -- Debtor (Sender) information
    snd_acc text COLLATE pg_catalog."default",
    snd_name text COLLATE pg_catalog."default",
    snd_bank text COLLATE pg_catalog."default",
    snd_bank_name text COLLATE pg_catalog."default",
    snd_mid_bank text COLLATE pg_catalog."default",
    snd_mid_bank_name text COLLATE pg_catalog."default",
    snd_mid_bank_acc text COLLATE pg_catalog."default",

    -- Creditor (Receiver) information
    rcv_acc text COLLATE pg_catalog."default",
    rcv_name text COLLATE pg_catalog."default",
    rcv_bank text COLLATE pg_catalog."default",
    rcv_bank_name text COLLATE pg_catalog."default",

    CONSTRAINT swift_input_pkey PRIMARY KEY (id),

    CONSTRAINT swift_input_msg_type_check
        CHECK (msg_type IN ('pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056', NULL))
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_input_msg_id
    ON public.swift_input(msg_id);
CREATE INDEX IF NOT EXISTS idx_swift_input_msg_type
    ON public.swift_input(msg_type);
CREATE INDEX IF NOT EXISTS idx_swift_input_stmt_id
    ON public.swift_input(stmt_id);
CREATE INDEX IF NOT EXISTS idx_swift_input_state
    ON public.swift_input(state);
CREATE INDEX IF NOT EXISTS idx_swift_input_imported
    ON public.swift_input(imported);
CREATE INDEX IF NOT EXISTS idx_swift_input_dval
    ON public.swift_input(dval);

COMMENT ON TABLE public.swift_input IS
    'Parent table for incoming SWIFT ISO 20022 messages (pacs.008, pacs.009, camt.053, camt.054, camt.056)';

-- ============================================================================
-- Settings Table: swift_settings
-- Stores system settings for SWIFT processing
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_settings
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    folder_in text COLLATE pg_catalog."default" NOT NULL,
    folder_out text COLLATE pg_catalog."default" NOT NULL,
    server text COLLATE pg_catalog."default",
    CONSTRAINT swift_settings_pkey PRIMARY KEY (id)
)
TABLESPACE pg_default;

COMMENT ON TABLE public.swift_settings IS
    'System settings for SWIFT message processing (input/output folders, server configuration)';

-- Insert default settings
INSERT INTO public.swift_settings (folder_in, folder_out, server)
VALUES ('/mnt/apng-swift/in', '/mnt/apng-swift/out', 'default')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Output Fields Table: swift_out_fields
-- Stores additional output fields for departments
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_out_fields
(
    dep_id integer NOT NULL,
    id integer NOT NULL,
    field1 text COLLATE pg_catalog."default",
    field2 text COLLATE pg_catalog."default",
    modified timestamp without time zone,
    CONSTRAINT swift_out_fields_pkey PRIMARY KEY (dep_id, id)
)
TABLESPACE pg_default;

COMMENT ON TABLE public.swift_out_fields IS
    'Additional output fields for SWIFT message processing by department';

-- ============================================================================
-- Child Table 1: swift_stmt_bal
-- Stores Balance entries from camt.053 (BkToCstmrStmt/Stmt/Bal)
-- Each statement typically has 2-5 balances (OPBD, CLBD, CLAV, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_stmt_bal
(
    swift_input_id uuid NOT NULL,
    tp_cd text COLLATE pg_catalog."default" NOT NULL,
    amt numeric(18, 2) NOT NULL,
    amt_ccy text COLLATE pg_catalog."default",
    cdt_dbt_ind text COLLATE pg_catalog."default" NOT NULL,
    dt timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now(),

    CONSTRAINT swift_stmt_bal_pkey
        PRIMARY KEY (swift_input_id, tp_cd),

    CONSTRAINT swift_stmt_bal_swift_input_fkey
        FOREIGN KEY (swift_input_id)
        REFERENCES public.swift_input (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT swift_stmt_bal_tp_cd_check
        CHECK (tp_cd IN ('OPBD', 'CLBD', 'CLAV', 'FWAV', 'ITBD', 'ITAV', 'OPAV', 'PRCD')),

    CONSTRAINT swift_stmt_bal_cdt_dbt_ind_check
        CHECK (cdt_dbt_ind IN ('CRDT', 'DBIT'))
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_stmt_bal_swift_input_id
    ON public.swift_stmt_bal(swift_input_id);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_bal_dt
    ON public.swift_stmt_bal(dt);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_bal_tp_cd
    ON public.swift_stmt_bal(tp_cd);

COMMENT ON TABLE public.swift_stmt_bal IS
    'Balance entries (Bal) from camt.053 statements. Tp/CdOrPrtry/Cd codes: OPBD=Opening Booked, CLBD=Closing Booked, CLAV=Closing Available, ITBD=Interim Booked';

COMMENT ON COLUMN public.swift_stmt_bal.tp_cd IS
    'Balance type code (Tp/CdOrPrtry/Cd): OPBD, CLBD, CLAV, FWAV, ITBD, ITAV, OPAV, PRCD';
COMMENT ON COLUMN public.swift_stmt_bal.amt IS
    'Balance amount (Amt)';
COMMENT ON COLUMN public.swift_stmt_bal.amt_ccy IS
    'Currency code (Amt/@Ccy) - ISO 4217';
COMMENT ON COLUMN public.swift_stmt_bal.cdt_dbt_ind IS
    'Credit/Debit indicator (CdtDbtInd): CRDT=Credit/Positive, DBIT=Debit/Negative';
COMMENT ON COLUMN public.swift_stmt_bal.dt IS
    'Balance date (Dt/Dt)';

-- ============================================================================
-- Child Table 2: swift_stmt_ntry
-- Stores Entry records from camt.053 (BkToCstmrStmt/Stmt/Ntry)
-- Each entry represents a transaction or group of transactions
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_stmt_ntry
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    swift_input_id uuid NOT NULL,

    -- Entry identification
    ntry_ref text COLLATE pg_catalog."default",
    acct_svcr_ref text COLLATE pg_catalog."default",

    -- Amount
    amt numeric(18, 2) NOT NULL,
    amt_ccy text COLLATE pg_catalog."default",
    cdt_dbt_ind text COLLATE pg_catalog."default" NOT NULL,
    rvsl_ind boolean DEFAULT false,

    -- Status
    sts_cd text COLLATE pg_catalog."default" NOT NULL,

    -- Dates
    bookg_dt date,
    val_dt date,

    -- Bank Transaction Code (BkTxCd)
    bk_tx_cd_domn_cd text COLLATE pg_catalog."default",
    bk_tx_cd_fmly_cd text COLLATE pg_catalog."default",
    bk_tx_cd_sub_fmly_cd text COLLATE pg_catalog."default",
    bk_tx_cd_prtry text COLLATE pg_catalog."default",

    -- Additional information
    addtl_ntry_inf text COLLATE pg_catalog."default",

    created_at timestamp without time zone DEFAULT now(),

    CONSTRAINT swift_stmt_ntry_pkey PRIMARY KEY (id),

    CONSTRAINT swift_stmt_ntry_swift_input_fkey
        FOREIGN KEY (swift_input_id)
        REFERENCES public.swift_input (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT swift_stmt_ntry_cdt_dbt_ind_check
        CHECK (cdt_dbt_ind IN ('CRDT', 'DBIT')),

    CONSTRAINT swift_stmt_ntry_sts_cd_check
        CHECK (sts_cd IN ('BOOK', 'PDNG', 'INFO', 'FUTR'))
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_swift_input_id
    ON public.swift_stmt_ntry(swift_input_id);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_ntry_ref
    ON public.swift_stmt_ntry(ntry_ref);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_acct_svcr_ref
    ON public.swift_stmt_ntry(acct_svcr_ref);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_bookg_dt
    ON public.swift_stmt_ntry(bookg_dt);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_val_dt
    ON public.swift_stmt_ntry(val_dt);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_sts_cd
    ON public.swift_stmt_ntry(sts_cd);
CREATE INDEX IF NOT EXISTS idx_swift_stmt_ntry_bk_tx_cd_domn
    ON public.swift_stmt_ntry(bk_tx_cd_domn_cd);

COMMENT ON TABLE public.swift_stmt_ntry IS
    'Entry records (Ntry) from camt.053 statements. Each entry represents a transaction or batch of transactions.';

COMMENT ON COLUMN public.swift_stmt_ntry.ntry_ref IS
    'Entry reference (NtryRef) - unique identifier for the entry';
COMMENT ON COLUMN public.swift_stmt_ntry.acct_svcr_ref IS
    'Account servicer reference (AcctSvcrRef) - bank internal reference';
COMMENT ON COLUMN public.swift_stmt_ntry.amt IS
    'Entry amount (Amt)';
COMMENT ON COLUMN public.swift_stmt_ntry.cdt_dbt_ind IS
    'Credit/Debit indicator (CdtDbtInd): CRDT or DBIT';
COMMENT ON COLUMN public.swift_stmt_ntry.rvsl_ind IS
    'Reversal indicator (RvslInd) - true if this is a reversal entry';
COMMENT ON COLUMN public.swift_stmt_ntry.sts_cd IS
    'Status code (Sts/Cd): BOOK=Booked, PDNG=Pending, INFO=Information, FUTR=Future';
COMMENT ON COLUMN public.swift_stmt_ntry.bookg_dt IS
    'Booking date (BookgDt/Dt)';
COMMENT ON COLUMN public.swift_stmt_ntry.val_dt IS
    'Value date (ValDt/Dt)';
COMMENT ON COLUMN public.swift_stmt_ntry.bk_tx_cd_domn_cd IS
    'Bank transaction code domain (BkTxCd/Domn/Cd): PMNT, ACMT, CAMT, LDAS, FORX, TRAD, SECU';
COMMENT ON COLUMN public.swift_stmt_ntry.bk_tx_cd_fmly_cd IS
    'Bank transaction code family (BkTxCd/Domn/Fmly/Cd): RCDT, ICDT, RDDT, IDDT, CCRD, MCRD';
COMMENT ON COLUMN public.swift_stmt_ntry.bk_tx_cd_sub_fmly_cd IS
    'Bank transaction code subfamily (BkTxCd/Domn/Fmly/SubFmlyCd): XBCT, DMCT, STDO, RRTN';

-- ============================================================================
-- Child Table 3: swift_entry_tx_dtls
-- Stores Transaction Details from camt.053 (BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls)
-- One entry (Ntry) can contain multiple transaction details (batch payments)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_entry_tx_dtls
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    ntry_id uuid NOT NULL,

    -- References (Refs)
    msg_id text COLLATE pg_catalog."default",
    acct_svcr_ref text COLLATE pg_catalog."default",
    pmt_inf_id text COLLATE pg_catalog."default",
    instr_id text COLLATE pg_catalog."default",
    end_to_end_id text COLLATE pg_catalog."default",
    tx_id text COLLATE pg_catalog."default",
    uetr uuid,
    mndt_id text COLLATE pg_catalog."default",
    chq_nb text COLLATE pg_catalog."default",
    clr_sys_ref text COLLATE pg_catalog."default",

    -- Amount details (AmtDtls)
    amt numeric(18, 2),
    amt_ccy text COLLATE pg_catalog."default",
    cdt_dbt_ind text COLLATE pg_catalog."default",

    -- Related dates (RltdDts)
    accptnc_dt_tm timestamp without time zone,
    intr_bk_sttlm_dt date,
    trad_dt date,

    -- Related parties (RltdPties)
    dbtr_nm text COLLATE pg_catalog."default",
    dbtr_pstl_adr_ctry text COLLATE pg_catalog."default",
    dbtr_acct_id text COLLATE pg_catalog."default",
    dbtr_acct_iban text COLLATE pg_catalog."default",
    dbtr_agt_bicfi text COLLATE pg_catalog."default",
    dbtr_agt_nm text COLLATE pg_catalog."default",

    cdtr_nm text COLLATE pg_catalog."default",
    cdtr_pstl_adr_ctry text COLLATE pg_catalog."default",
    cdtr_acct_id text COLLATE pg_catalog."default",
    cdtr_acct_iban text COLLATE pg_catalog."default",
    cdtr_agt_bicfi text COLLATE pg_catalog."default",
    cdtr_agt_nm text COLLATE pg_catalog."default",

    -- Remittance information (RmtInf)
    rmt_inf_ustrd text COLLATE pg_catalog."default",
    rmt_inf_strd text COLLATE pg_catalog."default",

    -- Purpose (Purp)
    purp_cd text COLLATE pg_catalog."default",
    purp_prtry text COLLATE pg_catalog."default",

    -- Additional information
    addtl_tx_inf text COLLATE pg_catalog."default",

    created_at timestamp without time zone DEFAULT now(),

    CONSTRAINT swift_entry_tx_dtls_pkey PRIMARY KEY (id),

    CONSTRAINT swift_entry_tx_dtls_ntry_fkey
        FOREIGN KEY (ntry_id)
        REFERENCES public.swift_stmt_ntry (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT swift_entry_tx_dtls_cdt_dbt_ind_check
        CHECK (cdt_dbt_ind IN ('CRDT', 'DBIT', NULL))
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_ntry_id
    ON public.swift_entry_tx_dtls(ntry_id);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_uetr
    ON public.swift_entry_tx_dtls(uetr);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_end_to_end_id
    ON public.swift_entry_tx_dtls(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_instr_id
    ON public.swift_entry_tx_dtls(instr_id);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_tx_id
    ON public.swift_entry_tx_dtls(tx_id);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_intr_bk_sttlm_dt
    ON public.swift_entry_tx_dtls(intr_bk_sttlm_dt);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_dbtr_agt_bicfi
    ON public.swift_entry_tx_dtls(dbtr_agt_bicfi);
CREATE INDEX IF NOT EXISTS idx_swift_entry_tx_dtls_cdtr_agt_bicfi
    ON public.swift_entry_tx_dtls(cdtr_agt_bicfi);

COMMENT ON TABLE public.swift_entry_tx_dtls IS
    'Transaction details (TxDtls) from camt.053 entries. One entry (Ntry) can contain multiple TxDtls (batch payments, salary payments, etc.)';

COMMENT ON COLUMN public.swift_entry_tx_dtls.ntry_id IS
    'Foreign key to swift_stmt_ntry (parent entry)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.msg_id IS
    'Message identification (Refs/MsgId)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.instr_id IS
    'Instruction identification (Refs/InstrId)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.end_to_end_id IS
    'End-to-end identification (Refs/EndToEndId)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.tx_id IS
    'Transaction identification (Refs/TxId)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.uetr IS
    'Unique End-to-end Transaction Reference (Refs/UETR)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.intr_bk_sttlm_dt IS
    'Interbank settlement date (RltdDts/IntrBkSttlmDt)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.dbtr_nm IS
    'Debtor name (RltdPties/Dbtr/Nm)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.dbtr_acct_iban IS
    'Debtor account IBAN (RltdPties/DbtrAcct/Id/IBAN)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.dbtr_agt_bicfi IS
    'Debtor agent BIC (RltdPties/DbtrAgt/FinInstnId/BICFI)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.cdtr_nm IS
    'Creditor name (RltdPties/Cdtr/Nm)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.cdtr_acct_iban IS
    'Creditor account IBAN (RltdPties/CdtrAcct/Id/IBAN)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.cdtr_agt_bicfi IS
    'Creditor agent BIC (RltdPties/CdtrAgt/FinInstnId/BICFI)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.rmt_inf_ustrd IS
    'Unstructured remittance information (RmtInf/Ustrd)';
COMMENT ON COLUMN public.swift_entry_tx_dtls.purp_cd IS
    'Purpose code (Purp/Cd): SALA, PENS, SUPP, TRAD, CASH, GOVT, etc.';

-- ============================================================================
-- Permissions
-- ============================================================================
ALTER TABLE IF EXISTS public.swift_input OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_settings OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_out_fields OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_stmt_bal OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_stmt_ntry OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_entry_tx_dtls OWNER TO postgres;

GRANT ALL ON TABLE public.swift_input TO apng;
GRANT ALL ON TABLE public.swift_input TO postgres;
GRANT ALL ON TABLE public.swift_settings TO apng;
GRANT ALL ON TABLE public.swift_settings TO postgres;
GRANT ALL ON TABLE public.swift_out_fields TO apng;
GRANT ALL ON TABLE public.swift_out_fields TO postgres;
GRANT ALL ON TABLE public.swift_stmt_bal TO apng;
GRANT ALL ON TABLE public.swift_stmt_bal TO postgres;
GRANT ALL ON TABLE public.swift_stmt_ntry TO apng;
GRANT ALL ON TABLE public.swift_stmt_ntry TO postgres;
GRANT ALL ON TABLE public.swift_entry_tx_dtls TO apng;
GRANT ALL ON TABLE public.swift_entry_tx_dtls TO postgres;

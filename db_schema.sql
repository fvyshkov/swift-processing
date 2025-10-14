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
-- REFERENCE TABLES (ISO 20022 Code Sets)
-- ============================================================================

-- Drop reference tables
DROP TABLE IF EXISTS public.ref_currency_codes CASCADE;
DROP TABLE IF EXISTS public.ref_country_codes CASCADE;
DROP TABLE IF EXISTS public.ref_settlement_method CASCADE;
DROP TABLE IF EXISTS public.ref_charge_bearer CASCADE;
DROP TABLE IF EXISTS public.ref_purpose_codes CASCADE;
DROP TABLE IF EXISTS public.ref_balance_type CASCADE;
DROP TABLE IF EXISTS public.ref_credit_debit_indicator CASCADE;
DROP TABLE IF EXISTS public.ref_entry_status CASCADE;
DROP TABLE IF EXISTS public.ref_bank_tx_domain CASCADE;
DROP TABLE IF EXISTS public.ref_bank_tx_family CASCADE;
DROP TABLE IF EXISTS public.ref_bank_tx_subfamily CASCADE;
DROP TABLE IF EXISTS public.ref_cancellation_reason CASCADE;
DROP TABLE IF EXISTS public.ref_instruction_priority CASCADE;
DROP TABLE IF EXISTS public.ref_account_type CASCADE;
DROP TABLE IF EXISTS public.ref_message_types CASCADE;

-- ----------------------------------------------------------------------------
-- Currency Codes (ISO 4217)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_currency_codes
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_currency_codes_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_currency_codes IS 'ISO 4217 currency codes';

-- ----------------------------------------------------------------------------
-- Country Codes (ISO 3166-1 alpha-2)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_country_codes
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_country_codes_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_country_codes IS 'ISO 3166-1 alpha-2 country codes';

-- ----------------------------------------------------------------------------
-- Settlement Method (SttlmMtd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_settlement_method
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_settlement_method_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_settlement_method IS 'Settlement method codes (SttlmMtd)';

-- ----------------------------------------------------------------------------
-- Charge Bearer Codes (ChrgBr)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_charge_bearer
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_charge_bearer_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_charge_bearer IS 'Charge bearer codes (ChrgBr) - who pays the fees';

-- ----------------------------------------------------------------------------
-- Purpose Codes (External Purpose Code)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_purpose_codes
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_purpose_codes_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_purpose_codes IS 'Payment purpose codes (Purp/Cd)';

-- ----------------------------------------------------------------------------
-- Balance Type Codes (Tp/CdOrPrtry/Cd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_balance_type
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_balance_type_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_balance_type IS 'Balance type codes for camt.053 (Bal/Tp/CdOrPrtry/Cd)';

-- ----------------------------------------------------------------------------
-- Credit/Debit Indicator (CdtDbtInd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_credit_debit_indicator
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_credit_debit_indicator_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_credit_debit_indicator IS 'Credit/Debit indicator codes (CdtDbtInd)';

-- ----------------------------------------------------------------------------
-- Entry Status Codes (Sts/Cd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_entry_status
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_entry_status_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_entry_status IS 'Entry status codes for camt.053 (Ntry/Sts/Cd)';

-- ----------------------------------------------------------------------------
-- Bank Transaction Code Domain (BkTxCd/Domn/Cd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_bank_tx_domain
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_bank_tx_domain_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_bank_tx_domain IS 'Bank transaction code domain (BkTxCd/Domn/Cd)';

-- ----------------------------------------------------------------------------
-- Bank Transaction Family Codes (BkTxCd/Domn/Fmly/Cd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_bank_tx_family
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_bank_tx_family_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_bank_tx_family IS 'Bank transaction family codes (BkTxCd/Domn/Fmly/Cd)';

-- ----------------------------------------------------------------------------
-- Bank Transaction Subfamily Codes (BkTxCd/Domn/Fmly/SubFmlyCd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_bank_tx_subfamily
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_bank_tx_subfamily_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_bank_tx_subfamily IS 'Bank transaction subfamily codes (BkTxCd/Domn/Fmly/SubFmlyCd)';

-- ----------------------------------------------------------------------------
-- Cancellation Reason Codes (camt.056 CxlRsnInf/Rsn/Cd)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_cancellation_reason
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_cancellation_reason_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_cancellation_reason IS 'Cancellation reason codes for camt.056 (CxlRsnInf/Rsn/Cd)';

-- ----------------------------------------------------------------------------
-- Instruction Priority (InstrPrty)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_instruction_priority
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_instruction_priority_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_instruction_priority IS 'Instruction priority codes (PmtTpInf/InstrPrty)';

-- ----------------------------------------------------------------------------
-- Account Type Codes (Acct/Tp)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_account_type
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_account_type_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_account_type IS 'Account type codes (Acct/Tp)';

-- ----------------------------------------------------------------------------
-- Message Types
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ref_message_types
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    CONSTRAINT ref_message_types_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.ref_message_types IS 'ISO 20022 message type identifiers';

-- ============================================================================
-- Permissions for Reference Tables
-- ============================================================================
ALTER TABLE IF EXISTS public.ref_currency_codes OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_country_codes OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_settlement_method OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_charge_bearer OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_purpose_codes OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_balance_type OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_credit_debit_indicator OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_entry_status OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_bank_tx_domain OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_bank_tx_family OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_bank_tx_subfamily OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_cancellation_reason OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_instruction_priority OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_account_type OWNER TO postgres;
ALTER TABLE IF EXISTS public.ref_message_types OWNER TO postgres;

GRANT ALL ON TABLE public.ref_currency_codes TO apng;
GRANT ALL ON TABLE public.ref_currency_codes TO postgres;
GRANT ALL ON TABLE public.ref_country_codes TO apng;
GRANT ALL ON TABLE public.ref_country_codes TO postgres;
GRANT ALL ON TABLE public.ref_settlement_method TO apng;
GRANT ALL ON TABLE public.ref_settlement_method TO postgres;
GRANT ALL ON TABLE public.ref_charge_bearer TO apng;
GRANT ALL ON TABLE public.ref_charge_bearer TO postgres;
GRANT ALL ON TABLE public.ref_purpose_codes TO apng;
GRANT ALL ON TABLE public.ref_purpose_codes TO postgres;
GRANT ALL ON TABLE public.ref_balance_type TO apng;
GRANT ALL ON TABLE public.ref_balance_type TO postgres;
GRANT ALL ON TABLE public.ref_credit_debit_indicator TO apng;
GRANT ALL ON TABLE public.ref_credit_debit_indicator TO postgres;
GRANT ALL ON TABLE public.ref_entry_status TO apng;
GRANT ALL ON TABLE public.ref_entry_status TO postgres;
GRANT ALL ON TABLE public.ref_bank_tx_domain TO apng;
GRANT ALL ON TABLE public.ref_bank_tx_domain TO postgres;
GRANT ALL ON TABLE public.ref_bank_tx_family TO apng;
GRANT ALL ON TABLE public.ref_bank_tx_family TO postgres;
GRANT ALL ON TABLE public.ref_bank_tx_subfamily TO apng;
GRANT ALL ON TABLE public.ref_bank_tx_subfamily TO postgres;
GRANT ALL ON TABLE public.ref_cancellation_reason TO apng;
GRANT ALL ON TABLE public.ref_cancellation_reason TO postgres;
GRANT ALL ON TABLE public.ref_instruction_priority TO apng;
GRANT ALL ON TABLE public.ref_instruction_priority TO postgres;
GRANT ALL ON TABLE public.ref_account_type TO apng;
GRANT ALL ON TABLE public.ref_account_type TO postgres;
GRANT ALL ON TABLE public.ref_message_types TO apng;
GRANT ALL ON TABLE public.ref_message_types TO postgres;

-- ============================================================================
-- POPULATE REFERENCE DATA
-- ============================================================================

-- ============================================================================
-- Currency Codes (ISO 4217)
-- ============================================================================
INSERT INTO public.ref_currency_codes (code, name_en, name_ru, name_combined) VALUES
('EUR', 'Euro', 'Евро', 'Euro (Евро)'),
('USD', 'US Dollar', 'Доллар США', 'US Dollar (Доллар США)'),
('GBP', 'British Pound', 'Фунт стерлингов', 'British Pound (Фунт стерлингов)'),
('CHF', 'Swiss Franc', 'Швейцарский франк', 'Swiss Franc (Швейцарский франк)'),
('JPY', 'Japanese Yen', 'Японская йена', 'Japanese Yen (Японская йена)'),
('RON', 'Romanian Leu', 'Румынский лей', 'Romanian Leu (Румынский лей)'),
('NOK', 'Norwegian Krone', 'Норвежская крона', 'Norwegian Krone (Норвежская крона)'),
('SEK', 'Swedish Krona', 'Шведская крона', 'Swedish Krona (Шведская крона)'),
('DKK', 'Danish Krone', 'Датская крона', 'Danish Krone (Датская крона)'),
('PLN', 'Polish Zloty', 'Польский злотый', 'Polish Zloty (Польский злотый)'),
('RUB', 'Russian Ruble', 'Российский рубль', 'Russian Ruble (Российский рубль)'),
('CNY', 'Chinese Yuan', 'Китайский юань', 'Chinese Yuan (Китайский юань)'),
('CAD', 'Canadian Dollar', 'Канадский доллар', 'Canadian Dollar (Канадский доллар)'),
('AUD', 'Australian Dollar', 'Австралийский доллар', 'Australian Dollar (Австралийский доллар)'),
('HKD', 'Hong Kong Dollar', 'Гонконгский доллар', 'Hong Kong Dollar (Гонконгский доллар)'),
('SGD', 'Singapore Dollar', 'Сингапурский доллар', 'Singapore Dollar (Сингапурский доллар)'),
('INR', 'Indian Rupee', 'Индийская рупия', 'Indian Rupee (Индийская рупия)'),
('KRW', 'South Korean Won', 'Южнокорейская вона', 'South Korean Won (Южнокорейская вона)'),
('BRL', 'Brazilian Real', 'Бразильский реал', 'Brazilian Real (Бразильский реал)'),
('MXN', 'Mexican Peso', 'Мексиканское песо', 'Mexican Peso (Мексиканское песо)'),
('ZAR', 'South African Rand', 'Южноафриканский рэнд', 'South African Rand (Южноафриканский рэнд)'),
('TRY', 'Turkish Lira', 'Турецкая лира', 'Turkish Lira (Турецкая лира)'),
('NZD', 'New Zealand Dollar', 'Новозеландский доллар', 'New Zealand Dollar (Новозеландский доллар)'),
('THB', 'Thai Baht', 'Тайский бат', 'Thai Baht (Тайский бат)'),
('IDR', 'Indonesian Rupiah', 'Индонезийская рупия', 'Indonesian Rupiah (Индонезийская рупия)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Country Codes (ISO 3166-1 alpha-2)
-- ============================================================================
INSERT INTO public.ref_country_codes (code, name_en, name_ru, name_combined) VALUES
('GB', 'United Kingdom', 'Великобритания', 'United Kingdom (Великобритания)'),
('RO', 'Romania', 'Румыния', 'Romania (Румыния)'),
('BE', 'Belgium', 'Бельгия', 'Belgium (Бельгия)'),
('NO', 'Norway', 'Норвегия', 'Norway (Норвегия)'),
('DE', 'Germany', 'Германия', 'Germany (Германия)'),
('FR', 'France', 'Франция', 'France (Франция)'),
('NL', 'Netherlands', 'Нидерланды', 'Netherlands (Нидерланды)'),
('IT', 'Italy', 'Италия', 'Italy (Италия)'),
('ES', 'Spain', 'Испания', 'Spain (Испания)'),
('CH', 'Switzerland', 'Швейцария', 'Switzerland (Швейцария)'),
('US', 'United States', 'США', 'United States (США)'),
('RU', 'Russia', 'Россия', 'Russia (Россия)'),
('CN', 'China', 'Китай', 'China (Китай)'),
('JP', 'Japan', 'Япония', 'Japan (Япония)'),
('IN', 'India', 'Индия', 'India (Индия)'),
('CA', 'Canada', 'Канада', 'Canada (Канада)'),
('AU', 'Australia', 'Австралия', 'Australia (Австралия)'),
('BR', 'Brazil', 'Бразилия', 'Brazil (Бразилия)'),
('MX', 'Mexico', 'Мексика', 'Mexico (Мексика)'),
('KR', 'South Korea', 'Южная Корея', 'South Korea (Южная Корея)'),
('SE', 'Sweden', 'Швеция', 'Sweden (Швеция)'),
('DK', 'Denmark', 'Дания', 'Denmark (Дания)'),
('PL', 'Poland', 'Польша', 'Poland (Польша)'),
('AT', 'Austria', 'Австрия', 'Austria (Австрия)'),
('FI', 'Finland', 'Финляндия', 'Finland (Финляндия)'),
('IE', 'Ireland', 'Ирландия', 'Ireland (Ирландия)'),
('PT', 'Portugal', 'Португалия', 'Portugal (Португалия)'),
('GR', 'Greece', 'Греция', 'Greece (Греция)'),
('CZ', 'Czech Republic', 'Чехия', 'Czech Republic (Чехия)'),
('HU', 'Hungary', 'Венгрия', 'Hungary (Венгрия)'),
('SG', 'Singapore', 'Сингапур', 'Singapore (Сингапур)'),
('HK', 'Hong Kong', 'Гонконг', 'Hong Kong (Гонконг)'),
('AE', 'United Arab Emirates', 'ОАЭ', 'United Arab Emirates (ОАЭ)'),
('SA', 'Saudi Arabia', 'Саудовская Аравия', 'Saudi Arabia (Саудовская Аравия)'),
('TR', 'Turkey', 'Турция', 'Turkey (Турция)'),
('ZA', 'South Africa', 'ЮАР', 'South Africa (ЮАР)'),
('TH', 'Thailand', 'Таиланд', 'Thailand (Таиланд)'),
('ID', 'Indonesia', 'Индонезия', 'Indonesia (Индонезия)'),
('NZ', 'New Zealand', 'Новая Зеландия', 'New Zealand (Новая Зеландия)'),
('LU', 'Luxembourg', 'Люксембург', 'Luxembourg (Люксембург)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Settlement Method (SttlmMtd)
-- ============================================================================
INSERT INTO public.ref_settlement_method (code, name_en, name_ru, name_combined) VALUES
('INDA', 'Indirect Agent', 'Косвенный агент', 'Indirect Agent (Косвенный агент)'),
('INGA', 'Instructing Agent', 'Инструктирующий агент', 'Instructing Agent (Инструктирующий агент)'),
('CLRG', 'Clearing', 'Клиринг', 'Clearing (Клиринг)'),
('COVE', 'Cover', 'Покрытие', 'Cover (Покрытие)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Charge Bearer Codes (ChrgBr)
-- ============================================================================
INSERT INTO public.ref_charge_bearer (code, name_en, name_ru, name_combined) VALUES
('DEBT', 'Borne by Debtor', 'За счет плательщика', 'Borne by Debtor (За счет плательщика)'),
('CRED', 'Borne by Creditor', 'За счет получателя', 'Borne by Creditor (За счет получателя)'),
('SHAR', 'Shared', 'Разделенная комиссия', 'Shared (Разделенная комиссия)'),
('SLEV', 'Service Level', 'По уровню сервиса', 'Service Level (По уровню сервиса)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Purpose Codes (External Purpose Code)
-- ============================================================================
INSERT INTO public.ref_purpose_codes (code, name_en, name_ru, name_combined) VALUES
('SALA', 'Salary Payment', 'Выплата зарплаты', 'Salary Payment (Выплата зарплаты)'),
('PENS', 'Pension Payment', 'Пенсионный платеж', 'Pension Payment (Пенсионный платеж)'),
('SUPP', 'Supplier Payment', 'Платеж поставщику', 'Supplier Payment (Платеж поставщику)'),
('TRAD', 'Trade Settlement', 'Торговый расчет', 'Trade Settlement (Торговый расчет)'),
('CASH', 'Cash Management Transfer', 'Управление наличностью', 'Cash Management Transfer (Управление наличностью)'),
('LOAN', 'Loan', 'Кредит', 'Loan (Кредит)'),
('INTC', 'Intra-Company Payment', 'Внутрикорпоративный платеж', 'Intra-Company Payment (Внутрикорпоративный платеж)'),
('TREA', 'Treasury Payment', 'Казначейский платеж', 'Treasury Payment (Казначейский платеж)'),
('GOVT', 'Government Payment', 'Государственный платеж', 'Government Payment (Государственный платеж)'),
('BONU', 'Bonus Payment', 'Бонусный платеж', 'Bonus Payment (Бонусный платеж)'),
('CBFF', 'Capital Building', 'Капитальное строительство', 'Capital Building (Капитальное строительство)'),
('DIVI', 'Dividend', 'Дивиденд', 'Dividend (Дивиденд)'),
('CHAR', 'Charity Payment', 'Благотворительный платеж', 'Charity Payment (Благотворительный платеж)'),
('TAXS', 'Tax Payment', 'Налоговый платеж', 'Tax Payment (Налоговый платеж)'),
('RENT', 'Rent Payment', 'Оплата аренды', 'Rent Payment (Оплата аренды)'),
('UTIL', 'Utilities', 'Коммунальные услуги', 'Utilities (Коммунальные услуги)'),
('REFU', 'Refund', 'Возврат', 'Refund (Возврат)'),
('INSV', 'Insurance Premium', 'Страховая премия', 'Insurance Premium (Страховая премия)'),
('INTE', 'Interest Payment', 'Процентный платеж', 'Interest Payment (Процентный платеж)'),
('FEES', 'Fees', 'Комиссии', 'Fees (Комиссии)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Balance Type Codes (Tp/CdOrPrtry/Cd)
-- ============================================================================
INSERT INTO public.ref_balance_type (code, name_en, name_ru, name_combined) VALUES
('OPBD', 'Opening Booked', 'Начальный проведенный баланс', 'Opening Booked (Начальный проведенный баланс)'),
('CLBD', 'Closing Booked', 'Конечный проведенный баланс', 'Closing Booked (Конечный проведенный баланс)'),
('CLAV', 'Closing Available', 'Конечный доступный баланс', 'Closing Available (Конечный доступный баланс)'),
('FWAV', 'Forward Available', 'Прогнозный доступный баланс', 'Forward Available (Прогнозный доступный баланс)'),
('ITBD', 'Interim Booked', 'Промежуточный проведенный', 'Interim Booked (Промежуточный проведенный)'),
('ITAV', 'Interim Available', 'Промежуточный доступный', 'Interim Available (Промежуточный доступный)'),
('OPAV', 'Opening Available', 'Начальный доступный баланс', 'Opening Available (Начальный доступный баланс)'),
('PRCD', 'Previously Closed Booked', 'Предыдущий закрытый баланс', 'Previously Closed Booked (Предыдущий закрытый баланс)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Credit/Debit Indicator (CdtDbtInd)
-- ============================================================================
INSERT INTO public.ref_credit_debit_indicator (code, name_en, name_ru, name_combined) VALUES
('CRDT', 'Credit', 'Кредит (Поступление)', 'Credit (Кредит (Поступление))'),
('DBIT', 'Debit', 'Дебет (Списание)', 'Debit (Дебет (Списание))')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Entry Status Codes (Sts/Cd)
-- ============================================================================
INSERT INTO public.ref_entry_status (code, name_en, name_ru, name_combined) VALUES
('BOOK', 'Booked', 'Проведено', 'Booked (Проведено)'),
('PDNG', 'Pending', 'В ожидании', 'Pending (В ожидании)'),
('INFO', 'Information', 'Информационная запись', 'Information (Информационная запись)'),
('FUTR', 'Future', 'Будущая транзакция', 'Future (Будущая транзакция)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Bank Transaction Code Domain (BkTxCd/Domn/Cd)
-- ============================================================================
INSERT INTO public.ref_bank_tx_domain (code, name_en, name_ru, name_combined) VALUES
('PMNT', 'Payments', 'Платежи', 'Payments (Платежи)'),
('ACMT', 'Account Management', 'Управление счетом', 'Account Management (Управление счетом)'),
('CAMT', 'Cash Management', 'Управление наличностью', 'Cash Management (Управление наличностью)'),
('XTND', 'Extended Domain', 'Расширенный домен', 'Extended Domain (Расширенный домен)'),
('LDAS', 'Loans and Deposits', 'Кредиты и депозиты', 'Loans and Deposits (Кредиты и депозиты)'),
('CMDT', 'Commodities', 'Товары', 'Commodities (Товары)'),
('FORX', 'Foreign Exchange', 'Валютные операции', 'Foreign Exchange (Валютные операции)'),
('TRAD', 'Trade Services', 'Торговые услуги', 'Trade Services (Торговые услуги)'),
('SECU', 'Securities', 'Ценные бумаги', 'Securities (Ценные бумаги)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Bank Transaction Family Codes (BkTxCd/Domn/Fmly/Cd)
-- ============================================================================
INSERT INTO public.ref_bank_tx_family (code, name_en, name_ru, name_combined) VALUES
('RCDT', 'Received Credit Transfer', 'Полученный кредитовый перевод', 'Received Credit Transfer (Полученный кредитовый перевод)'),
('ICDT', 'Issued Credit Transfer', 'Отправленный кредитовый перевод', 'Issued Credit Transfer (Отправленный кредитовый перевод)'),
('RDDT', 'Received Direct Debit', 'Полученное прямое дебетование', 'Received Direct Debit (Полученное прямое дебетование)'),
('IDDT', 'Issued Direct Debit', 'Отправленное прямое дебетование', 'Issued Direct Debit (Отправленное прямое дебетование)'),
('CCRD', 'Customer Card Transaction', 'Карточная транзакция клиента', 'Customer Card Transaction (Карточная транзакция клиента)'),
('MCRD', 'Merchant Card Transaction', 'Карточная транзакция продавца', 'Merchant Card Transaction (Карточная транзакция продавца)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Bank Transaction Subfamily Codes (BkTxCd/Domn/Fmly/SubFmlyCd)
-- ============================================================================
INSERT INTO public.ref_bank_tx_subfamily (code, name_en, name_ru, name_combined) VALUES
('XBCT', 'Cross Border Credit Transfer', 'Трансграничный кредитовый перевод', 'Cross Border Credit Transfer (Трансграничный кредитовый перевод)'),
('DMCT', 'Domestic Credit Transfer', 'Внутренний кредитовый перевод', 'Domestic Credit Transfer (Внутренний кредитовый перевод)'),
('STDO', 'Standing Order', 'Постоянное поручение', 'Standing Order (Постоянное поручение)'),
('RRTN', 'Return', 'Возврат', 'Return (Возврат)'),
('REQL', 'Request for Liquidity', 'Запрос ликвидности', 'Request for Liquidity (Запрос ликвидности)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Cancellation Reason Codes (camt.056 CxlRsnInf/Rsn/Cd)
-- ============================================================================
INSERT INTO public.ref_cancellation_reason (code, name_en, name_ru, name_combined) VALUES
('DUPL', 'Duplicate Payment', 'Дублирующий платеж', 'Duplicate Payment (Дублирующий платеж)'),
('FRAD', 'Fraudulent Origin', 'Мошенничество', 'Fraudulent Origin (Мошенничество)'),
('TECH', 'Technical Problems', 'Технические проблемы', 'Technical Problems (Технические проблемы)'),
('CUST', 'Requested By Customer', 'Запрошено клиентом', 'Requested By Customer (Запрошено клиентом)'),
('CUTA', 'Requested By Customer - Technical Problem', 'Запрошено клиентом - технические проблемы', 'Requested By Customer - Technical Problem (Запрошено клиентом - технические проблемы)'),
('UPAY', 'Undue Payment', 'Необоснованный платеж', 'Undue Payment (Необоснованный платеж)'),
('AM09', 'Wrong Amount', 'Неверная сумма', 'Wrong Amount (Неверная сумма)'),
('AC03', 'Invalid Creditor Account Number', 'Неверный счет кредитора', 'Invalid Creditor Account Number (Неверный счет кредитора)'),
('AC04', 'Closed Account', 'Закрытый счет', 'Closed Account (Закрытый счет)'),
('AG01', 'Transaction Forbidden', 'Транзакция запрещена', 'Transaction Forbidden (Транзакция запрещена)'),
('AG02', 'Invalid Bank Operation Code', 'Неверный операционный код банка', 'Invalid Bank Operation Code (Неверный операционный код банка)'),
('AGNT', 'Incorrect Agent', 'Неверный агент', 'Incorrect Agent (Неверный агент)'),
('CURR', 'Incorrect Currency', 'Неверная валюта', 'Incorrect Currency (Неверная валюта)'),
('FOCR', 'Following Cancellation Request', 'Следуя запросу на отмену', 'Following Cancellation Request (Следуя запросу на отмену)'),
('LEGL', 'Legal Decision', 'Судебное решение', 'Legal Decision (Судебное решение)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Instruction Priority (InstrPrty)
-- ============================================================================
INSERT INTO public.ref_instruction_priority (code, name_en, name_ru, name_combined) VALUES
('HIGH', 'High Priority', 'Высокий приоритет', 'High Priority (Высокий приоритет)'),
('NORM', 'Normal Priority', 'Обычный приоритет', 'Normal Priority (Обычный приоритет)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Account Type Codes (Acct/Tp)
-- ============================================================================
INSERT INTO public.ref_account_type (code, name_en, name_ru, name_combined) VALUES
('CACC', 'Current Account', 'Текущий счет', 'Current Account (Текущий счет)'),
('SVGS', 'Savings Account', 'Сберегательный счет', 'Savings Account (Сберегательный счет)'),
('TRAN', 'Transactional Account', 'Транзакционный счет', 'Transactional Account (Транзакционный счет)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Message Types
-- ============================================================================
INSERT INTO public.ref_message_types (code, name_en, name_ru, name_combined) VALUES
('pacs.008', 'Customer Credit Transfer', 'Клиентский кредитовый перевод', 'Customer Credit Transfer (Клиентский кредитовый перевод)'),
('pacs.009', 'Financial Institution Credit Transfer (COV)', 'Межбанковский кредитовый перевод (покрытие)', 'Financial Institution Credit Transfer (COV) (Межбанковский кредитовый перевод (покрытие))'),
('camt.053', 'Bank to Customer Statement', 'Банковская выписка клиенту', 'Bank to Customer Statement (Банковская выписка клиенту)'),
('camt.054', 'Bank to Customer Debit/Credit Notification', 'Уведомление о дебете/кредите', 'Bank to Customer Debit/Credit Notification (Уведомление о дебете/кредите)'),
('camt.056', 'FI to FI Payment Cancellation Request', 'Запрос на отмену платежа', 'FI to FI Payment Cancellation Request (Запрос на отмену платежа)')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Reference Data Summary
-- ============================================================================
-- Total records inserted:
-- Currency Codes: 25
-- Country Codes: 40
-- Settlement Method: 4
-- Charge Bearer: 4
-- Purpose Codes: 20
-- Balance Type: 8
-- Credit/Debit Indicator: 2
-- Entry Status: 4
-- Bank Transaction Domain: 9
-- Bank Transaction Family: 6
-- Bank Transaction Subfamily: 5
-- Cancellation Reason: 15
-- Instruction Priority: 2
-- Account Type: 3
-- Message Types: 5
-- ============================================================================
-- TOTAL: 152 reference values
-- ============================================================================

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

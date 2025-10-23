-- ============================================================================
-- SWIFT ISO 20022 Message Storage Schema - FULL VERSION
-- Complete setup with all tables, fields, reference data and process states
-- Version: 2025-10-23 - Added support for pacs.009, camt.054, camt.056
-- ============================================================================

-- Drop existing tables (in correct order due to FK constraints)
DROP TABLE IF EXISTS public.process_operation_states CASCADE;
DROP TABLE IF EXISTS public.process CASCADE;
DROP TABLE IF EXISTS public.process_operation CASCADE;
DROP TABLE IF EXISTS public.process_state CASCADE;
DROP TABLE IF EXISTS public.process_type CASCADE;

DROP TABLE IF EXISTS public.swift_ntfctn_tx_dtls CASCADE;
DROP TABLE IF EXISTS public.swift_ntfctn_ntry CASCADE;
DROP TABLE IF EXISTS public.swift_entry_tx_dtls CASCADE;
DROP TABLE IF EXISTS public.swift_stmt_ntry CASCADE;
DROP TABLE IF EXISTS public.swift_stmt_bal CASCADE;
DROP TABLE IF EXISTS public.swift_out_fields CASCADE;
DROP TABLE IF EXISTS public.swift_settings CASCADE;
DROP TABLE IF EXISTS public.swift_input CASCADE;

-- ============================================================================
-- Parent Table: swift_input
-- Stores incoming SWIFT messages (pacs.008, pacs.009, camt.053, camt.054, camt.056)
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

    -- Statement identification (for camt.053)
    stmt_id text COLLATE pg_catalog."default",
    elctrnc_seq_nb numeric,

    -- Notification identification (for camt.054)  -- ✨ NEW
    ntfctn_id text COLLATE pg_catalog."default",  -- ✨ NEW

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

    -- Legacy fields (keep for compatibility)
    pk text COLLATE pg_catalog."default",
    snd_mid_bank_acc_val text COLLATE pg_catalog."default",

    -- ========================================================================
    -- ✨ NEW FIELDS FOR pacs.009 (Financial Institution Credit Transfer)
    -- ========================================================================
    instd_agt text COLLATE pg_catalog."default",              -- Instructed Agent BIC
    instd_agt_name text COLLATE pg_catalog."default",         -- Instructed Agent Name
    underlying_dbtr_name text COLLATE pg_catalog."default",   -- Real debtor from UndrlygCstmrCdtTrf
    underlying_dbtr_acc text COLLATE pg_catalog."default",    -- Real debtor account
    underlying_dbtr_agt text COLLATE pg_catalog."default",    -- Real debtor agent BIC
    underlying_cdtr_name text COLLATE pg_catalog."default",   -- Real creditor from UndrlygCstmrCdtTrf
    underlying_cdtr_acc text COLLATE pg_catalog."default",    -- Real creditor account
    underlying_cdtr_agt text COLLATE pg_catalog."default",    -- Real creditor agent BIC

    -- ========================================================================
    -- ✨ NEW FIELDS FOR camt.056 (Payment Cancellation Request)
    -- ========================================================================
    case_id text COLLATE pg_catalog."default",                -- Case Assignment ID
    case_assgnr text COLLATE pg_catalog."default",            -- Case creator BIC
    orgnl_msg_id text COLLATE pg_catalog."default",           -- Original message ID
    orgnl_msg_nm_id text COLLATE pg_catalog."default",        -- Original message name (e.g. pacs.008.001.08)
    orgnl_instr_id text COLLATE pg_catalog."default",         -- Original InstrId
    orgnl_end_to_end_id text COLLATE pg_catalog."default",    -- Original EndToEndId
    orgnl_tx_id text COLLATE pg_catalog."default",            -- Original TxId
    orgnl_uetr uuid,                                          -- Original UETR
    cxl_rsn_cd text COLLATE pg_catalog."default",             -- Cancellation reason code
    cxl_rsn_addtl_inf text COLLATE pg_catalog."default",      -- Additional cancellation info

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
CREATE INDEX IF NOT EXISTS idx_swift_input_ntfctn_id          -- ✨ NEW
    ON public.swift_input(ntfctn_id);                         -- ✨ NEW
CREATE INDEX IF NOT EXISTS idx_swift_input_state
    ON public.swift_input(state);
CREATE INDEX IF NOT EXISTS idx_swift_input_imported
    ON public.swift_input(imported);
CREATE INDEX IF NOT EXISTS idx_swift_input_dval
    ON public.swift_input(dval);
CREATE INDEX IF NOT EXISTS idx_swift_input_case_id            -- ✨ NEW
    ON public.swift_input(case_id);                           -- ✨ NEW
CREATE INDEX IF NOT EXISTS idx_swift_input_orgnl_uetr         -- ✨ NEW
    ON public.swift_input(orgnl_uetr);                        -- ✨ NEW
CREATE INDEX IF NOT EXISTS idx_swift_input_orgnl_end_to_end_id -- ✨ NEW
    ON public.swift_input(orgnl_end_to_end_id);               -- ✨ NEW

COMMENT ON TABLE public.swift_input IS
    'Parent table for incoming SWIFT ISO 20022 messages (pacs.008, pacs.009, camt.053, camt.054, camt.056)';

COMMENT ON COLUMN public.swift_input.ntfctn_id IS
    'Notification ID for camt.054 messages (Ntfctn/Id)';
COMMENT ON COLUMN public.swift_input.instd_agt IS
    'Instructed Agent BIC for pacs.009 (InstdAgt/FinInstnId/BICFI)';
COMMENT ON COLUMN public.swift_input.underlying_dbtr_name IS
    'Real customer debtor name from pacs.009 (UndrlygCstmrCdtTrf/Dbtr/Nm)';
COMMENT ON COLUMN public.swift_input.underlying_cdtr_name IS
    'Real customer creditor name from pacs.009 (UndrlygCstmrCdtTrf/Cdtr/Nm)';
COMMENT ON COLUMN public.swift_input.case_id IS
    'Case ID for camt.056 cancellation request (Assgnmt/Id)';
COMMENT ON COLUMN public.swift_input.orgnl_uetr IS
    'Original UETR for camt.056 to link to cancelled transaction';
COMMENT ON COLUMN public.swift_input.cxl_rsn_cd IS
    'Cancellation reason code for camt.056 (CxlRsnInf/Rsn/Cd): DUPL, FRAD, TECH, CUST, etc.';

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

-- Insert default settings (only if table is empty)
INSERT INTO public.swift_settings (folder_in, folder_out, server)
SELECT '/mnt/apng-swift/in', '/mnt/apng-swift/out', 'default'
WHERE NOT EXISTS (SELECT 1 FROM public.swift_settings);

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
    'Balance entries (Bal) from camt.053 statements. Tp/CdOrPrtry/Cd codes: OPBD=Opening Booked, CLBD=Closing Booked, etc.';

-- ============================================================================
-- Child Table 2: swift_stmt_ntry
-- Stores Entry records from camt.053 (BkToCstmrStmt/Stmt/Ntry)
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

-- ============================================================================
-- Child Table 3: swift_entry_tx_dtls
-- Stores Transaction Details from camt.053 (BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls)
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

COMMENT ON TABLE public.swift_entry_tx_dtls IS
    'Transaction details (TxDtls) from camt.053 entries.';

-- ============================================================================
-- ✨ NEW Child Table 4: swift_ntfctn_ntry
-- Stores Entry records from camt.054 (BkToCstmrDbtCdtNtfctn/Ntfctn/Ntry)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_ntfctn_ntry
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    swift_input_id uuid NOT NULL,
    ntfctn_id text COLLATE pg_catalog."default",

    -- Entry identification
    ntry_ref text COLLATE pg_catalog."default",
    acct_svcr_ref text COLLATE pg_catalog."default",

    -- Amount
    amt numeric(18, 2) NOT NULL,
    amt_ccy text COLLATE pg_catalog."default",
    cdt_dbt_ind text COLLATE pg_catalog."default" NOT NULL,

    -- Status
    sts_cd text COLLATE pg_catalog."default" NOT NULL,

    -- Dates
    bookg_dt date,
    val_dt date,

    -- Bank Transaction Code (BkTxCd)
    bk_tx_cd_domn_cd text COLLATE pg_catalog."default",
    bk_tx_cd_fmly_cd text COLLATE pg_catalog."default",
    bk_tx_cd_sub_fmly_cd text COLLATE pg_catalog."default",

    created_at timestamp without time zone DEFAULT now(),

    CONSTRAINT swift_ntfctn_ntry_pkey PRIMARY KEY (id),

    CONSTRAINT swift_ntfctn_ntry_swift_input_fkey
        FOREIGN KEY (swift_input_id)
        REFERENCES public.swift_input (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT swift_ntfctn_ntry_cdt_dbt_ind_check
        CHECK (cdt_dbt_ind IN ('CRDT', 'DBIT')),

    CONSTRAINT swift_ntfctn_ntry_sts_cd_check
        CHECK (sts_cd IN ('BOOK', 'PDNG', 'INFO'))
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_ntry_swift_input_id
    ON public.swift_ntfctn_ntry(swift_input_id);
CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_ntry_ntfctn_id
    ON public.swift_ntfctn_ntry(ntfctn_id);
CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_ntry_ntry_ref
    ON public.swift_ntfctn_ntry(ntry_ref);

COMMENT ON TABLE public.swift_ntfctn_ntry IS
    'Entry records (Ntry) from camt.054 notifications. Each entry represents a debit/credit notification.';

-- ============================================================================
-- ✨ NEW Child Table 5: swift_ntfctn_tx_dtls
-- Stores Transaction Details from camt.054 (BkToCstmrDbtCdtNtfctn/Ntfctn/Ntry/NtryDtls/TxDtls)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_ntfctn_tx_dtls
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    ntry_id uuid NOT NULL,

    -- References
    instr_id text COLLATE pg_catalog."default",
    end_to_end_id text COLLATE pg_catalog."default",
    uetr uuid,

    -- Amount
    amt numeric(18, 2),
    amt_ccy text COLLATE pg_catalog."default",
    cdt_dbt_ind text COLLATE pg_catalog."default",

    -- Related dates
    intr_bk_sttlm_dt date,

    created_at timestamp without time zone DEFAULT now(),

    CONSTRAINT swift_ntfctn_tx_dtls_pkey PRIMARY KEY (id),

    CONSTRAINT swift_ntfctn_tx_dtls_ntry_fkey
        FOREIGN KEY (ntry_id)
        REFERENCES public.swift_ntfctn_ntry (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_tx_dtls_ntry_id
    ON public.swift_ntfctn_tx_dtls(ntry_id);
CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_tx_dtls_uetr
    ON public.swift_ntfctn_tx_dtls(uetr);
CREATE INDEX IF NOT EXISTS idx_swift_ntfctn_tx_dtls_end_to_end_id
    ON public.swift_ntfctn_tx_dtls(end_to_end_id);

COMMENT ON TABLE public.swift_ntfctn_tx_dtls IS
    'Transaction details (TxDtls) from camt.054 notification entries.';

-- ============================================================================
-- PROCESS MANAGEMENT TABLES
-- ============================================================================

-- Process Type Table
CREATE TABLE IF NOT EXISTS public.process_type
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    resource_url text,
    CONSTRAINT process_type_pkey PRIMARY KEY (code)
)
TABLESPACE pg_default;

COMMENT ON TABLE public.process_type IS
    'Process types for different SWIFT message types';

-- Process State Table
CREATE TABLE IF NOT EXISTS public.process_state
(
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_code text NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    color_code text,
    allow_edit boolean DEFAULT false,
    allow_delete boolean DEFAULT false,
    start boolean DEFAULT false,
    CONSTRAINT process_state_pkey PRIMARY KEY (id),
    CONSTRAINT process_state_type_code_code_key UNIQUE (type_code, code),
    CONSTRAINT process_state_type_code_fkey
        FOREIGN KEY (type_code)
        REFERENCES public.process_type (code)
        ON DELETE CASCADE
)
TABLESPACE pg_default;

COMMENT ON TABLE public.process_state IS
    'States for SWIFT message processing workflows';

-- Process Operation Table
CREATE TABLE IF NOT EXISTS public.process_operation
(
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_code text NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    icon text,
    resource_url text,
    availability_condition text,
    cancel boolean DEFAULT false,
    to_state text,
    database text,
    CONSTRAINT process_operation_pkey PRIMARY KEY (id),
    CONSTRAINT process_operation_type_code_code_key UNIQUE (type_code, code),
    CONSTRAINT process_operation_type_code_fkey
        FOREIGN KEY (type_code)
        REFERENCES public.process_type (code)
        ON DELETE CASCADE
)
TABLESPACE pg_default;

COMMENT ON TABLE public.process_operation IS
    'Operations available for SWIFT message processing';

-- Process Operation States (many-to-many)
CREATE TABLE IF NOT EXISTS public.process_operation_states
(
    operation_id uuid NOT NULL,
    state_id uuid NOT NULL,
    CONSTRAINT process_operation_states_pkey PRIMARY KEY (operation_id, state_id),
    CONSTRAINT process_operation_states_operation_fkey
        FOREIGN KEY (operation_id)
        REFERENCES public.process_operation (id)
        ON DELETE CASCADE,
    CONSTRAINT process_operation_states_state_fkey
        FOREIGN KEY (state_id)
        REFERENCES public.process_state (id)
        ON DELETE CASCADE
)
TABLESPACE pg_default;

-- Process Table (instances)
CREATE TABLE IF NOT EXISTS public.process
(
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    swift_input_id uuid NOT NULL,
    state_id uuid NOT NULL,
    CONSTRAINT process_pkey PRIMARY KEY (id),
    CONSTRAINT process_swift_input_fkey
        FOREIGN KEY (swift_input_id)
        REFERENCES public.swift_input (id)
        ON DELETE CASCADE,
    CONSTRAINT process_state_id_fkey
        FOREIGN KEY (state_id)
        REFERENCES public.process_state (id)
)
TABLESPACE pg_default;

COMMENT ON TABLE public.process IS
    'Process instances for each SWIFT message';

-- ============================================================================
-- POPULATE PROCESS MANAGEMENT DATA (FROM BACKUP)
-- ============================================================================

-- Process Types
INSERT INTO public.process_type (code, name_en, name_ru, name_combined, resource_url) VALUES
('pacs.008', 'Customer Credit Transfer', 'Клиентский кредитовый перевод', 'Customer Credit Transfer (Клиентский кредитовый перевод)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}'),
('pacs.009', 'Financial Institution Credit Transfer (COV)', 'Межбанковский кредитовый перевод (покрытие)', 'Financial Institution Credit Transfer (COV) (Межбанковский кредитовый перевод (покрытие))', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}'),
('camt.053', 'Bank to Customer Statement', 'Банковская выписка клиенту', 'Bank to Customer Statement (Банковская выписка клиенту)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}'),
('camt.054', 'Bank to Customer Debit/Credit Notification', 'Уведомление о дебете/кредите', 'Bank to Customer Debit/Credit Notification (Уведомление о дебете/кредите)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}'),
('camt.056', 'FI to FI Payment Cancellation Request', 'Запрос на отмену платежа', 'FI to FI Payment Cancellation Request (Запрос на отмену платежа)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}')
ON CONFLICT (code) DO NOTHING;

-- Process States (using UUIDs from backup)
INSERT INTO public.process_state (id, type_code, code, name_en, name_ru, name_combined, color_code, allow_edit, allow_delete, start) VALUES
('b164a0c1-9544-47c4-84a5-d858d29714df', 'pacs.009', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true, true),
('3d62da83-1ec1-4ce8-8213-f3869eb7fcdd', 'camt.053', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true, true),
('0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9', 'camt.054', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true, true),
('895acd9f-b1d8-4844-ade2-713c9b92ebfd', 'camt.056', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true, true),
('7527efd9-007e-4710-afc7-7fc9426c726a', 'pacs.009', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false, false),
('00c57ee4-58ea-47b3-9804-497773cdd339', 'camt.054', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false, false),
('815c1662-3351-488a-8f40-ddee60b0a3a3', 'camt.056', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false, false),
('088d04ed-28d0-4447-b7f6-defb08cbce1a', 'pacs.008', 'PAYMENT_CREATED', 'Payment Created', 'Платеж создан', 'Payment Created (Платеж создан)', '#008000', false, false, false),
('f8c40da3-cf4e-42ec-a641-53eeb7208448', 'pacs.008', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true, true),
('9f676606-51f2-4bbb-b220-88ae23f166c2', 'pacs.008', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#dbbbb8', false, false, false),
('cf11183a-fe76-43e8-8f8f-aa998e83f26a', 'camt.053', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#71f093', false, false, false)
ON CONFLICT (id) DO NOTHING;

-- Process Operations (using UUIDs from backup)
INSERT INTO public.process_operation (id, type_code, code, name_en, name_ru, name_combined, icon, resource_url, availability_condition, cancel, to_state, database) VALUES
('e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11', 'pacs.008', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'Mark as Processed (Отметить как обработанный)', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
('04497cef-080c-41e4-8636-8b571bf9afb3', 'pacs.009', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'Mark as Processed (Отметить как обработанный)', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
('3630a61c-2c21-44f1-9ea7-f7075327b14b', 'camt.053', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'Mark as Processed (Отметить как обработанный)', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
('16d9608e-db6e-499e-ba57-2a3bffbf6481', 'camt.054', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'Mark as Processed (Отметить как обработанный)', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
('ecaca1ee-dc5b-4c1e-87f9-79b488e09525', 'camt.056', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'Mark as Processed (Отметить как обработанный)', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
('50e4a5c8-f510-4e45-bac3-f037c81545a6', 'pacs.008', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'Cancel Processing (Отменить обработку)', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
('2405f16a-fcdb-4ef7-968e-7a41d5284e3e', 'pacs.009', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'Cancel Processing (Отменить обработку)', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
('f159119f-7ea1-46e9-8339-ba6714f89174', 'camt.053', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'Cancel Processing (Отменить обработку)', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
('eae080aa-61a6-4bd8-8056-1e53019188b5', 'camt.054', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'Cancel Processing (Отменить обработку)', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
('ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4', 'camt.056', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'Cancel Processing (Отменить обработку)', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
('cd28fb8c-d732-4195-8c62-93001648552e', 'pacs.008', 'CANCEL_PAYMENT', 'Cancel Payment Creation', 'Отменить создание платежа', 'Cancel Payment Creation (Отменить создание платежа)', 'cancel', NULL, '{"target_state": "LOADED", "available_in_states": ["PAYMENT_CREATED"]}', true, 'LOADED', NULL),
('2808dd8d-23c6-466d-b50a-d999268255ab', 'pacs.008', 'CREATE_PAYMENT', 'Create Payment', 'Создать платеж', 'Create Payment (Создать платеж)', 'payment', 'declare  p_dep_id int := 100;  p_id varchar2(250) := :id;  p_test_xml varchar2(4000):= :xml;begin\n  :out_payment_pk := p_dep_id||'',''||p_id;end;', '{"target_state": "PAYMENT_CREATED", "available_in_states": ["LOADED"]}', false, 'PAYMENT_CREATED', NULL)
ON CONFLICT (id) DO NOTHING;

-- Process Operation States (many-to-many relationships)
INSERT INTO public.process_operation_states (operation_id, state_id) VALUES
('e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11', 'f8c40da3-cf4e-42ec-a641-53eeb7208448'),
('04497cef-080c-41e4-8636-8b571bf9afb3', 'b164a0c1-9544-47c4-84a5-d858d29714df'),
('3630a61c-2c21-44f1-9ea7-f7075327b14b', '3d62da83-1ec1-4ce8-8213-f3869eb7fcdd'),
('16d9608e-db6e-499e-ba57-2a3bffbf6481', '0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9'),
('ecaca1ee-dc5b-4c1e-87f9-79b488e09525', '895acd9f-b1d8-4844-ade2-713c9b92ebfd'),
('50e4a5c8-f510-4e45-bac3-f037c81545a6', '9f676606-51f2-4bbb-b220-88ae23f166c2'),
('2405f16a-fcdb-4ef7-968e-7a41d5284e3e', '7527efd9-007e-4710-afc7-7fc9426c726a'),
('f159119f-7ea1-46e9-8339-ba6714f89174', 'cf11183a-fe76-43e8-8f8f-aa998e83f26a'),
('eae080aa-61a6-4bd8-8056-1e53019188b5', '00c57ee4-58ea-47b3-9804-497773cdd339'),
('ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4', '815c1662-3351-488a-8f40-ddee60b0a3a3'),
('cd28fb8c-d732-4195-8c62-93001648552e', '088d04ed-28d0-4447-b7f6-defb08cbce1a'),
('2808dd8d-23c6-466d-b50a-d999268255ab', 'f8c40da3-cf4e-42ec-a641-53eeb7208448')
ON CONFLICT (operation_id, state_id) DO NOTHING;

-- ============================================================================
-- Permissions
-- ============================================================================
ALTER TABLE IF EXISTS public.swift_input OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_settings OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_out_fields OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_stmt_bal OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_stmt_ntry OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_entry_tx_dtls OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_ntfctn_ntry OWNER TO postgres;    -- ✨ NEW
ALTER TABLE IF EXISTS public.swift_ntfctn_tx_dtls OWNER TO postgres; -- ✨ NEW
ALTER TABLE IF EXISTS public.process_type OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_state OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation_states OWNER TO postgres;
ALTER TABLE IF EXISTS public.process OWNER TO postgres;

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
GRANT ALL ON TABLE public.swift_ntfctn_ntry TO apng;    -- ✨ NEW
GRANT ALL ON TABLE public.swift_ntfctn_ntry TO postgres; -- ✨ NEW
GRANT ALL ON TABLE public.swift_ntfctn_tx_dtls TO apng;  -- ✨ NEW
GRANT ALL ON TABLE public.swift_ntfctn_tx_dtls TO postgres; -- ✨ NEW
GRANT ALL ON TABLE public.process_type TO apng;
GRANT ALL ON TABLE public.process_type TO postgres;
GRANT ALL ON TABLE public.process_state TO apng;
GRANT ALL ON TABLE public.process_state TO postgres;
GRANT ALL ON TABLE public.process_operation TO apng;
GRANT ALL ON TABLE public.process_operation TO postgres;
GRANT ALL ON TABLE public.process_operation_states TO apng;
GRANT ALL ON TABLE public.process_operation_states TO postgres;
GRANT ALL ON TABLE public.process TO apng;
GRANT ALL ON TABLE public.process TO postgres;

-- ============================================================================
-- Summary of Changes
-- ============================================================================
-- ✨ NEW FIELDS IN swift_input (19 fields added):
--    - ntfctn_id (camt.054)
--    - instd_agt, instd_agt_name (pacs.009)
--    - underlying_dbtr_name, underlying_dbtr_acc, underlying_dbtr_agt (pacs.009)
--    - underlying_cdtr_name, underlying_cdtr_acc, underlying_cdtr_agt (pacs.009)
--    - case_id, case_assgnr (camt.056)
--    - orgnl_msg_id, orgnl_msg_nm_id, orgnl_instr_id (camt.056)
--    - orgnl_end_to_end_id, orgnl_tx_id, orgnl_uetr (camt.056)
--    - cxl_rsn_cd, cxl_rsn_addtl_inf (camt.056)
--
-- ✨ NEW TABLES (2 tables):
--    - swift_ntfctn_ntry (for camt.054 notifications)
--    - swift_ntfctn_tx_dtls (for camt.054 transaction details)
--
-- ✅ PRESERVED from backup.sql:
--    - All existing fields in swift_input (pk, snd_mid_bank_acc_val kept)
--    - All process_type, process_state, process_operation data with original UUIDs
--    - All process_operation_states relationships
--    - Table process (structure only, no data inserted)
-- ============================================================================


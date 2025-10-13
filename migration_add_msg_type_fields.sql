-- ============================================================================
-- Migration: Add msg_type and camt.053 fields to swift_input
-- Date: 2025-10-13
-- Description: Adds message type detection and camt.053 specific fields
-- ============================================================================

-- Add msg_type field with constraint
ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS msg_type text COLLATE pg_catalog."default";

-- Add constraint for msg_type
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'swift_input_msg_type_check'
    ) THEN
        ALTER TABLE public.swift_input
            ADD CONSTRAINT swift_input_msg_type_check
            CHECK (msg_type IN ('pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056', NULL));
    END IF;
END $$;

-- Add message identification fields
ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS msg_id text COLLATE pg_catalog."default";

ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS msg_def_idr text COLLATE pg_catalog."default";

ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS cre_dt_tm timestamp without time zone;

-- Add statement identification fields (for camt.053/054)
ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS stmt_id text COLLATE pg_catalog."default";

ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS elctrnc_seq_nb numeric;

-- Add account information fields
ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS acct_id text COLLATE pg_catalog."default";

ALTER TABLE public.swift_input
    ADD COLUMN IF NOT EXISTS acct_ccy text COLLATE pg_catalog."default";

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_swift_input_msg_id
    ON public.swift_input(msg_id);

CREATE INDEX IF NOT EXISTS idx_swift_input_msg_type
    ON public.swift_input(msg_type);

CREATE INDEX IF NOT EXISTS idx_swift_input_stmt_id
    ON public.swift_input(stmt_id);

-- Grant permissions (if role exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'apng') THEN
        GRANT ALL ON TABLE public.swift_input TO apng;
    END IF;
END $$;

-- ============================================================================
-- Insert default settings if swift_settings table is empty
-- ============================================================================
INSERT INTO public.swift_settings (folder_in, folder_out, server)
SELECT '/mnt/apng-swift/in', '/mnt/apng-swift/out', 'default'
WHERE NOT EXISTS (SELECT 1 FROM public.swift_settings LIMIT 1);

-- Update comment
COMMENT ON TABLE public.swift_input IS
    'Parent table for incoming SWIFT ISO 20022 messages (pacs.008, pacs.009, camt.053, camt.054, camt.056)';

COMMENT ON COLUMN public.swift_input.msg_type IS
    'Message type: pacs.008, pacs.009, camt.053, camt.054, camt.056';

COMMENT ON COLUMN public.swift_input.msg_id IS
    'Message ID from GrpHdr/MsgId';

COMMENT ON COLUMN public.swift_input.stmt_id IS
    'Statement ID (for camt.053: Stmt/Id)';

COMMENT ON COLUMN public.swift_input.elctrnc_seq_nb IS
    'Electronic sequence number (for camt.053: Stmt/ElctrncSeqNb)';

COMMENT ON COLUMN public.swift_input.acct_id IS
    'Account ID (for camt.053: Stmt/Acct/Id)';

COMMENT ON COLUMN public.swift_input.acct_ccy IS
    'Account currency (for camt.053: Stmt/Acct/Ccy)';

-- ============================================================================
-- Verification queries (uncomment to check results)
-- ============================================================================

-- Check if columns exist
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'swift_input'
-- AND column_name IN ('msg_type', 'msg_id', 'stmt_id', 'elctrnc_seq_nb', 'acct_id', 'acct_ccy')
-- ORDER BY column_name;

-- Check indexes
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'swift_input'
-- AND indexname LIKE 'idx_swift_input_msg%'
-- ORDER BY indexname;

-- Check constraint
-- SELECT conname, pg_get_constraintdef(oid)
-- FROM pg_constraint
-- WHERE conrelid = 'public.swift_input'::regclass
-- AND conname = 'swift_input_msg_type_check';

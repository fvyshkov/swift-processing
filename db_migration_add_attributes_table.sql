-- ============================================================================
-- Migration: Add attributes_table field to process_type and modify process table
-- Date: 2025-10-26
-- ============================================================================

-- 1. Add attributes_table field to process_type table
ALTER TABLE public.process_type 
ADD COLUMN IF NOT EXISTS attributes_table text;

COMMENT ON COLUMN public.process_type.attributes_table IS
    'Table name where document attributes for this type are stored';

-- 2. Update existing process types with their corresponding tables
UPDATE public.process_type SET attributes_table = 'swift_input' WHERE code IN ('pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056');

-- 3. Modify process table - add doc_id column
ALTER TABLE public.process 
ADD COLUMN IF NOT EXISTS doc_id uuid;

-- 4. Copy data from swift_input_id to doc_id
UPDATE public.process SET doc_id = swift_input_id WHERE doc_id IS NULL;

-- 5. Drop foreign key constraint and old column
ALTER TABLE public.process 
DROP CONSTRAINT IF EXISTS process_swift_input_fkey;

ALTER TABLE public.process 
DROP COLUMN IF EXISTS swift_input_id;

-- 6. Make doc_id required
ALTER TABLE public.process 
ALTER COLUMN doc_id SET NOT NULL;

-- 7. Add comment for doc_id
COMMENT ON COLUMN public.process.doc_id IS
    'Document ID - can reference records in different tables based on process type';

-- 8. Recreate index for doc_id
CREATE INDEX IF NOT EXISTS idx_process_doc_id ON public.process(doc_id);

-- ============================================================================
-- Summary of changes:
-- 1. Added attributes_table field to process_type table
-- 2. Updated existing process types to reference swift_input table
-- 3. Replaced swift_input_id with doc_id in process table (no FK constraint)
-- ============================================================================

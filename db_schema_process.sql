-- ============================================================================
-- Document State Management System Schema
-- Three reference tables: process_type, process_state, process_operation
-- ============================================================================

-- Drop existing tables (in correct order due to FK constraints)
DROP TABLE IF EXISTS public.process_operation_states CASCADE;
DROP TABLE IF EXISTS public.process_operation CASCADE;
DROP TABLE IF EXISTS public.process_state CASCADE;
DROP TABLE IF EXISTS public.process_type CASCADE;

-- ============================================================================
-- Table 1: process_type - Document Types Reference
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.process_type
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    resource_url text,
    CONSTRAINT process_type_pkey PRIMARY KEY (code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.process_type IS
    'Document types reference - defines types of documents that can be processed';

COMMENT ON COLUMN public.process_type.code IS
    'Document type code (primary key)';
COMMENT ON COLUMN public.process_type.name_en IS
    'English name of document type';
COMMENT ON COLUMN public.process_type.name_ru IS
    'Russian name of document type';
COMMENT ON COLUMN public.process_type.name_combined IS
    'Combined display name (English + Russian)';
COMMENT ON COLUMN public.process_type.resource_url IS
    'Resource URL implementing document display by key';

CREATE INDEX IF NOT EXISTS idx_process_type_name_en
    ON public.process_type(name_en);

-- ============================================================================
-- Table 2: process_state - Document States Reference
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.process_state
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    type_code text NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    color_code text,
    allow_edit boolean DEFAULT false,
    allow_delete boolean DEFAULT false,

    CONSTRAINT process_state_pkey PRIMARY KEY (id),

    CONSTRAINT process_state_type_fkey
        FOREIGN KEY (type_code)
        REFERENCES public.process_type (code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT process_state_type_code_unique UNIQUE (type_code, code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.process_state IS
    'Document states reference - defines possible states for each document type';

COMMENT ON COLUMN public.process_state.id IS
    'Unique state identifier (UUID)';
COMMENT ON COLUMN public.process_state.type_code IS
    'Reference to document type (FK to process_type)';
COMMENT ON COLUMN public.process_state.code IS
    'State code (unique within type)';
COMMENT ON COLUMN public.process_state.name_en IS
    'English name of state';
COMMENT ON COLUMN public.process_state.name_ru IS
    'Russian name of state';
COMMENT ON COLUMN public.process_state.name_combined IS
    'Combined display name (English + Russian)';
COMMENT ON COLUMN public.process_state.color_code IS
    'Color code for UI display (hex format: #RRGGBB)';
COMMENT ON COLUMN public.process_state.allow_edit IS
    'Flag indicating if document can be edited in this state';
COMMENT ON COLUMN public.process_state.allow_delete IS
    'Flag indicating if document can be deleted in this state';

CREATE INDEX IF NOT EXISTS idx_process_state_type_code
    ON public.process_state(type_code);
CREATE INDEX IF NOT EXISTS idx_process_state_type_code_code
    ON public.process_state(type_code, code);

-- ============================================================================
-- Table 3: process_operation - Document Operations Reference
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.process_operation
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    type_code text NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    icon text,
    resource_url text,
    availability_condition text,

    CONSTRAINT process_operation_pkey PRIMARY KEY (id),

    CONSTRAINT process_operation_type_fkey
        FOREIGN KEY (type_code)
        REFERENCES public.process_type (code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT process_operation_code_unique UNIQUE (type_code, code)
) TABLESPACE pg_default;

COMMENT ON TABLE public.process_operation IS
    'Document operations reference - defines actions available for document types';

COMMENT ON COLUMN public.process_operation.id IS
    'Unique operation identifier (UUID)';
COMMENT ON COLUMN public.process_operation.type_code IS
    'Reference to document type (FK to process_type)';
COMMENT ON COLUMN public.process_operation.code IS
    'Operation code (unique within type)';
COMMENT ON COLUMN public.process_operation.name_en IS
    'English name of operation';
COMMENT ON COLUMN public.process_operation.name_ru IS
    'Russian name of operation';
COMMENT ON COLUMN public.process_operation.name_combined IS
    'Combined display name (English + Russian)';
COMMENT ON COLUMN public.process_operation.icon IS
    'Icon identifier for UI display';
COMMENT ON COLUMN public.process_operation.resource_url IS
    'Resource URL implementing the operation (receives document key and type)';
COMMENT ON COLUMN public.process_operation.availability_condition IS
    'JSON with conditions for operation availability based on document state';

CREATE INDEX IF NOT EXISTS idx_process_operation_type_code
    ON public.process_operation(type_code);
CREATE INDEX IF NOT EXISTS idx_process_operation_code
    ON public.process_operation(type_code, code);

-- ============================================================================
-- Table 4: process_operation_states - Many-to-many relation
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.process_operation_states
(
    operation_id uuid NOT NULL,
    state_id uuid NOT NULL,

    CONSTRAINT process_operation_states_pkey PRIMARY KEY (operation_id, state_id),

    CONSTRAINT process_operation_states_operation_fkey
        FOREIGN KEY (operation_id)
        REFERENCES public.process_operation (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT process_operation_states_state_fkey
        FOREIGN KEY (state_id)
        REFERENCES public.process_state (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) TABLESPACE pg_default;

COMMENT ON TABLE public.process_operation_states IS
    'Links operations to states where they are available';

COMMENT ON COLUMN public.process_operation_states.operation_id IS
    'Reference to operation (FK to process_operation)';
COMMENT ON COLUMN public.process_operation_states.state_id IS
    'Reference to state (FK to process_state)';

CREATE INDEX IF NOT EXISTS idx_process_operation_states_operation_id
    ON public.process_operation_states(operation_id);
CREATE INDEX IF NOT EXISTS idx_process_operation_states_state_id
    ON public.process_operation_states(state_id);

-- ============================================================================
-- Permissions
-- ============================================================================
ALTER TABLE IF EXISTS public.process_type OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_state OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation_states OWNER TO postgres;

GRANT ALL ON TABLE public.process_type TO apng;
GRANT ALL ON TABLE public.process_type TO postgres;
GRANT ALL ON TABLE public.process_state TO apng;
GRANT ALL ON TABLE public.process_state TO postgres;
GRANT ALL ON TABLE public.process_operation TO apng;
GRANT ALL ON TABLE public.process_operation TO postgres;
GRANT ALL ON TABLE public.process_operation_states TO apng;
GRANT ALL ON TABLE public.process_operation_states TO postgres;

-- ============================================================================
-- Initial Data Population from ref_message_types
-- ============================================================================
INSERT INTO public.process_type (code, name_en, name_ru, name_combined, resource_url)
SELECT
    code,
    name_en,
    name_ru,
    name_combined,
    '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}' as resource_url
FROM public.ref_message_types
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Reference Data Summary
-- ============================================================================
-- Total records inserted:
-- Document Types: 5 (from ref_message_types)
-- ============================================================================

-- ============================================================================
-- SWIFT Process Management System - COMPLETE SETUP
-- Creates tables, states, and operations from scratch
-- ============================================================================
-- Usage: psql -U postgres -d apng -f setup_process_system.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- DROP EXISTING TABLES
-- ============================================================================
DROP TABLE IF EXISTS public.process_operation_states CASCADE;
DROP TABLE IF EXISTS public.process_operation CASCADE;
DROP TABLE IF EXISTS public.process_state CASCADE;
DROP TABLE IF EXISTS public.process_type CASCADE;

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

-- Table 1: process_type - Document Types
CREATE TABLE public.process_type
(
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    resource_url text,
    CONSTRAINT process_type_pkey PRIMARY KEY (code)
);

CREATE INDEX idx_process_type_name_en ON public.process_type(name_en);

-- Table 2: process_state - Document States
CREATE TABLE public.process_state
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
    CONSTRAINT process_state_type_fkey FOREIGN KEY (type_code)
        REFERENCES public.process_type (code) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT process_state_type_code_unique UNIQUE (type_code, code)
);

CREATE INDEX idx_process_state_type_code ON public.process_state(type_code);
CREATE INDEX idx_process_state_type_code_code ON public.process_state(type_code, code);

-- Table 3: process_operation - Operations
CREATE TABLE public.process_operation
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
    cancel boolean DEFAULT false,
    to_state text,
    database text,

    CONSTRAINT process_operation_pkey PRIMARY KEY (id),
    CONSTRAINT process_operation_type_fkey FOREIGN KEY (type_code)
        REFERENCES public.process_type (code) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT process_operation_code_unique UNIQUE (type_code, code)
);

CREATE INDEX idx_process_operation_type_code ON public.process_operation(type_code);
CREATE INDEX idx_process_operation_code ON public.process_operation(type_code, code);
CREATE INDEX idx_process_operation_cancel ON public.process_operation(cancel);
CREATE INDEX idx_process_operation_to_state ON public.process_operation(to_state) WHERE to_state IS NOT NULL;

-- Table 4: process_operation_states - Links
CREATE TABLE public.process_operation_states
(
    operation_id uuid NOT NULL,
    state_id uuid NOT NULL,

    CONSTRAINT process_operation_states_pkey PRIMARY KEY (operation_id, state_id),
    CONSTRAINT process_operation_states_operation_fkey FOREIGN KEY (operation_id)
        REFERENCES public.process_operation (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT process_operation_states_state_fkey FOREIGN KEY (state_id)
        REFERENCES public.process_state (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_process_operation_states_operation_id ON public.process_operation_states(operation_id);
CREATE INDEX idx_process_operation_states_state_id ON public.process_operation_states(state_id);

-- Permissions
ALTER TABLE public.process_type OWNER TO postgres;
ALTER TABLE public.process_state OWNER TO postgres;
ALTER TABLE public.process_operation OWNER TO postgres;
ALTER TABLE public.process_operation_states OWNER TO postgres;

GRANT ALL ON TABLE public.process_type TO apng;
GRANT ALL ON TABLE public.process_state TO apng;
GRANT ALL ON TABLE public.process_operation TO apng;
GRANT ALL ON TABLE public.process_operation_states TO apng;

-- ============================================================================
-- POPULATE: Document Types (from ref_message_types)
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
-- POPULATE: States
-- ============================================================================

-- State: LOADED (all types)
INSERT INTO public.process_state (type_code, code, name_en, name_ru, name_combined, color_code, allow_edit, allow_delete)
VALUES 
    ('pacs.008', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true),
    ('pacs.009', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true),
    ('camt.053', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true),
    ('camt.054', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true),
    ('camt.056', 'LOADED', 'Loaded', 'Загружен', 'Loaded (Загружен)', '#FF8C00', true, true)
ON CONFLICT (type_code, code) DO NOTHING;

-- State: PROCESSED (all types)
INSERT INTO public.process_state (type_code, code, name_en, name_ru, name_combined, color_code, allow_edit, allow_delete)
VALUES 
    ('pacs.008', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false),
    ('pacs.009', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false),
    ('camt.053', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false),
    ('camt.054', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false),
    ('camt.056', 'PROCESSED', 'Processed', 'Обработан', 'Processed (Обработан)', '#8B0000', false, false)
ON CONFLICT (type_code, code) DO NOTHING;

-- State: PAYMENT_CREATED (pacs.008 only)
INSERT INTO public.process_state (type_code, code, name_en, name_ru, name_combined, color_code, allow_edit, allow_delete)
VALUES 
    ('pacs.008', 'PAYMENT_CREATED', 'Payment Created', 'Платеж создан', 'Payment Created (Платеж создан)', '#008000', false, false)
ON CONFLICT (type_code, code) DO NOTHING;

-- ============================================================================
-- POPULATE: Operations
-- ============================================================================

-- Operation: MARK_AS_PROCESSED (all types)
INSERT INTO public.process_operation (type_code, code, name_en, name_ru, name_combined, icon, resource_url, availability_condition, cancel, to_state, database)
VALUES 
    ('pacs.008', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 
     'Mark as Processed (Отметить как обработанный)', 'check', NULL,
     '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
    ('pacs.009', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 
     'Mark as Processed (Отметить как обработанный)', 'check', NULL,
     '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
    ('camt.053', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 
     'Mark as Processed (Отметить как обработанный)', 'check', NULL,
     '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
    ('camt.054', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 
     'Mark as Processed (Отметить как обработанный)', 'check', NULL,
     '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL),
    ('camt.056', 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 
     'Mark as Processed (Отметить как обработанный)', 'check', NULL,
     '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'PROCESSED', NULL)
ON CONFLICT (type_code, code) DO NOTHING;

-- Operation: CANCEL_PROCESSING (all types)
INSERT INTO public.process_operation (type_code, code, name_en, name_ru, name_combined, icon, resource_url, availability_condition, cancel, to_state, database)
VALUES 
    ('pacs.008', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 
     'Cancel Processing (Отменить обработку)', 'undo', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
    ('pacs.009', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 
     'Cancel Processing (Отменить обработку)', 'undo', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
    ('camt.053', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 
     'Cancel Processing (Отменить обработку)', 'undo', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
    ('camt.054', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 
     'Cancel Processing (Отменить обработку)', 'undo', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL),
    ('camt.056', 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 
     'Cancel Processing (Отменить обработку)', 'undo', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'LOADED', NULL)
ON CONFLICT (type_code, code) DO NOTHING;

-- Operation: CREATE_PAYMENT (pacs.008 only)
INSERT INTO public.process_operation (type_code, code, name_en, name_ru, name_combined, icon, resource_url, availability_condition, cancel, to_state, database)
VALUES 
    ('pacs.008', 'CREATE_PAYMENT', 'Create Payment', 'Создать платеж', 
     'Create Payment (Создать платеж)', 'payment', NULL,
     '{"target_state": "PAYMENT_CREATED", "available_in_states": ["LOADED"]}', false, 'PAYMENT_CREATED', NULL)
ON CONFLICT (type_code, code) DO NOTHING;

-- Operation: CANCEL_PAYMENT (pacs.008 only)
INSERT INTO public.process_operation (type_code, code, name_en, name_ru, name_combined, icon, resource_url, availability_condition, cancel, to_state, database)
VALUES 
    ('pacs.008', 'CANCEL_PAYMENT', 'Cancel Payment Creation', 'Отменить создание платежа', 
     'Cancel Payment Creation (Отменить создание платежа)', 'cancel', NULL,
     '{"target_state": "LOADED", "available_in_states": ["PAYMENT_CREATED"]}', true, 'LOADED', NULL)
ON CONFLICT (type_code, code) DO NOTHING;

-- ============================================================================
-- LINK: Operations to States
-- ============================================================================

-- Link MARK_AS_PROCESSED to LOADED state
INSERT INTO process_operation_states (operation_id, state_id)
SELECT po.id, ps.id
FROM process_operation po
JOIN process_state ps ON ps.type_code = po.type_code AND ps.code = 'LOADED'
WHERE po.code = 'MARK_AS_PROCESSED'
ON CONFLICT (operation_id, state_id) DO NOTHING;

-- Link CANCEL_PROCESSING to PROCESSED state
INSERT INTO process_operation_states (operation_id, state_id)
SELECT po.id, ps.id
FROM process_operation po
JOIN process_state ps ON ps.type_code = po.type_code AND ps.code = 'PROCESSED'
WHERE po.code = 'CANCEL_PROCESSING'
ON CONFLICT (operation_id, state_id) DO NOTHING;

-- Link CREATE_PAYMENT to LOADED state (pacs.008)
INSERT INTO process_operation_states (operation_id, state_id)
SELECT po.id, ps.id
FROM process_operation po
JOIN process_state ps ON ps.type_code = po.type_code AND ps.code = 'LOADED'
WHERE po.code = 'CREATE_PAYMENT' AND po.type_code = 'pacs.008'
ON CONFLICT (operation_id, state_id) DO NOTHING;

-- Link CANCEL_PAYMENT to PAYMENT_CREATED state (pacs.008)
INSERT INTO process_operation_states (operation_id, state_id)
SELECT po.id, ps.id
FROM process_operation po
JOIN process_state ps ON ps.type_code = po.type_code AND ps.code = 'PAYMENT_CREATED'
WHERE po.code = 'CANCEL_PAYMENT' AND po.type_code = 'pacs.008'
ON CONFLICT (operation_id, state_id) DO NOTHING;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Document Types' as item, COUNT(*) as count FROM process_type
UNION ALL
SELECT 'States', COUNT(*) FROM process_state
UNION ALL
SELECT 'Operations', COUNT(*) FROM process_operation
UNION ALL
SELECT 'Operation-State Links', COUNT(*) FROM process_operation_states;

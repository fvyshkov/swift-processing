-- ============================================================================
-- Process Management Tables - Structure and Reference Data
-- ============================================================================

-- Drop existing tables (in correct order due to FK constraints)
DROP TABLE IF EXISTS public.swift_settings CASCADE;
DROP TABLE IF EXISTS public.process_operation_states CASCADE;
DROP TABLE IF EXISTS public.process CASCADE;
DROP TABLE IF EXISTS public.process_operation CASCADE;
DROP TABLE IF EXISTS public.process_state CASCADE;
DROP TABLE IF EXISTS public.process_type CASCADE;

-- ============================================================================
-- Process Type Table
-- ============================================================================
CREATE TABLE public.process_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    attributes_table text,
    parent_id uuid,
    CONSTRAINT process_type_pkey PRIMARY KEY (id),
    CONSTRAINT process_type_code_key UNIQUE (code),
    CONSTRAINT process_type_parent_id_fkey 
        FOREIGN KEY (parent_id) 
        REFERENCES public.process_type(id)
        ON DELETE SET NULL
);

COMMENT ON TABLE public.process_type IS 'Process types for different SWIFT message types with hierarchy support';
COMMENT ON COLUMN public.process_type.id IS 'Unique identifier for process type';
COMMENT ON COLUMN public.process_type.code IS 'Process type code (e.g., pacs.008, camt.053)';
COMMENT ON COLUMN public.process_type.attributes_table IS 'Table name where document attributes for this type are stored';
COMMENT ON COLUMN public.process_type.parent_id IS 'Reference to parent process type for hierarchy';


-- Create indexes for process_type
CREATE INDEX idx_process_type_code ON public.process_type(code);
CREATE INDEX idx_process_type_parent_id ON public.process_type(parent_id);

-- ============================================================================
-- Process State Table
-- ============================================================================
CREATE TABLE public.process_state (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_id uuid NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    color_code text,
    allow_edit boolean DEFAULT false,
    allow_delete boolean DEFAULT false,
    start boolean DEFAULT false,
    CONSTRAINT process_state_pkey PRIMARY KEY (id),
    CONSTRAINT process_state_type_id_code_key UNIQUE (type_id, code),
    CONSTRAINT process_state_type_id_fkey 
        FOREIGN KEY (type_id) 
        REFERENCES public.process_type(id) 
        ON DELETE CASCADE
);

COMMENT ON TABLE public.process_state IS 'States for SWIFT message processing workflows';

-- ============================================================================
-- Process Operation Table
-- ============================================================================
CREATE TABLE public.process_operation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_id uuid NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    icon text,
    resource_url text,
    availability_condition text,
    cancel boolean DEFAULT false,
    move_to_state_script text,
    workflow text,
    database text,
    CONSTRAINT process_operation_pkey PRIMARY KEY (id),
    CONSTRAINT process_operation_type_id_code_key UNIQUE (type_id, code),
    CONSTRAINT process_operation_type_id_fkey 
        FOREIGN KEY (type_id) 
        REFERENCES public.process_type(id) 
        ON DELETE CASCADE
);

COMMENT ON TABLE public.process_operation IS 'Operations available for SWIFT message processing';
COMMENT ON COLUMN public.process_operation.move_to_state_script IS 'Python script that returns the target state ID based on document attributes';

-- ============================================================================
-- Process Operation States (many-to-many)
-- ============================================================================
CREATE TABLE public.process_operation_states (
    operation_id uuid NOT NULL,
    state_id uuid NOT NULL,
    CONSTRAINT process_operation_states_pkey PRIMARY KEY (operation_id, state_id),
    CONSTRAINT process_operation_states_operation_fkey 
        FOREIGN KEY (operation_id) 
        REFERENCES public.process_operation(id) 
        ON DELETE CASCADE,
    CONSTRAINT process_operation_states_state_fkey 
        FOREIGN KEY (state_id) 
        REFERENCES public.process_state(id) 
        ON DELETE CASCADE
);

-- ============================================================================
-- Process Table (instances) - STRUCTURE ONLY, NO DATA
-- ============================================================================
CREATE TABLE public.process (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    doc_id uuid NOT NULL,
    state_id uuid NOT NULL,
    CONSTRAINT process_pkey PRIMARY KEY (id),
    CONSTRAINT process_state_id_fkey 
        FOREIGN KEY (state_id) 
        REFERENCES public.process_state(id)
);

COMMENT ON TABLE public.process IS 'Process instances for each SWIFT message';
COMMENT ON COLUMN public.process.doc_id IS 'Document ID - can reference records in different tables based on process type';

CREATE INDEX idx_process_doc_id ON public.process(doc_id);

-- ============================================================================
-- Swift Settings Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.swift_settings (
    id serial PRIMARY KEY,
    folder_in text,
    folder_out text,
    folder_unprocessed text,
    server text
);

-- ============================================================================
-- Reference Data
-- ============================================================================

-- Process Types (all at first level - parent_id is NULL)
INSERT INTO public.process_type (code, name_en, name_ru, attributes_table, parent_id) VALUES
('pacs.008', 'Customer Credit Transfer', 'Клиентский кредитовый перевод', 'swift_input', NULL),
('pacs.009', 'Financial Institution Credit Transfer (COV)', 'Межбанковский кредитовый перевод (покрытие)', 'swift_input', NULL),
('camt.053', 'Bank to Customer Statement', 'Банковская выписка клиенту', 'swift_input', NULL),
('camt.054', 'Bank to Customer Debit/Credit Notification', 'Уведомление о дебете/кредите', 'swift_input', NULL),
('camt.056', 'FI to FI Payment Cancellation Request', 'Запрос на отмену платежа', 'swift_input', NULL),
('TRN', 'Transaction', 'Транзакция (строка выписки)', 'swift_stmt_ntry', NULL)
ON CONFLICT (code) DO NOTHING;

-- Process States (using UUIDs from backup)
INSERT INTO public.process_state (id, type_id, code, name_en, name_ru, color_code, allow_edit, allow_delete, start) VALUES
-- pacs.008 states
('f8c40da3-cf4e-42ec-a641-53eeb7208448', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'LOADED', 'Loaded', 'Загружен', '#ccdec5', true, true, true),
('9f676606-51f2-4bbb-b220-88ae23f166c2', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'PROCESSED', 'Processed', 'Обработан', '#8bd672', false, false, false),
('088d04ed-28d0-4447-b7f6-defb08cbce1a', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'PAYMENT_CREATED', 'Payment Created', 'Платеж создан', '#008000', false, false, false),
-- pacs.009 states
('b164a0c1-9544-47c4-84a5-d858d29714df', (SELECT id FROM process_type WHERE code = 'pacs.009'), 'LOADED', 'Loaded', 'Загружен', '#FF8C00', true, true, true),
('7527efd9-007e-4710-afc7-7fc9426c726a', (SELECT id FROM process_type WHERE code = 'pacs.009'), 'PROCESSED', 'Processed', 'Обработан', '#8B0000', false, false, false),
-- camt.053 states
('3d62da83-1ec1-4ce8-8213-f3869eb7fcdd', (SELECT id FROM process_type WHERE code = 'camt.053'), 'LOADED', 'Loaded', 'Загружен', '#FF8C00', true, true, true),
('cf11183a-fe76-43e8-8f8f-aa998e83f26a', (SELECT id FROM process_type WHERE code = 'camt.053'), 'PROCESSED', 'Processed', 'Обработан', '#71f093', false, false, false),
-- camt.054 states
('0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9', (SELECT id FROM process_type WHERE code = 'camt.054'), 'LOADED', 'Loaded', 'Загружен', '#FF8C00', true, true, true),
('00c57ee4-58ea-47b3-9804-497773cdd339', (SELECT id FROM process_type WHERE code = 'camt.054'), 'PROCESSED', 'Processed', 'Обработан', '#8B0000', false, false, false),
-- camt.056 states
('895acd9f-b1d8-4844-ade2-713c9b92ebfd', (SELECT id FROM process_type WHERE code = 'camt.056'), 'LOADED', 'Loaded', 'Загружен', '#FF8C00', true, true, true),
('815c1662-3351-488a-8f40-ddee60b0a3a3', (SELECT id FROM process_type WHERE code = 'camt.056'), 'PROCESSED', 'Processed', 'Обработан', '#8B0000', false, false, false),
-- TRN states
('09835826-3239-4cde-8fdd-112f8e39c494', (SELECT id FROM process_type WHERE code = 'TRN'), 'LOADED', 'Loaded', 'Загружена', '#FF8C00', NULL, NULL, false),
('27b572c3-8bdf-42b7-bd43-999c3df7ba7d', (SELECT id FROM process_type WHERE code = 'TRN'), 'PROCESSED', 'Processed', 'Обработана', '#dbbbb8', NULL, NULL, false)
ON CONFLICT (id) DO NOTHING;

-- Process Operations (using UUIDs from backup)
INSERT INTO public.process_operation (id, type_id, code, name_en, name_ru, icon, resource_url, availability_condition, cancel, move_to_state_script, workflow, database) VALUES
('e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'to_state="PROCESSED"', NULL, NULL),
('04497cef-080c-41e4-8636-8b571bf9afb3', (SELECT id FROM process_type WHERE code = 'pacs.009'), 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'to_state="PROCESSED"', NULL, NULL),
('3630a61c-2c21-44f1-9ea7-f7075327b14b', (SELECT id FROM process_type WHERE code = 'camt.053'), 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'to_state="PROCESSED"', NULL, NULL),
('16d9608e-db6e-499e-ba57-2a3bffbf6481', (SELECT id FROM process_type WHERE code = 'camt.054'), 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'to_state="PROCESSED"', NULL, NULL),
('ecaca1ee-dc5b-4c1e-87f9-79b488e09525', (SELECT id FROM process_type WHERE code = 'camt.056'), 'MARK_AS_PROCESSED', 'Mark as Processed', 'Отметить как обработанный', 'check', NULL, '{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}', false, 'to_state="PROCESSED"', NULL, NULL),
('50e4a5c8-f510-4e45-bac3-f037c81545a6', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'to_state="LOADED"', NULL, NULL),
('2405f16a-fcdb-4ef7-968e-7a41d5284e3e', (SELECT id FROM process_type WHERE code = 'pacs.009'), 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'to_state="LOADED"', NULL, NULL),
('f159119f-7ea1-46e9-8339-ba6714f89174', (SELECT id FROM process_type WHERE code = 'camt.053'), 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'to_state="LOADED"', NULL, NULL),
('eae080aa-61a6-4bd8-8056-1e53019188b5', (SELECT id FROM process_type WHERE code = 'camt.054'), 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'to_state="LOADED"', NULL, NULL),
('ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4', (SELECT id FROM process_type WHERE code = 'camt.056'), 'CANCEL_PROCESSING', 'Cancel Processing', 'Отменить обработку', 'undo', NULL, '{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}', true, 'to_state="LOADED"', NULL, NULL),
('cd28fb8c-d732-4195-8c62-93001648552e', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'CANCEL_PAYMENT', 'Cancel Payment Creation', 'Отменить создание платежа', 'cancel', NULL, '{"target_state": "LOADED", "available_in_states": ["PAYMENT_CREATED"]}', true, 'to_state="LOADED"', NULL, NULL),
('2808dd8d-23c6-466d-b50a-d999268255ab', (SELECT id FROM process_type WHERE code = 'pacs.008'), 'CREATE_PAYMENT', 'Create Payment', 'Создать платеж', 'payment', 'declare  p_dep_id int := 100;  p_id varchar2(250) := :id;  p_test_xml varchar2(4000):= :xml;begin  :out_payment_pk := p_dep_id||'',''||p_id;end;', '{"target_state": "PAYMENT_CREATED", "available_in_states": ["LOADED"]}', false, 'to_state="PAYMENT_CREATED"', 'type_008_payment', 'colvir_cbs'),
('4742683f-144d-4e7d-9596-0e0f9debf090', (SELECT id FROM process_type WHERE code = 'TRN'), 'PROCESS', 'Process', 'Обработать транзакцию', NULL, '1', NULL, false, 'to_state = "PROCESSED"', '1', '1'),
('b07e6901-aacf-49bb-85c0-34c0fee379f3', (SELECT id FROM process_type WHERE code = 'TRN'), 'UNDO_PROCESS', 'Undo Process', 'Отмена обработки транзакции', NULL, NULL, NULL, false, 'to_state = "LOADED"', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- Process Operation States (many-to-many relationships)
INSERT INTO public.process_operation_states (operation_id, state_id) VALUES
('e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11', 'f8c40da3-cf4e-42ec-a641-53eeb7208448'),
('04497cef-080c-41e4-8636-8b571bf9afb3', 'b164a0c1-9544-47c4-84a5-d858d29714df'),
('3630a61c-2c21-44f1-9ea7-f7075327b14b', '3d62da83-1ec1-4ce8-8213-f3869eb7fcdd'),
('16d9608e-db6e-499e-ba57-2a3bffbf6481', '0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9'),
('ecaca1ee-dc5b-4c1e-87f9-79b488e09525', '895acd9f-b1d8-4844-ade2-713c9b92ebfd'),
('2405f16a-fcdb-4ef7-968e-7a41d5284e3e', '7527efd9-007e-4710-afc7-7fc9426c726a'),
('f159119f-7ea1-46e9-8339-ba6714f89174', 'cf11183a-fe76-43e8-8f8f-aa998e83f26a'),
('eae080aa-61a6-4bd8-8056-1e53019188b5', '00c57ee4-58ea-47b3-9804-497773cdd339'),
('ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4', '815c1662-3351-488a-8f40-ddee60b0a3a3'),
('cd28fb8c-d732-4195-8c62-93001648552e', '088d04ed-28d0-4447-b7f6-defb08cbce1a'),
('2808dd8d-23c6-466d-b50a-d999268255ab', 'f8c40da3-cf4e-42ec-a641-53eeb7208448')
ON CONFLICT (operation_id, state_id) DO NOTHING;

-- Swift Settings (default configuration)
INSERT INTO public.swift_settings (folder_in, folder_out, folder_unprocessed, server) VALUES
('/swift/in', '/swift/out', '/swift/unprocessed', 'localhost')
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- Permissions
-- ============================================================================
ALTER TABLE IF EXISTS public.process_type OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_state OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation OWNER TO postgres;
ALTER TABLE IF EXISTS public.process_operation_states OWNER TO postgres;
ALTER TABLE IF EXISTS public.process OWNER TO postgres;
ALTER TABLE IF EXISTS public.swift_settings OWNER TO postgres;

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
GRANT ALL ON TABLE public.swift_settings TO apng;
GRANT ALL ON TABLE public.swift_settings TO postgres;

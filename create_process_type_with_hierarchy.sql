-- ============================================================================
-- Process Type Table with Hierarchy Support
-- ============================================================================

-- Drop existing constraints and table
DROP TABLE IF EXISTS public.process_operation CASCADE;
DROP TABLE IF EXISTS public.process_state CASCADE;
DROP TABLE IF EXISTS public.process_type CASCADE;

-- Create process_type table with id and parent_id
CREATE TABLE public.process_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    resource_url text,
    attributes_table text,
    parent_id uuid,
    CONSTRAINT process_type_pkey PRIMARY KEY (id),
    CONSTRAINT process_type_code_key UNIQUE (code),
    CONSTRAINT process_type_parent_id_fkey 
        FOREIGN KEY (parent_id) 
        REFERENCES public.process_type(id)
        ON DELETE SET NULL
);

-- Add comments
COMMENT ON TABLE public.process_type IS 'Process types for different SWIFT message types with hierarchy support';
COMMENT ON COLUMN public.process_type.id IS 'Unique identifier for process type';
COMMENT ON COLUMN public.process_type.code IS 'Process type code (e.g., pacs.008, camt.053)';
COMMENT ON COLUMN public.process_type.attributes_table IS 'Table name where document attributes for this type are stored';
COMMENT ON COLUMN public.process_type.parent_id IS 'Reference to parent process type for hierarchy';

-- Create indexes
CREATE INDEX idx_process_type_code ON public.process_type(code);
CREATE INDEX idx_process_type_parent_id ON public.process_type(parent_id);

-- Insert process types (all at first level - parent_id is NULL)
INSERT INTO public.process_type (code, name_en, name_ru, name_combined, resource_url, attributes_table, parent_id) VALUES
('pacs.008', 'Customer Credit Transfer', 'Клиентский кредитовый перевод', 'Customer Credit Transfer (Клиентский кредитовый перевод)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}', 'swift_input', NULL),
('pacs.009', 'Financial Institution Credit Transfer (COV)', 'Межбанковский кредитовый перевод (покрытие)', 'Financial Institution Credit Transfer (COV) (Межбанковский кредитовый перевод (покрытие))', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}', 'swift_input', NULL),
('camt.053', 'Bank to Customer Statement', 'Банковская выписка клиенту', 'Bank to Customer Statement (Банковская выписка клиенту)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}', 'swift_input', NULL),
('camt.054', 'Bank to Customer Debit/Credit Notification', 'Уведомление о дебете/кредите', 'Bank to Customer Debit/Credit Notification (Уведомление о дебете/кредите)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}', 'swift_input', NULL),
('camt.056', 'FI to FI Payment Cancellation Request', 'Запрос на отмену платежа', 'FI to FI Payment Cancellation Request (Запрос на отмену платежа)', '/aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}', 'swift_input', NULL),
('TRN', 'Transaction', 'Транзакция (строка выписки)', 'Транзакция (строка выписки)', ' ', 'swift_stmt_ntry', NULL);

-- Grant permissions
ALTER TABLE IF EXISTS public.process_type OWNER TO postgres;
GRANT ALL ON TABLE public.process_type TO apng;
GRANT ALL ON TABLE public.process_type TO postgres;

-- Show the result
SELECT id, code, name_combined, parent_id FROM public.process_type ORDER BY code;

-- Initialize database schema and data for Render PostgreSQL

CREATE TABLE IF NOT EXISTS public.process_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    attributes_table text,
    parent_id uuid
);

CREATE TABLE IF NOT EXISTS public.process_state (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_id uuid NOT NULL,
    code text NOT NULL,
    name_en text NOT NULL,
    name_ru text NOT NULL,
    color_code text,
    allow_edit boolean DEFAULT false,
    allow_delete boolean DEFAULT false,
    start boolean DEFAULT false,
    operation_list_script text
);

CREATE TABLE IF NOT EXISTS public.process_operation (
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
    database text
);

CREATE TABLE IF NOT EXISTS public.process_operation_states (
    operation_id uuid NOT NULL,
    state_id uuid NOT NULL
);

-- Primary keys
ALTER TABLE ONLY public.process_operation DROP CONSTRAINT IF EXISTS process_operation_pkey CASCADE;
ALTER TABLE ONLY public.process_operation_states DROP CONSTRAINT IF EXISTS process_operation_states_pkey CASCADE;
ALTER TABLE ONLY public.process_state DROP CONSTRAINT IF EXISTS process_state_pkey CASCADE;
ALTER TABLE ONLY public.process_type DROP CONSTRAINT IF EXISTS process_type_pkey CASCADE;

ALTER TABLE ONLY public.process_operation ADD CONSTRAINT process_operation_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.process_operation_states ADD CONSTRAINT process_operation_states_pkey PRIMARY KEY (operation_id, state_id);
ALTER TABLE ONLY public.process_state ADD CONSTRAINT process_state_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.process_type ADD CONSTRAINT process_type_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.process_type ADD CONSTRAINT process_type_code_key UNIQUE (code);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_process_type_code ON public.process_type USING btree (code);
CREATE INDEX IF NOT EXISTS idx_process_type_parent_id ON public.process_type USING btree (parent_id);

-- Foreign keys
ALTER TABLE ONLY public.process_operation DROP CONSTRAINT IF EXISTS process_operation_type_id_fkey;
ALTER TABLE ONLY public.process_state DROP CONSTRAINT IF EXISTS process_state_type_id_fkey;
ALTER TABLE ONLY public.process_type DROP CONSTRAINT IF EXISTS process_type_parent_id_fkey;
ALTER TABLE ONLY public.process_operation_states DROP CONSTRAINT IF EXISTS process_operation_states_operation_fkey;
ALTER TABLE ONLY public.process_operation_states DROP CONSTRAINT IF EXISTS process_operation_states_state_fkey;

ALTER TABLE ONLY public.process_operation ADD CONSTRAINT process_operation_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.process_type(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.process_state ADD CONSTRAINT process_state_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.process_type(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.process_type ADD CONSTRAINT process_type_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.process_type(id) ON DELETE SET NULL;
ALTER TABLE ONLY public.process_operation_states ADD CONSTRAINT process_operation_states_operation_fkey FOREIGN KEY (operation_id) REFERENCES public.process_operation(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.process_operation_states ADD CONSTRAINT process_operation_states_state_fkey FOREIGN KEY (state_id) REFERENCES public.process_state(id) ON DELETE CASCADE;

-- Load data
COPY public.process_type (id, code, name_en, name_ru, attributes_table, parent_id) FROM stdin;
9cf44281-08a4-4ed8-bcff-58d4fddb672b	SWIFT	Income SWIFT Payment  	Входящие платежи SWIFT	1	\N
f1f61303-0d4e-4bbf-834d-aeec6e5d948b	pacs.008	Customer Credit Transfer	Клиентский кредитовый перевод	swift_input	9cf44281-08a4-4ed8-bcff-58d4fddb672b
ae2937b0-dd0b-4c02-996b-a40dfb5c570d	pacs.009	Financial Institution Credit Transfer (COV)	Межбанковский кредитовый перевод (покрытие)	swift_input	9cf44281-08a4-4ed8-bcff-58d4fddb672b
8d9c8ddf-cc5b-4631-8482-a9042f197a0e	camt.054	Bank to Customer Debit/Credit Notification	Уведомление о дебете/кредите	swift_input	9cf44281-08a4-4ed8-bcff-58d4fddb672b
f8a3c7f3-ee8a-4fde-911f-990d62c22f2c	camt.056	FI to FI Payment Cancellation Request	Запрос на отмену платежа	swift_input	9cf44281-08a4-4ed8-bcff-58d4fddb672b
3b7b37f1-7fcc-4a36-b636-32df05ed39b6	TRN	Transaction	Транзакция (строка выписки)	swift_stmt_ntry	9cf44281-08a4-4ed8-bcff-58d4fddb672b
4cd791ff-677f-499f-b17e-cfb69d1cdb7c	camt.053	Bank to Customer Statement	Банковская выписка клиенту	swift_input	9cf44281-08a4-4ed8-bcff-58d4fddb672b
\.

COPY public.process_state (id, type_id, code, name_en, name_ru, color_code, allow_edit, allow_delete, start, operation_list_script) FROM stdin;
3d62da83-1ec1-4ce8-8213-f3869eb7fcdd	4cd791ff-677f-499f-b17e-cfb69d1cdb7c	LOADED	Loaded	Загружен	#FFFFFF	t	t	t	oper_list = ["MARK_AS_PROCESSED"]
0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9	8d9c8ddf-cc5b-4631-8482-a9042f197a0e	LOADED	Loaded	Загружен	#FFFFFF	t	t	t	oper_list = ["MARK_AS_PROCESSED"]
895acd9f-b1d8-4844-ade2-713c9b92ebfd	f8a3c7f3-ee8a-4fde-911f-990d62c22f2c	LOADED	Loaded	Загружен	#FFFFFF	t	t	t	oper_list = ["MARK_AS_PROCESSED"]
f8c40da3-cf4e-42ec-a641-53eeb7208448	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	LOADED	Loaded	Загружен	#FFFFFF	t	t	t	oper_list = ["MARK_AS_PROCESSED","CREATE_PAYMENT"]
b164a0c1-9544-47c4-84a5-d858d29714df	ae2937b0-dd0b-4c02-996b-a40dfb5c570d	LOADED	Loaded	Загружен	#FFFFFF	t	t	t	oper_list = ["MARK_AS_PROCESSED"]
09835826-3239-4cde-8fdd-112f8e39c494	3b7b37f1-7fcc-4a36-b636-32df05ed39b6	LOADED	Loaded	Загружена	#FFFFFF	\N	\N	f	oper_list = ["MARK_AS_PROCESSED"]
27b572c3-8bdf-42b7-bd43-999c3df7ba7d	3b7b37f1-7fcc-4a36-b636-32df05ed39b6	PROCESSED	Processed	Обработана	#66CDAA	\N	\N	f	oper_list = ["CANCEL_PROCESSING"]
7527efd9-007e-4710-afc7-7fc9426c726a	ae2937b0-dd0b-4c02-996b-a40dfb5c570d	PROCESSED	Processed	Обработан	#66CDAA	f	f	f	oper_list = ["CANCEL_PROCESSING"]
9f676606-51f2-4bbb-b220-88ae23f166c2	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	PROCESSED	Processed	Обработан	#66CDAA	f	f	f	oper_list = ["CANCEL_PROCESSING"]
815c1662-3351-488a-8f40-ddee60b0a3a3	f8a3c7f3-ee8a-4fde-911f-990d62c22f2c	PROCESSED	Processed	Обработан	#66CDAA	f	f	f	oper_list = ["CANCEL_PROCESSING"]
cf11183a-fe76-43e8-8f8f-aa998e83f26a	4cd791ff-677f-499f-b17e-cfb69d1cdb7c	PROCESSED	Processed	Обработан	#66CDAA	f	f	f	oper_list = ["CANCEL_PROCESSING"]
088d04ed-28d0-4447-b7f6-defb08cbce1a	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	PAYMENT_CREATED	Payment Created	Платеж создан	#FFFFE0	f	f	f	oper_list = ["CANCEL_PAYMENT"]
00c57ee4-58ea-47b3-9804-497773cdd339	8d9c8ddf-cc5b-4631-8482-a9042f197a0e	PROCESSED	Processed	Обработан	#bcd2f5	f	f	f	oper_list = ["CANCEL_PROCESSING"]
\.

COPY public.process_operation (id, type_id, code, name_en, name_ru, icon, resource_url, availability_condition, cancel, move_to_state_script, workflow, database) FROM stdin;
e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	MARK_AS_PROCESSED	Mark as Processed	Отметить как обработанный	check	\N	{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}	f	to_state="PROCESSED"	\N	\N
04497cef-080c-41e4-8636-8b571bf9afb3	ae2937b0-dd0b-4c02-996b-a40dfb5c570d	MARK_AS_PROCESSED	Mark as Processed	Отметить как обработанный	check	\N	{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}	f	to_state="PROCESSED"	\N	\N
16d9608e-db6e-499e-ba57-2a3bffbf6481	8d9c8ddf-cc5b-4631-8482-a9042f197a0e	MARK_AS_PROCESSED	Mark as Processed	Отметить как обработанный	check	\N	{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}	f	to_state="PROCESSED"	\N	\N
ecaca1ee-dc5b-4c1e-87f9-79b488e09525	f8a3c7f3-ee8a-4fde-911f-990d62c22f2c	MARK_AS_PROCESSED	Mark as Processed	Отметить как обработанный	check	\N	{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}	f	to_state="PROCESSED"	\N	\N
50e4a5c8-f510-4e45-bac3-f037c81545a6	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	CANCEL_PROCESSING	Cancel Processing	Отменить обработку	undo	\N	{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}	t	to_state="LOADED"	\N	\N
2405f16a-fcdb-4ef7-968e-7a41d5284e3e	ae2937b0-dd0b-4c02-996b-a40dfb5c570d	CANCEL_PROCESSING	Cancel Processing	Отменить обработку	undo	\N	{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}	t	to_state="LOADED"	\N	\N
eae080aa-61a6-4bd8-8056-1e53019188b5	8d9c8ddf-cc5b-4631-8482-a9042f197a0e	CANCEL_PROCESSING	Cancel Processing	Отменить обработку	undo	\N	{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}	t	to_state="LOADED"	\N	\N
ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4	f8a3c7f3-ee8a-4fde-911f-990d62c22f2c	CANCEL_PROCESSING	Cancel Processing	Отменить обработку	undo	\N	{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}	t	to_state="LOADED"	\N	\N
cd28fb8c-d732-4195-8c62-93001648552e	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	CANCEL_PAYMENT	Cancel Payment Creation	Отменить создание платежа	cancel	\N	{"target_state": "LOADED", "available_in_states": ["PAYMENT_CREATED"]}	t	to_state="LOADED"	\N	\N
2808dd8d-23c6-466d-b50a-d999268255ab	f1f61303-0d4e-4bbf-834d-aeec6e5d948b	CREATE_PAYMENT	Create Payment	Создать платеж	payment	declare  p_dep_id int := 100;  p_id varchar2(250) := :id;  p_test_xml varchar2(4000):= :xml;begin  :out_payment_pk := p_dep_id||','||p_id;end;	{"target_state": "PAYMENT_CREATED", "available_in_states": ["LOADED"]}	f	to_state="PAYMENT_CREATED"	type_008_payment	colvir_cbs
4742683f-144d-4e7d-9596-0e0f9debf090	3b7b37f1-7fcc-4a36-b636-32df05ed39b6	PROCESS	Process	Обработать транзакцию	\N	1	\N	f	to_state = "PROCESSED"	1	1
b07e6901-aacf-49bb-85c0-34c0fee379f3	3b7b37f1-7fcc-4a36-b636-32df05ed39b6	UNDO_PROCESS	Undo Process	Отмена обработки транзакции	\N	\N	\N	f	to_state = "LOADED"	\N	\N
3630a61c-2c21-44f1-9ea7-f7075327b14b	4cd791ff-677f-499f-b17e-cfb69d1cdb7c	MARK_AS_PROCESSED	Mark as Processed	Отметить как обработанный	check	\N	{"target_state": "PROCESSED", "available_in_states": ["LOADED"]}	f	to_state="PROCESSED"	\N	\N
f159119f-7ea1-46e9-8339-ba6714f89174	4cd791ff-677f-499f-b17e-cfb69d1cdb7c	CANCEL_PROCESSING	Cancel Processing	Отменить обработку	undo		{"target_state": "LOADED", "available_in_states": ["PROCESSED"]}	t	to_state="LOADED"	\N	\N
\.

COPY public.process_operation_states (operation_id, state_id) FROM stdin;
e235c9a9-a22d-4ddb-ac59-3a54f9ad8d11	f8c40da3-cf4e-42ec-a641-53eeb7208448
04497cef-080c-41e4-8636-8b571bf9afb3	b164a0c1-9544-47c4-84a5-d858d29714df
3630a61c-2c21-44f1-9ea7-f7075327b14b	3d62da83-1ec1-4ce8-8213-f3869eb7fcdd
16d9608e-db6e-499e-ba57-2a3bffbf6481	0b0f00d2-9e1b-4ba7-ab3f-35655dac94a9
ecaca1ee-dc5b-4c1e-87f9-79b488e09525	895acd9f-b1d8-4844-ade2-713c9b92ebfd
2405f16a-fcdb-4ef7-968e-7a41d5284e3e	7527efd9-007e-4710-afc7-7fc9426c726a
f159119f-7ea1-46e9-8339-ba6714f89174	cf11183a-fe76-43e8-8f8f-aa998e83f26a
eae080aa-61a6-4bd8-8056-1e53019188b5	00c57ee4-58ea-47b3-9804-497773cdd339
ae4c638d-f954-4f3e-ac7a-c2ca7cd9ccb4	815c1662-3351-488a-8f40-ddee60b0a3a3
cd28fb8c-d732-4195-8c62-93001648552e	088d04ed-28d0-4447-b7f6-defb08cbce1a
2808dd8d-23c6-466d-b50a-d999268255ab	f8c40da3-cf4e-42ec-a641-53eeb7208448
50e4a5c8-f510-4e45-bac3-f037c81545a6	9f676606-51f2-4bbb-b220-88ae23f166c2
\.


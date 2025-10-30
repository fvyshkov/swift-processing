UPDATE process_state
SET operation_list_script = 'oper_list = ["CREATE_PAYMENT"]'
WHERE code = 'LOADED' 
  AND type_id = (SELECT id FROM process_type WHERE code = 'pacs.008');

UPDATE process_state
SET operation_list_script = 'oper_list = ["MARK_AS_PROCESSED"]'
WHERE code = 'LOADED';

UPDATE process_state
SET operation_list_script = 'oper_list = ["CANCEL_PROCESSING"]'
WHERE code = 'PROCESSED';

UPDATE process_state
SET operation_list_script = 'oper_list = ["CANCEL_PAYMENT"]'
WHERE code = 'PAYMENT_CREATED'
  AND type_id = (SELECT id FROM process_type WHERE code = 'pacs.008');


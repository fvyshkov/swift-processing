#!/usr/bin/env python3
"""
Get available operations for a process by its ID
"""

import os
import sys
import traceback

from apng_core.db import initDbSession, fetchall, fetchone
from apng_core.exceptions import UserException


def get_available_operations(doc_id: str):
    """
    Get list of available operations for a document
    
    Args:
        doc_id: UUID of the swift_input record
    
    Returns:
        List of dictionaries with operation details
    """
    
    # Step 1: Get current state and operation_list_script
    SQL_STATE = """
        SELECT 
            ps.id as state_id,
            ps.operation_list_script,
            si.*
        FROM swift_input si
        JOIN process p ON p.doc_id = si.id
        JOIN process_state ps ON ps.id = p.state_id
        WHERE si.id = %(doc_id)s
    """
    
    with initDbSession(database='default').cursor() as c:
        c.execute(SQL_STATE, {'doc_id': doc_id})
        result = fetchone(c)
        
        if not result:
            raise UserException({
                'message': 'Document not found or has no process',
                'description': f'Document ID: {doc_id}'
            })
        
        operation_list_script = result.get('operation_list_script')
        
        # If no script defined, return all operations for current state
        if not operation_list_script:
            # Fallback to old behavior - get all operations for current state
            SQL_OPS = """
                SELECT 
                    po.id,
                    po.code,
                    po.name_en,
                    po.name_ru,
                    po.icon,
                    po.resource_url,
                    po.cancel,
                    po.database,
                    po.move_to_state_script,
                    po.workflow
                FROM process_operation po
                JOIN process_operation_states pos ON pos.operation_id = po.id
                WHERE pos.state_id = %(state_id)s
                ORDER BY po.cancel, po.code
            """
            c.execute(SQL_OPS, {'state_id': result['state_id']})
            return fetchall(c)
        
        # Step 2: Execute operation_list_script
        # Prepare record with all swift_input fields
        record = dict(result)
        # Remove operation_list_script and state_id from record
        record.pop('operation_list_script', None)
        record.pop('state_id', None)
        
        # Create script context
        script_context = {
            'record': record,
            'oper_list': []  # Script should populate this
        }
        
        try:
            exec(operation_list_script, script_context)
            oper_list = script_context.get('oper_list', [])
            
            if not oper_list:
                return []
            
            # Step 3: Get operation details for codes returned by script
            # Get msg_type from swift_input to find correct type_id
            msg_type = result.get('msg_type')
            
            # Build IN clause for operation codes
            placeholders = ', '.join(['%s'] * len(oper_list))
            
            SQL_OPS_BY_CODE = f"""
                SELECT 
                    po.id,
                    po.code,
                    po.name_en,
                    po.name_ru,
                    po.icon,
                    po.resource_url,
                    po.cancel,
                    po.database,
                    po.move_to_state_script,
                    po.workflow
                FROM process_operation po
                JOIN process_type pt ON po.type_id = pt.id
                WHERE pt.code = %s
                  AND po.code IN ({placeholders})
                ORDER BY po.cancel, po.code
            """
            
            # Execute with msg_type and operation codes
            params = [msg_type] + oper_list
            c.execute(SQL_OPS_BY_CODE, params)
            return fetchall(c)
            
        except Exception as e:
            raise UserException({
                'message': 'Error executing operation_list_script',
                'description': str(e),
                'traceback': traceback.format_exc()
            })


# Get parameters
doc_id = parameters.get('id')
if not doc_id:
    raise UserException({
        'message': 'Document ID is required',
        'description': 'Parameter "id" is missing'
    })

data = get_available_operations(doc_id)
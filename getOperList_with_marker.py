#!/usr/bin/env python3
"""
Get available operations for a process by its ID
"""

import os
import sys

from apng_core.db import initDbSession, fetchall


def get_available_operations(process_id: str):
    """
    Get list of available operations for a process
    
    Args:
        process_id: UUID of the swift_input record
    
    Returns:
        List of dictionaries with operation details
    """
    SQL = """
         SELECT 
            po.id,
            po.code,
            po.name_en,
            po.name_ru,
            po.name_combined,
            po.icon,
            po.resource_url,
            po.cancel,
            po.to_state,
            po.database,
            si.state as current_state,
            si.msg_type
        FROM    swift_input si, process pp,
                process_operation po ,
                process_operation_states pos,
		process_state prc_st
		where pos.operation_id = po.id
		 and pos.state_id = pp.state_id
         AND prc_st.id = pp.state_id
		and pp.doc_id = si.id
        and si.id = %(process_id)s
        ORDER BY po.cancel, po.code
    """
    
    with initDbSession(database='default').cursor() as c:
        c.execute(SQL, {'process_id': process_id})
        results = fetchall(c)
        return results
        operations = []
        for row in results:
            # Replace placeholders in resource URL
            resource_url = row[6]
            if resource_url:
                resource_url = resource_url.replace('{id}', str(process_id))
                resource_url = resource_url.replace('{type}', row[11])
            
            operation = {
                'id': row[0],
                'code': row[1],
                'name_en': row[2],
                'name_ru': row[3],
                'name_combined': row[4],
                'icon': row[5],
                'resource_url': resource_url,
                'cancel': row[7],
                'to_state': row[8],
                'database': row[9] or 'default',
                'current_state': row[10],
                'process_type': row[11]
            }
            operations.append(operation)
        
        return operations


def get_process_state(process_id: str):
    """
    Get process current state
    
    Args:
        process_id: UUID of the process
    
    Returns:
        Dictionary with process state info or None
    """
    SQL = """
        SELECT 
            id,
            msg_type,
            state,
            file_name,
            amount,
            currency_code
        FROM swift_input
        WHERE id = %(process_id)s
    """
    
    with initDbSession(database='default').cursor() as c:
        c.execute(SQL, {'process_id': process_id})
        result = c.fetchone()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'msg_type': result[1],
            'state': result[2],
            'file_name': result[3],
            'amount': result[4],
            'currency_code': result[5]
        }


    
process_id = parameters.get('id')
#raise Exception(process_id)
# Get process info
#process = get_process_state(process_id)
#if not process:
#    print(f"Process not found: {process_id}")
#    sys.exit(1)

# Get operations
data = get_available_operations(process_id)
#raise Exception(parameters)
# Print results
#print(f"\nProcess: {process['file_name']}")
#print(f"Type: {process['msg_type']}")
#print(f"State: {process['state']}")
#print(f"\nAvailable operations ({len(operations)}):")

#for op in operations:
#    cancel_mark = "↶" if op['cancel'] else "→"
#    print(f"  {cancel_mark} [{op['icon']}] {op['name_ru']} (to: {op['to_state'] or 'no change'})")




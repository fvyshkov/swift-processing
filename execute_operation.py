#!/usr/bin/env python3
"""
Execute process operation on a document
- Changes document state
- Executes operation resource URL on specified database
"""

import os
import sys
import json
from typing import Dict, Optional, Any
from datetime import datetime

# Add parent directory to path to import apng_core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from apng_core.db import initDbSession, fetchone
    from apng_core.logger import Logger
except ImportError:
    print("ERROR: Cannot import apng_core modules")
    print("Make sure you're running this in the correct environment")
    sys.exit(1)

# Initialize logger
logger = Logger(__file__)


def get_operation_info(cursor, operation_id: str) -> Optional[Dict]:
    """
    Get operation information by ID
    
    Args:
        cursor: Database cursor
        operation_id: UUID of the operation
    
    Returns:
        Dictionary with operation info or None if not found
    """
    SQL = """
        SELECT 
            id,
            type_code,
            code,
            name_en,
            name_ru,
            name_combined,
            icon,
            resource_url,
            availability_condition,
            cancel,
            to_state,
            database
        FROM process_operation
        WHERE id = %(operation_id)s
    """
    
    try:
        cursor.execute(SQL, {'operation_id': operation_id})
        result = cursor.fetchone()
        
        if not result:
            return None
        
        # Parse availability_condition if exists
        availability_condition = {}
        if result[8]:
            try:
                availability_condition = json.loads(result[8])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in availability_condition: {result[8]}")
        
        return {
            'id': result[0],
            'type_code': result[1],
            'code': result[2],
            'name_en': result[3],
            'name_ru': result[4],
            'name_combined': result[5],
            'icon': result[6],
            'resource_url': result[7],
            'availability_condition': availability_condition,
            'cancel': result[9] if result[9] is not None else False,
            'to_state': result[10],
            'database': result[11]
        }
    except Exception as e:
        logger.error(f"Error getting operation info: {e}")
        raise


def get_document_state(cursor, document_id: str) -> Optional[Dict]:
    """
    Get document current state
    
    Args:
        cursor: Database cursor
        document_id: UUID of the document
    
    Returns:
        Dictionary with document state info or None if not found
    """
    SQL = """
        SELECT 
            id,
            msg_type,
            state,
            file_name
        FROM swift_input
        WHERE id = %(document_id)s
    """
    
    try:
        cursor.execute(SQL, {'document_id': document_id})
        result = cursor.fetchone()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'msg_type': result[1],
            'state': result[2],
            'file_name': result[3]
        }
    except Exception as e:
        logger.error(f"Error getting document state: {e}")
        raise


def update_document_state(cursor, document_id: str, new_state: str) -> bool:
    """
    Update document state
    
    Args:
        cursor: Database cursor
        document_id: UUID of the document
        new_state: New state code
    
    Returns:
        True if successful, False otherwise
    """
    SQL = """
        UPDATE swift_input
        SET state = %(new_state)s
        WHERE id = %(document_id)s
    """
    
    try:
        cursor.execute(SQL, {
            'document_id': document_id,
            'new_state': new_state
        })
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error updating document state: {e}")
        raise


def execute_operation_url(operation: Dict, document_id: str, parameters: Dict = None) -> Dict:
    """
    Execute operation resource URL
    
    Args:
        operation: Operation dictionary with resource_url and database
        document_id: UUID of the document
        parameters: Additional parameters for execution
    
    Returns:
        Dictionary with execution result
    """
    resource_url = operation.get('resource_url')
    database_name = operation.get('database') or 'default'
    
    if not resource_url:
        return {
            'success': False,
            'error': 'No resource_url defined for operation'
        }
    
    # Parse resource URL to extract action
    # Format: /aoa/ProcessAction?action=actionName&docId={id}&docType={type}
    try:
        if '?' in resource_url:
            path, query = resource_url.split('?', 1)
            params = {}
            for param in query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    # Replace placeholders
                    value = value.replace('{id}', str(document_id))
                    if parameters and '{type}' in value:
                        value = value.replace('{type}', str(parameters.get('type', '')))
                    params[key] = value
            
            action = params.get('action')
            
            if not action:
                return {
                    'success': False,
                    'error': 'No action specified in resource_url'
                }
            
            logger.info(f"Executing action: {action}")
            logger.info(f"Database: {database_name}")
            logger.info(f"Parameters: {params}")
            
            # Here you would implement actual action execution
            # This is a placeholder for the actual implementation
            result = {
                'success': True,
                'action': action,
                'database': database_name,
                'parameters': params,
                'message': f'Action {action} would be executed on database {database_name}'
            }
            
            return result
            
        else:
            return {
                'success': False,
                'error': 'Invalid resource_url format'
            }
            
    except Exception as e:
        logger.error(f"Error executing operation URL: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def log_operation_execution(cursor, document_id: str, operation_id: str, 
                           old_state: str, new_state: str, success: bool, 
                           result: Dict) -> bool:
    """
    Log operation execution to history (if table exists)
    
    Args:
        cursor: Database cursor
        document_id: UUID of the document
        operation_id: UUID of the operation
        old_state: State before operation
        new_state: State after operation
        success: Operation success flag
        result: Operation execution result
    
    Returns:
        True if logged successfully
    """
    # This is a placeholder - implement when operation_history table is created
    logger.info(f"Would log operation execution:")
    logger.info(f"  Document: {document_id}")
    logger.info(f"  Operation: {operation_id}")
    logger.info(f"  State: {old_state} → {new_state}")
    logger.info(f"  Success: {success}")
    logger.info(f"  Result: {result}")
    
    return True


def execute_operation(operation_id: str, document_id: str, 
                     parameters: Dict = None, verbose: bool = False) -> Dict:
    """
    Execute operation on a document
    
    Args:
        operation_id: UUID of the operation
        document_id: UUID of the document
        parameters: Additional parameters for execution
        verbose: If True, print detailed information
    
    Returns:
        Dictionary with execution result
    """
    if parameters is None:
        parameters = {}
    
    try:
        with initDbSession(database='default').cursor() as c:
            # Get operation info
            operation = get_operation_info(c, operation_id)
            
            if not operation:
                error_msg = f"Operation not found: {operation_id}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            if verbose:
                logger.info("=" * 70)
                logger.info("Operation Execution")
                logger.info("=" * 70)
                logger.info(f"Operation: {operation['name_combined']}")
                logger.info(f"Code: {operation['code']}")
                logger.info(f"Cancel: {operation['cancel']}")
                logger.info(f"Target State: {operation['to_state']}")
                logger.info(f"Database: {operation['database'] or 'default'}")
            
            # Get current document state
            doc_state = get_document_state(c, document_id)
            
            if not doc_state:
                error_msg = f"Document not found: {document_id}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            old_state = doc_state['state']
            
            if verbose:
                logger.info("")
                logger.info("Document Information")
                logger.info("-" * 70)
                logger.info(f"ID: {document_id}")
                logger.info(f"File: {doc_state['file_name']}")
                logger.info(f"Type: {doc_state['msg_type']}")
                logger.info(f"Current State: {old_state}")
            
            # Add document type to parameters
            parameters['type'] = doc_state['msg_type']
            
            # Execute operation resource URL
            if verbose:
                logger.info("")
                logger.info("Executing Operation URL")
                logger.info("-" * 70)
            
            url_result = execute_operation_url(operation, document_id, parameters)
            
            if not url_result.get('success'):
                logger.error(f"Operation URL execution failed: {url_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Operation execution failed: {url_result.get('error')}",
                    'document_id': document_id,
                    'operation_id': operation_id,
                    'old_state': old_state,
                    'new_state': old_state  # No change
                }
            
            if verbose:
                logger.info(f"✓ {url_result.get('message', 'Executed successfully')}")
            
            # Update document state if to_state is specified
            new_state = old_state  # Default: no change
            
            if operation['to_state']:
                if verbose:
                    logger.info("")
                    logger.info("Updating Document State")
                    logger.info("-" * 70)
                    logger.info(f"From: {old_state}")
                    logger.info(f"To: {operation['to_state']}")
                
                success = update_document_state(c, document_id, operation['to_state'])
                
                if success:
                    new_state = operation['to_state']
                    if verbose:
                        logger.info(f"✓ State updated successfully")
                else:
                    logger.error("Failed to update document state")
                    return {
                        'success': False,
                        'error': 'Failed to update document state',
                        'document_id': document_id,
                        'operation_id': operation_id,
                        'old_state': old_state,
                        'new_state': old_state
                    }
            else:
                if verbose:
                    logger.info("")
                    logger.info("State Update")
                    logger.info("-" * 70)
                    logger.info("No state change (to_state is NULL)")
            
            # Log operation execution
            log_operation_execution(
                c, document_id, operation_id,
                old_state, new_state, True, url_result
            )
            
            # Commit transaction
            c.connection.commit()
            
            if verbose:
                logger.info("")
                logger.info("=" * 70)
                logger.info("Operation Completed Successfully")
                logger.info("=" * 70)
            
            return {
                'success': True,
                'document_id': document_id,
                'operation_id': operation_id,
                'operation_code': operation['code'],
                'operation_name': operation['name_ru'],
                'old_state': old_state,
                'new_state': new_state,
                'state_changed': old_state != new_state,
                'url_result': url_result
            }
            
    except Exception as e:
        error_msg = f"Error executing operation: {e}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': error_msg
        }


def execute_operation_by_code(operation_code: str, document_id: str, 
                              doc_type: str = None, parameters: Dict = None,
                              verbose: bool = False) -> Dict:
    """
    Execute operation by code (convenience method)
    
    Args:
        operation_code: Operation code (e.g., 'MARK_AS_PROCESSED')
        document_id: UUID of the document
        doc_type: Document type code (optional, will be fetched if not provided)
        parameters: Additional parameters for execution
        verbose: If True, print detailed information
    
    Returns:
        Dictionary with execution result
    """
    try:
        with initDbSession(database='default').cursor() as c:
            # Get document type if not provided
            if not doc_type:
                doc_state = get_document_state(c, document_id)
                if not doc_state:
                    return {
                        'success': False,
                        'error': f'Document not found: {document_id}'
                    }
                doc_type = doc_state['msg_type']
            
            # Find operation by code and document type
            SQL = """
                SELECT id
                FROM process_operation
                WHERE code = %(operation_code)s
                  AND type_code = %(doc_type)s
            """
            
            c.execute(SQL, {
                'operation_code': operation_code,
                'doc_type': doc_type
            })
            
            result = c.fetchone()
            
            if not result:
                return {
                    'success': False,
                    'error': f'Operation not found: {operation_code} for type {doc_type}'
                }
            
            operation_id = result[0]
            
            # Execute operation
            return execute_operation(operation_id, document_id, parameters, verbose)
            
    except Exception as e:
        error_msg = f"Error executing operation by code: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }


# Example usage as module
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute process operation on SWIFT document'
    )
    parser.add_argument(
        'document_id',
        help='UUID of the document'
    )
    parser.add_argument(
        'operation',
        help='Operation ID (UUID) or operation code'
    )
    parser.add_argument(
        '-t', '--type',
        help='Document type (required if using operation code)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '-p', '--param',
        action='append',
        help='Additional parameter in format key=value'
    )
    
    args = parser.parse_args()
    
    # Parse additional parameters
    parameters = {}
    if args.param:
        for param in args.param:
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key] = value
    
    # Check if operation is UUID or code
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if uuid_pattern.match(args.operation):
        # Operation is UUID
        result = execute_operation(
            args.operation,
            args.document_id,
            parameters,
            args.verbose
        )
    else:
        # Operation is code
        result = execute_operation_by_code(
            args.operation,
            args.document_id,
            args.type,
            parameters,
            args.verbose
        )
    
    if args.json:
        # Output as JSON
        import json
        print(json.dumps(result, indent=2, default=str))
    elif not args.verbose:
        # Simple output
        if result['success']:
            print(f"\n✓ Operation executed successfully")
            print(f"  Document: {result['document_id']}")
            print(f"  Operation: {result.get('operation_name', result.get('operation_code'))}")
            if result.get('state_changed'):
                print(f"  State: {result['old_state']} → {result['new_state']}")
            else:
                print(f"  State: {result['old_state']} (no change)")
        else:
            print(f"\n✗ Operation failed: {result['error']}")
            sys.exit(1)


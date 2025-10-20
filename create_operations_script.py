#!/usr/bin/env python3
"""
Script for creating process operations for SWIFT documents
Creates operations with state transitions and reverse operations
"""

import os
import sys

# Add parent directory to path to import apng_core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from apng_core.db import initDbSession
    from apng_core.logger import Logger
except ImportError:
    print("ERROR: Cannot import apng_core modules")
    print("Make sure you're running this in the correct environment")
    sys.exit(1)

# Initialize logger
logger = Logger(__file__)

# Define operations configuration
OPERATIONS_CONFIG = [
    {
        'code': 'MARK_AS_PROCESSED',
        'name_en': 'Mark as Processed',
        'name_ru': 'Отметить как обработанный',
        'icon': 'check',
        'resource_url': '/aoa/ProcessAction?action=markProcessed&docId={id}&docType={type}',
        'types': ['pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056'],  # All types
        'available_in_states': ['LOADED'],  # Available when document is LOADED
        'target_state': 'PROCESSED'
    },
    {
        'code': 'CANCEL_PROCESSING',
        'name_en': 'Cancel Processing',
        'name_ru': 'Отменить обработку',
        'icon': 'undo',
        'resource_url': '/aoa/ProcessAction?action=cancelProcessing&docId={id}&docType={type}',
        'types': ['pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056'],  # All types
        'available_in_states': ['PROCESSED'],  # Available when document is PROCESSED
        'target_state': 'LOADED'
    },
    {
        'code': 'CREATE_PAYMENT',
        'name_en': 'Create Payment',
        'name_ru': 'Создать платеж',
        'icon': 'payment',
        'resource_url': '/aoa/ProcessAction?action=createPayment&docId={id}&docType={type}',
        'types': ['pacs.008'],  # Only pacs.008
        'available_in_states': ['LOADED'],  # Available when document is LOADED
        'target_state': 'PAYMENT_CREATED'
    },
    {
        'code': 'CANCEL_PAYMENT',
        'name_en': 'Cancel Payment Creation',
        'name_ru': 'Отменить создание платежа',
        'icon': 'cancel',
        'resource_url': '/aoa/ProcessAction?action=cancelPayment&docId={id}&docType={type}',
        'types': ['pacs.008'],  # Only pacs.008
        'available_in_states': ['PAYMENT_CREATED'],  # Available when payment is created
        'target_state': 'LOADED'
    }
]


def get_state_id(cursor, type_code, state_code):
    """
    Get state ID by type_code and state_code
    
    Args:
        cursor: Database cursor
        type_code: Document type code
        state_code: State code
    
    Returns:
        UUID of the state or None if not found
    """
    SQL = """
        SELECT id 
        FROM process_state 
        WHERE type_code = %(type_code)s AND code = %(state_code)s
    """
    
    try:
        cursor.execute(SQL, {'type_code': type_code, 'state_code': state_code})
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting state ID for {type_code}/{state_code}: {e}")
        return None


def create_operation(cursor, type_code, operation_config):
    """
    Create a single process operation record
    
    Args:
        cursor: Database cursor
        type_code: Document type code
        operation_config: Operation configuration dictionary
    
    Returns:
        UUID of created/updated operation or None on error
    """
    name_combined = f"{operation_config['name_en']} ({operation_config['name_ru']})"
    
    # Build availability condition JSON
    availability_condition = {
        'target_state': operation_config.get('target_state'),
        'available_in_states': operation_config['available_in_states']
    }
    
    import json
    availability_json = json.dumps(availability_condition, ensure_ascii=False)
    
    SQL = """
        INSERT INTO process_operation (
            type_code, code, name_en, name_ru, name_combined,
            icon, resource_url, availability_condition
        )
        VALUES (
            %(type_code)s, %(code)s, %(name_en)s, %(name_ru)s, %(name_combined)s,
            %(icon)s, %(resource_url)s, %(availability_condition)s
        )
        ON CONFLICT (type_code, code) DO UPDATE SET
            name_en = EXCLUDED.name_en,
            name_ru = EXCLUDED.name_ru,
            name_combined = EXCLUDED.name_combined,
            icon = EXCLUDED.icon,
            resource_url = EXCLUDED.resource_url,
            availability_condition = EXCLUDED.availability_condition
        RETURNING id
    """
    
    params = {
        'type_code': type_code,
        'code': operation_config['code'],
        'name_en': operation_config['name_en'],
        'name_ru': operation_config['name_ru'],
        'name_combined': name_combined,
        'icon': operation_config['icon'],
        'resource_url': operation_config['resource_url'],
        'availability_condition': availability_json
    }
    
    try:
        cursor.execute(SQL, params)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error creating operation {operation_config['code']} for type {type_code}: {e}")
        raise


def link_operation_to_states(cursor, operation_id, type_code, state_codes):
    """
    Link operation to states where it's available
    
    Args:
        cursor: Database cursor
        operation_id: Operation UUID
        type_code: Document type code
        state_codes: List of state codes where operation is available
    
    Returns:
        Number of links created
    """
    # First, delete existing links for this operation
    DELETE_SQL = "DELETE FROM process_operation_states WHERE operation_id = %(operation_id)s"
    cursor.execute(DELETE_SQL, {'operation_id': operation_id})
    
    created_count = 0
    
    for state_code in state_codes:
        # Get state ID
        state_id = get_state_id(cursor, type_code, state_code)
        
        if not state_id:
            logger.warning(f"  State {state_code} not found for type {type_code}, skipping link")
            continue
        
        # Create link
        INSERT_SQL = """
            INSERT INTO process_operation_states (operation_id, state_id)
            VALUES (%(operation_id)s, %(state_id)s)
            ON CONFLICT (operation_id, state_id) DO NOTHING
        """
        
        try:
            cursor.execute(INSERT_SQL, {'operation_id': operation_id, 'state_id': state_id})
            created_count += 1
        except Exception as e:
            logger.error(f"  Error linking operation to state {state_code}: {e}")
    
    return created_count


def check_states_exist(cursor):
    """
    Check if process_state table has required states
    
    Args:
        cursor: Database cursor
    
    Returns:
        Dictionary of state counts by type
    """
    SQL = """
        SELECT type_code, COUNT(*) as count
        FROM process_state
        GROUP BY type_code
        ORDER BY type_code
    """
    
    try:
        cursor.execute(SQL)
        states = cursor.fetchall()
        
        if not states:
            logger.warning("No states found in process_state table")
            logger.warning("Please run create_states_script.py first")
            return {}
        
        logger.info("Available states by document type:")
        state_counts = {}
        for row in states:
            type_code, count = row
            state_counts[type_code] = count
            logger.info(f"  - {type_code}: {count} states")
        
        return state_counts
        
    except Exception as e:
        logger.error(f"Error checking states: {e}")
        raise


def create_all_operations():
    """
    Main function to create all process operations
    """
    logger.info("=" * 70)
    logger.info("Starting process operations creation")
    logger.info("=" * 70)
    
    created_count = 0
    linked_count = 0
    error_count = 0
    
    try:
        with initDbSession(database='default').cursor() as c:
            # Check available states
            state_counts = check_states_exist(c)
            
            if not state_counts:
                logger.error("Cannot proceed without states")
                logger.error("Run create_states_script.py first")
                return False
            
            logger.info("")
            logger.info("Creating process operations...")
            logger.info("")
            
            # Iterate through each operation configuration
            for op_config in OPERATIONS_CONFIG:
                op_code = op_config['code']
                op_name = f"{op_config['name_en']} ({op_config['name_ru']})"
                
                logger.info(f"Processing operation: {op_name}")
                logger.info(f"  Code: {op_code}")
                logger.info(f"  Icon: {op_config['icon']}")
                logger.info(f"  Available in states: {', '.join(op_config['available_in_states'])}")
                logger.info(f"  Target state: {op_config.get('target_state', 'N/A')}")
                logger.info(f"  Document types: {', '.join(op_config['types'])}")
                
                # Create operation for each specified document type
                for type_code in op_config['types']:
                    # Check if type has states
                    if type_code not in state_counts:
                        logger.warning(f"    Skipping {type_code} - no states found")
                        continue
                    
                    try:
                        # Create operation
                        operation_id = create_operation(c, type_code, op_config)
                        if operation_id:
                            logger.info(f"    ✓ Created/updated for {type_code}: {operation_id}")
                            created_count += 1
                            
                            # Link to states
                            links = link_operation_to_states(
                                c, operation_id, type_code, 
                                op_config['available_in_states']
                            )
                            linked_count += links
                            logger.info(f"    ✓ Linked to {links} state(s)")
                        else:
                            logger.error(f"    ✗ Failed to create for {type_code}")
                            error_count += 1
                    except Exception as e:
                        logger.error(f"    ✗ Error for {type_code}: {e}")
                        error_count += 1
                
                logger.info("")
            
            # Commit transaction
            c.connection.commit()
            
            logger.info("=" * 70)
            logger.info("Process operations creation completed")
            logger.info(f"  Created/Updated operations: {created_count}")
            logger.info(f"  State links created: {linked_count}")
            logger.info(f"  Errors: {error_count}")
            logger.info("=" * 70)
            
            # Display created operations
            logger.info("")
            logger.info("Current operations in database:")
            logger.info("")
            
            SQL_LIST = """
                SELECT 
                    po.type_code,
                    po.code,
                    po.name_combined,
                    po.icon,
                    STRING_AGG(ps.code, ', ' ORDER BY ps.code) as available_states
                FROM process_operation po
                LEFT JOIN process_operation_states pos ON pos.operation_id = po.id
                LEFT JOIN process_state ps ON ps.id = pos.state_id
                GROUP BY po.type_code, po.code, po.name_combined, po.icon
                ORDER BY po.type_code, po.code
            """
            
            c.execute(SQL_LIST)
            operations = c.fetchall()
            
            current_type = None
            for row in operations:
                type_code, code, name, icon, states = row
                
                if type_code != current_type:
                    logger.info(f"\n{type_code}:")
                    current_type = type_code
                
                logger.info(f"  - {code}: {name}")
                logger.info(f"      Icon: {icon}, Available in: {states or 'N/A'}")
            
            return error_count == 0
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    logger.info("SWIFT Process Operations Creation Script")
    logger.info("")
    
    success = create_all_operations()
    
    if success:
        logger.info("")
        logger.info("SUCCESS: All operations created successfully")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("FAILED: Some errors occurred during creation")
        sys.exit(1)


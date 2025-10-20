#!/usr/bin/env python3
"""
Script for creating process states for SWIFT documents
Creates states with different colors for different document types
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

# Define states configuration
STATES_CONFIG = [
    {
        'code': 'LOADED',
        'name_en': 'Loaded',
        'name_ru': 'Загружен',
        'color_code': '#FF8C00',  # Orange (DarkOrange)
        'allow_edit': True,
        'allow_delete': True,
        'types': ['pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056']  # All types
    },
    {
        'code': 'PROCESSED',
        'name_en': 'Processed',
        'name_ru': 'Обработан',
        'color_code': '#8B0000',  # Burgundy (DarkRed)
        'allow_edit': False,
        'allow_delete': False,
        'types': ['pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056']  # All types
    },
    {
        'code': 'PAYMENT_CREATED',
        'name_en': 'Payment Created',
        'name_ru': 'Платеж создан',
        'color_code': '#008000',  # Green
        'allow_edit': False,
        'allow_delete': False,
        'types': ['pacs.008']  # Only pacs.008
    }
]


def create_state(cursor, type_code, state_config):
    """
    Create a single process state record
    
    Args:
        cursor: Database cursor
        type_code: Document type code
        state_config: State configuration dictionary
    
    Returns:
        UUID of created/updated state or None on error
    """
    name_combined = f"{state_config['name_en']} ({state_config['name_ru']})"
    
    SQL = """
        INSERT INTO process_state (
            type_code, code, name_en, name_ru, name_combined,
            color_code, allow_edit, allow_delete
        )
        VALUES (
            %(type_code)s, %(code)s, %(name_en)s, %(name_ru)s, %(name_combined)s,
            %(color_code)s, %(allow_edit)s, %(allow_delete)s
        )
        ON CONFLICT (type_code, code) DO UPDATE SET
            name_en = EXCLUDED.name_en,
            name_ru = EXCLUDED.name_ru,
            name_combined = EXCLUDED.name_combined,
            color_code = EXCLUDED.color_code,
            allow_edit = EXCLUDED.allow_edit,
            allow_delete = EXCLUDED.allow_delete
        RETURNING id
    """
    
    params = {
        'type_code': type_code,
        'code': state_config['code'],
        'name_en': state_config['name_en'],
        'name_ru': state_config['name_ru'],
        'name_combined': name_combined,
        'color_code': state_config['color_code'],
        'allow_edit': state_config['allow_edit'],
        'allow_delete': state_config['allow_delete']
    }
    
    try:
        cursor.execute(SQL, params)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error creating state {state_config['code']} for type {type_code}: {e}")
        raise


def check_process_types(cursor):
    """
    Check if process_type table has required document types
    
    Args:
        cursor: Database cursor
    
    Returns:
        List of available type codes
    """
    SQL = """
        SELECT code, name_en, name_ru
        FROM process_type
        ORDER BY code
    """
    
    try:
        cursor.execute(SQL)
        types = cursor.fetchall()
        
        if not types:
            logger.warning("No document types found in process_type table")
            logger.warning("Please run db_schema_process.sql first")
            return []
        
        logger.info("Available document types:")
        type_codes = []
        for row in types:
            type_codes.append(row[0])
            logger.info(f"  - {row[0]}: {row[1]} ({row[2]})")
        
        return type_codes
        
    except Exception as e:
        logger.error(f"Error checking process types: {e}")
        raise


def create_all_states():
    """
    Main function to create all process states
    """
    logger.info("=" * 70)
    logger.info("Starting process states creation")
    logger.info("=" * 70)
    
    created_count = 0
    error_count = 0
    
    try:
        with initDbSession(database='default').cursor() as c:
            # Check available document types
            available_types = check_process_types(c)
            
            if not available_types:
                logger.error("Cannot proceed without document types")
                return False
            
            logger.info("")
            logger.info("Creating process states...")
            logger.info("")
            
            # Iterate through each state configuration
            for state_config in STATES_CONFIG:
                state_code = state_config['code']
                state_name = f"{state_config['name_en']} ({state_config['name_ru']})"
                
                logger.info(f"Processing state: {state_name}")
                logger.info(f"  Code: {state_code}")
                logger.info(f"  Color: {state_config['color_code']}")
                logger.info(f"  Allow edit: {state_config['allow_edit']}")
                logger.info(f"  Allow delete: {state_config['allow_delete']}")
                logger.info(f"  Document types: {', '.join(state_config['types'])}")
                
                # Create state for each specified document type
                for type_code in state_config['types']:
                    # Check if type exists
                    if type_code not in available_types:
                        logger.warning(f"    Skipping {type_code} - not in process_type table")
                        continue
                    
                    try:
                        state_id = create_state(c, type_code, state_config)
                        if state_id:
                            logger.info(f"    ✓ Created/updated for {type_code}: {state_id}")
                            created_count += 1
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
            logger.info("Process states creation completed")
            logger.info(f"  Created/Updated: {created_count}")
            logger.info(f"  Errors: {error_count}")
            logger.info("=" * 70)
            
            # Display created states
            logger.info("")
            logger.info("Current states in database:")
            logger.info("")
            
            SQL_LIST = """
                SELECT 
                    ps.type_code,
                    ps.code,
                    ps.name_combined,
                    ps.color_code,
                    ps.allow_edit,
                    ps.allow_delete
                FROM process_state ps
                ORDER BY ps.type_code, ps.code
            """
            
            c.execute(SQL_LIST)
            states = c.fetchall()
            
            current_type = None
            for row in states:
                type_code, code, name, color, edit, delete = row
                
                if type_code != current_type:
                    logger.info(f"\n{type_code}:")
                    current_type = type_code
                
                logger.info(f"  - {code}: {name}")
                logger.info(f"      Color: {color}, Edit: {edit}, Delete: {delete}")
            
            return error_count == 0
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    logger.info("SWIFT Process States Creation Script")
    logger.info("")
    
    success = create_all_states()
    
    if success:
        logger.info("")
        logger.info("SUCCESS: All states created successfully")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("FAILED: Some errors occurred during creation")
        sys.exit(1)


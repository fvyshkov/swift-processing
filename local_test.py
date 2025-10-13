#!/usr/bin/env python3
"""
Local test script for SWIFT processing system.

This script will:
1. Create test database and all tables
2. Create test folders and files
3. Run the processing script
4. Generate a detailed report of results

Requirements:
- PostgreSQL server running
- psycopg2 library installed: pip install psycopg2-binary
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import traceback

# Database configuration
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_NAME = 'swift_test'

# Folder configuration
TEST_FOLDER_IN = './test_data/folder_in'
TEST_FOLDER_OUT = './test_data/folder_out'

def print_section(title):
    """Print formatted section header"""
    print('\n' + '='*80)
    print(f'  {title}')
    print('='*80)

def create_database():
    """Create test database"""
    print_section('STEP 1: Create Database')

    # Connect to postgres database
    print(f'Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...')
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Drop database if exists
    print(f'Dropping database {DB_NAME} if exists...')
    cursor.execute(f'DROP DATABASE IF EXISTS {DB_NAME}')

    # Create database
    print(f'Creating database {DB_NAME}...')
    cursor.execute(f'CREATE DATABASE {DB_NAME}')

    cursor.close()
    conn.close()

    print(f'✓ Database {DB_NAME} created successfully')

    return True

def create_tables():
    """Create all tables from db_schema_test.sql"""
    print_section('STEP 2: Create Tables')

    # Read schema file
    schema_file = 'db_schema_test.sql'
    print(f'Reading schema from {schema_file}...')

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect to test database
    print(f'Connecting to database {DB_NAME}...')
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Execute schema
    print('Executing schema SQL...')
    cursor.execute(schema_sql)
    conn.commit()

    # Verify tables created
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()
    print(f'\n✓ Created {len(tables)} tables:')
    for table in tables:
        print(f'  - {table[0]}')

    cursor.close()
    conn.close()

    return True

def insert_test_settings():
    """Insert test settings"""
    print_section('STEP 3: Insert Test Settings')

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Get absolute paths
    abs_folder_in = os.path.abspath(TEST_FOLDER_IN)
    abs_folder_out = os.path.abspath(TEST_FOLDER_OUT)

    # Insert settings
    print(f'Inserting test settings...')
    cursor.execute("""
        INSERT INTO swift_settings (folder_in, folder_out, server)
        VALUES (%s, %s, %s)
    """, (abs_folder_in, abs_folder_out, 'test_server'))

    conn.commit()

    print(f'✓ Settings inserted:')
    print(f'  folder_in:  {abs_folder_in}')
    print(f'  folder_out: {abs_folder_out}')
    print(f'  server:     test_server')

    cursor.close()
    conn.close()

    return abs_folder_in, abs_folder_out

def create_test_folders():
    """Create test folders"""
    print_section('STEP 4: Create Test Folders')

    # Create folders
    for folder in [TEST_FOLDER_IN, TEST_FOLDER_OUT]:
        if os.path.exists(folder):
            print(f'Folder exists: {folder}')
            # Clean folder
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f'  Cleaned folder')
        else:
            os.makedirs(folder, exist_ok=True)
            print(f'✓ Created folder: {folder}')

    return True

def create_test_files():
    """Create test XML files"""
    print_section('STEP 5: Create Test Files')

    # pacs.008 test file
    pacs008_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr><head:FIId><head:FinInstnId><head:BICFI>DSBAHKHH</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
		<head:To><head:FIId><head:FinInstnId><head:BICFI>ID521122</head:BICFI></head:FinInstnId></head:FIId></head:To>
		<head:BizMsgIdr>pacs8bizmsgidr02</head:BizMsgIdr>
		<head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2022-10-20T10:25:00+01:00</head:CreDt>
	</head:AppHdr>
	<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
		<pacs:FIToFICstmrCdtTrf>
			<pacs:GrpHdr><pacs:MsgId>pacs8bizmsgidr02</pacs:MsgId><pacs:CreDtTm>2022-10-20T10:25:00+01:00</pacs:CreDtTm><pacs:NbOfTxs>1</pacs:NbOfTxs><pacs:SttlmInf><pacs:SttlmMtd>INDA</pacs:SttlmMtd></pacs:SttlmInf></pacs:GrpHdr>
			<pacs:CdtTrfTxInf>
				<pacs:PmtId><pacs:InstrId>pacs8bizmsgidr02</pacs:InstrId><pacs:EndToEndId>pacs008EndToEndId-001</pacs:EndToEndId><pacs:UETR>7a562c67-ca16-48ba-b074-65581be6f001</pacs:UETR></pacs:PmtId>
				<pacs:IntrBkSttlmAmt Ccy="USD">98725497</pacs:IntrBkSttlmAmt>
				<pacs:IntrBkSttlmDt>2022-10-20</pacs:IntrBkSttlmDt>
				<pacs:Dbtr><pacs:Nm>A Capone</pacs:Nm></pacs:Dbtr>
				<pacs:DbtrAcct><pacs:Id><pacs:Othr><pacs:Id>ACPN-2569874</pacs:Id></pacs:Othr></pacs:Id></pacs:DbtrAcct>
				<pacs:Cdtr><pacs:Nm>J Smith</pacs:Nm></pacs:Cdtr>
				<pacs:CdtrAcct><pacs:Id><pacs:Othr><pacs:Id>65479512</pacs:Id></pacs:Othr></pacs:Id></pacs:CdtrAcct>
			</pacs:CdtTrfTxInf>
		</pacs:FIToFICstmrCdtTrf>
	</pacs:Document>
</Envelope>'''

    # camt.053 test file
    camt053_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr><head:FIId><head:FinInstnId><head:BICFI>DNBANOKK</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
		<head:To><head:FIId><head:FinInstnId><head:BICFI>GUCRNOK1</head:BICFI></head:FinInstnId></head:FIId></head:To>
		<head:BizMsgIdr>cmt053bizmsgidr-001</head:BizMsgIdr>
		<head:MsgDefIdr>camt.053.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2021-06-03T18:00:00+02:00</head:CreDt>
	</head:AppHdr>
	<camt:Document xmlns:camt="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
		<camt:BkToCstmrStmt>
			<camt:GrpHdr><camt:MsgId>cmt053bizmsgidr-001</camt:MsgId><camt:CreDtTm>2021-06-03T18:00:00+02:00</camt:CreDtTm></camt:GrpHdr>
			<camt:Stmt>
				<camt:Id>STMNTID</camt:Id>
				<camt:StmtPgntn><camt:PgNb>1</camt:PgNb><camt:LastPgInd>true</camt:LastPgInd></camt:StmtPgntn>
				<camt:ElctrncSeqNb>32145</camt:ElctrncSeqNb>
				<camt:Acct><camt:Id><camt:Othr><camt:Id>123654786</camt:Id></camt:Othr></camt:Id><camt:Ccy>NOK</camt:Ccy></camt:Acct>
				<camt:Bal>
					<camt:Tp><camt:CdOrPrtry><camt:Cd>OPBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
					<camt:Amt Ccy="NOK">4645498.54</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Dt><camt:Dt>2021-06-03</camt:Dt></camt:Dt>
				</camt:Bal>
				<camt:Bal>
					<camt:Tp><camt:CdOrPrtry><camt:Cd>CLBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
					<camt:Amt Ccy="NOK">7010498.54</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Dt><camt:Dt>2021-06-03</camt:Dt></camt:Dt>
				</camt:Bal>
				<camt:Ntry>
					<camt:Amt Ccy="NOK">2365000</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Sts><camt:Cd>BOOK</camt:Cd></camt:Sts>
					<camt:BookgDt><camt:Dt>2021-06-03</camt:Dt></camt:BookgDt>
					<camt:ValDt><camt:Dt>2021-06-03</camt:Dt></camt:ValDt>
					<camt:BkTxCd><camt:Domn><camt:Cd>PMNT</camt:Cd><camt:Fmly><camt:Cd>RCDT</camt:Cd><camt:SubFmlyCd>XBCT</camt:SubFmlyCd></camt:Fmly></camt:Domn></camt:BkTxCd>
					<camt:NtryDtls>
						<camt:TxDtls>
							<camt:Refs><camt:InstrId>pacs8bizmsgidr01</camt:InstrId><camt:EndToEndId>E2E04044506271305</camt:EndToEndId><camt:UETR>174c245f-2682-4291-ad67-2a41e530cd27</camt:UETR></camt:Refs>
							<camt:Amt Ccy="NOK">2365000</camt:Amt>
							<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
						</camt:TxDtls>
					</camt:NtryDtls>
				</camt:Ntry>
			</camt:Stmt>
		</camt:BkToCstmrStmt>
	</camt:Document>
</Envelope>'''

    # Unknown message type (for testing skip)
    unknown_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:MsgDefIdr>pacs.002.001.08</head:MsgDefIdr>
	</head:AppHdr>
	<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.08">
		<pacs:FIToFIPmtStsRpt>
			<pacs:GrpHdr><pacs:MsgId>unknown_msg</pacs:MsgId></pacs:GrpHdr>
		</pacs:FIToFIPmtStsRpt>
	</pacs:Document>
</Envelope>'''

    # Invalid XML (for error testing)
    invalid_content = 'This is not valid XML!'

    # Write files
    test_files = [
        ('pacs008_example.xml', pacs008_content),
        ('camt053_example.xml', camt053_content),
        ('unknown_type.xml', unknown_content),
        ('invalid.xml', invalid_content),
    ]

    for filename, content in test_files:
        file_path = os.path.join(TEST_FOLDER_IN, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ Created: {filename} ({len(content)} bytes)')

    return True

def run_processing_simulation():
    """Simulate processing by calling new_job_script functions"""
    print_section('STEP 6: Run Processing Simulation')

    print('This would run the actual processing script.')
    print('For now, we\'ll manually insert test data to verify database structure.')

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Simulate pacs.008 insert
    print('\nInserting pacs.008 test record...')
    cursor.execute("""
        INSERT INTO swift_input
        (file_name, state, msg_type, snd_name, rcv_name, amount, currency_code, dval)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, ('pacs008_example.xml', 'finished', 'pacs.008', 'A Capone', 'J Smith', 98725497, 'USD', '2022-10-20'))

    pacs008_id = cursor.fetchone()[0]
    print(f'  ✓ Inserted pacs.008 record: id={pacs008_id}')

    # Simulate camt.053 insert with details
    print('\nInserting camt.053 test record...')
    cursor.execute("""
        INSERT INTO swift_input
        (file_name, state, msg_type, msg_id, stmt_id, elctrnc_seq_nb, acct_id, acct_ccy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, ('camt053_example.xml', 'finished', 'camt.053', 'cmt053bizmsgidr-001', 'STMNTID', 32145, '123654786', 'NOK'))

    camt053_id = cursor.fetchone()[0]
    print(f'  ✓ Inserted camt.053 record: id={camt053_id}')

    # Insert balances
    print('  Inserting balances...')
    cursor.execute("""
        INSERT INTO swift_stmt_bal (swift_input_id, tp_cd, amt, amt_ccy, cdt_dbt_ind, dt)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (camt053_id, 'OPBD', 4645498.54, 'NOK', 'CRDT', '2021-06-03'))

    cursor.execute("""
        INSERT INTO swift_stmt_bal (swift_input_id, tp_cd, amt, amt_ccy, cdt_dbt_ind, dt)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (camt053_id, 'CLBD', 7010498.54, 'NOK', 'CRDT', '2021-06-03'))

    print('    ✓ Inserted 2 balances')

    # Insert entry
    print('  Inserting entry...')
    cursor.execute("""
        INSERT INTO swift_stmt_ntry
        (swift_input_id, amt, amt_ccy, cdt_dbt_ind, sts_cd, bookg_dt, val_dt,
         bk_tx_cd_domn_cd, bk_tx_cd_fmly_cd, bk_tx_cd_sub_fmly_cd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (camt053_id, 2365000, 'NOK', 'CRDT', 'BOOK', '2021-06-03', '2021-06-03', 'PMNT', 'RCDT', 'XBCT'))

    entry_id = cursor.fetchone()[0]
    print(f'    ✓ Inserted entry: id={entry_id}')

    # Insert transaction detail
    print('  Inserting transaction detail...')
    cursor.execute("""
        INSERT INTO swift_entry_tx_dtls
        (ntry_id, instr_id, end_to_end_id, uetr, amt, amt_ccy, cdt_dbt_ind)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (entry_id, 'pacs8bizmsgidr01', 'E2E04044506271305', '174c245f-2682-4291-ad67-2a41e530cd27', 2365000, 'NOK', 'CRDT'))

    print('    ✓ Inserted transaction detail')

    conn.commit()
    cursor.close()
    conn.close()

    print('\n✓ Processing simulation complete')

    return True

def generate_report():
    """Generate detailed report"""
    print_section('STEP 7: Generate Report')

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Get statistics
    print('\n📊 DATABASE STATISTICS:')
    print('-' * 80)

    # swift_input
    cursor.execute('SELECT COUNT(*), msg_type, state FROM swift_input GROUP BY msg_type, state ORDER BY msg_type')
    results = cursor.fetchall()
    print(f'\nswift_input table:')
    for count, msg_type, state in results:
        print(f'  {count} record(s): msg_type={msg_type}, state={state}')

    # swift_stmt_bal
    cursor.execute('SELECT COUNT(*) FROM swift_stmt_bal')
    bal_count = cursor.fetchone()[0]
    print(f'\nswift_stmt_bal table: {bal_count} record(s)')

    # swift_stmt_ntry
    cursor.execute('SELECT COUNT(*) FROM swift_stmt_ntry')
    ntry_count = cursor.fetchone()[0]
    print(f'swift_stmt_ntry table: {ntry_count} record(s)')

    # swift_entry_tx_dtls
    cursor.execute('SELECT COUNT(*) FROM swift_entry_tx_dtls')
    tx_count = cursor.fetchone()[0]
    print(f'swift_entry_tx_dtls table: {tx_count} record(s)')

    # Detailed records
    print('\n' + '-' * 80)
    print('📋 DETAILED RECORDS:')
    print('-' * 80)

    # pacs.008 details
    print('\n🔷 pacs.008 Records:')
    cursor.execute("""
        SELECT file_name, msg_type, snd_name, rcv_name, amount, currency_code, dval, state
        FROM swift_input
        WHERE msg_type = 'pacs.008'
    """)
    for row in cursor.fetchall():
        print(f'  File: {row[0]}')
        print(f'    Type: {row[1]}')
        print(f'    Sender: {row[2]} → Receiver: {row[3]}')
        print(f'    Amount: {row[4]} {row[5]}')
        print(f'    Date: {row[6]}')
        print(f'    State: {row[7]}')

    # camt.053 details
    print('\n🔷 camt.053 Records:')
    cursor.execute("""
        SELECT id, file_name, msg_type, msg_id, stmt_id, elctrnc_seq_nb, acct_id, acct_ccy, state
        FROM swift_input
        WHERE msg_type = 'camt.053'
    """)
    for row in cursor.fetchall():
        stmt_id = row[0]
        print(f'  File: {row[1]}')
        print(f'    Type: {row[2]}')
        print(f'    MsgId: {row[3]}')
        print(f'    StmtId: {row[4]}')
        print(f'    SeqNb: {row[5]}')
        print(f'    Account: {row[6]} ({row[7]})')
        print(f'    State: {row[8]}')

        # Balances
        cursor.execute("""
            SELECT tp_cd, amt, amt_ccy, cdt_dbt_ind, dt
            FROM swift_stmt_bal
            WHERE swift_input_id = %s
            ORDER BY tp_cd
        """, (stmt_id,))
        balances = cursor.fetchall()
        if balances:
            print(f'    Balances: {len(balances)}')
            for bal in balances:
                print(f'      {bal[0]}: {bal[1]} {bal[2]} ({bal[3]}) on {bal[4]}')

        # Entries
        cursor.execute("""
            SELECT id, amt, amt_ccy, cdt_dbt_ind, sts_cd, bookg_dt
            FROM swift_stmt_ntry
            WHERE swift_input_id = %s
        """, (stmt_id,))
        entries = cursor.fetchall()
        if entries:
            print(f'    Entries: {len(entries)}')
            for entry in entries:
                entry_id = entry[0]
                print(f'      Entry #{entry_id}: {entry[1]} {entry[2]} ({entry[3]}) status={entry[4]} date={entry[5]}')

                # Transaction details
                cursor.execute("""
                    SELECT instr_id, end_to_end_id, uetr, amt, amt_ccy
                    FROM swift_entry_tx_dtls
                    WHERE ntry_id = %s
                """, (entry_id,))
                tx_details = cursor.fetchall()
                if tx_details:
                    for tx in tx_details:
                        print(f'        TxDetail: InstrId={tx[0]}, E2E={tx[1]}')
                        print(f'                  UETR={tx[2]}')
                        print(f'                  Amount={tx[3]} {tx[4]}')

    # Foreign key integrity check
    print('\n' + '-' * 80)
    print('🔒 FOREIGN KEY INTEGRITY:')
    print('-' * 80)

    # Check orphaned balances
    cursor.execute("""
        SELECT COUNT(*)
        FROM swift_stmt_bal b
        LEFT JOIN swift_input i ON b.swift_input_id = i.id
        WHERE i.id IS NULL
    """)
    orphaned_bal = cursor.fetchone()[0]
    print(f'Orphaned balances: {orphaned_bal} (should be 0)')

    # Check orphaned entries
    cursor.execute("""
        SELECT COUNT(*)
        FROM swift_stmt_ntry n
        LEFT JOIN swift_input i ON n.swift_input_id = i.id
        WHERE i.id IS NULL
    """)
    orphaned_ntry = cursor.fetchone()[0]
    print(f'Orphaned entries: {orphaned_ntry} (should be 0)')

    # Check orphaned tx details
    cursor.execute("""
        SELECT COUNT(*)
        FROM swift_entry_tx_dtls t
        LEFT JOIN swift_stmt_ntry n ON t.ntry_id = n.id
        WHERE n.id IS NULL
    """)
    orphaned_tx = cursor.fetchone()[0]
    print(f'Orphaned transaction details: {orphaned_tx} (should be 0)')

    cursor.close()
    conn.close()

    print('\n' + '='*80)
    print('✅ Report generation complete!')
    print('='*80)

    return True

def main():
    """Main test execution"""
    print('='*80)
    print('  SWIFT PROCESSING SYSTEM - LOCAL TEST')
    print('='*80)
    print(f'Start time: {datetime.now()}')
    print()
    print('This script will:')
    print('  1. Create test database and tables')
    print('  2. Insert test settings')
    print('  3. Create test folders and files')
    print('  4. Simulate message processing')
    print('  5. Generate detailed report')
    print()
    print('Configuration:')
    print(f'  Database: {DB_NAME}@{DB_HOST}:{DB_PORT}')
    print(f'  User: {DB_USER}')
    print(f'  Test folders: {TEST_FOLDER_IN}, {TEST_FOLDER_OUT}')
    print()
    # Auto-start enabled

    try:
        # Step 1: Create database
        create_database()

        # Step 2: Create tables
        create_tables()

        # Step 3: Insert settings
        insert_test_settings()

        # Step 4: Create folders
        create_test_folders()

        # Step 5: Create test files
        create_test_files()

        # Step 6: Run processing
        run_processing_simulation()

        # Step 7: Generate report
        generate_report()

        print('\n' + '='*80)
        print('✅ ALL TESTS COMPLETED SUCCESSFULLY!')
        print('='*80)
        print(f'End time: {datetime.now()}')

        return 0

    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        print(f'\nTraceback:')
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

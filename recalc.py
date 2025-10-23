import json
import logging
import requests
from apng_core.db import initDbSession, fetchone
from apng_core.exceptions import UserException
from apng_core.auth import getUser

# Initialize logger
logger = logging.getLogger('recalc')

# Claude API configuration
CLAUDE_API_KEY = "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"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"


def parse_address_with_llm(address_string):
    prompt = f"""Parse the following address into structured fields. Return ONLY a JSON object with these exact keys: postal_code, country, region, city, street, building.

Address: {address_string}

Rules:
- If a field is not present in the address, use null
- Extract postal/zip code if present
- Identify country (full name or code)
- Extract region/oblast/state if present
- Extract city/town name
- Extract street name
- Extract building/house number

Return ONLY the JSON object, no explanations."""

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 500,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    response_data = response.json()
    response_text = response_data['content'][0]['text'].strip()
    
    # Try to parse JSON from response
    # Sometimes Claude wraps JSON in markdown code blocks
    if response_text.startswith('```'):
        # Extract JSON from code block
        lines = response_text.split('\n')
        json_lines = [l for l in lines if l and not l.startswith('```') and not l.startswith('json')]
        response_text = '\n'.join(json_lines)
    
    parsed = json.loads(response_text)
    
    # Ensure all expected keys are present
    result = {
        'postal_code': parsed.get('postal_code'),
        'country': parsed.get('country'),
        'region': parsed.get('region'),
        'city': parsed.get('city'),
        'street': parsed.get('street'),
        'building': parsed.get('building')
    }
    
    logger.debug(f"Successfully parsed address: {address_string}")
    logger.debug(f"Result: {result}")
    
    return result
    


# Main execution
user = getUser()
user_str = user.code

dep_id = parameters.get('app').get('record').get('DEP_ID')
id = parameters.get('app').get('record').get('ID')

if not dep_id or not id:
    raise UserException({'message': 'Missing dep_id or id in parameters'})


# Read addresses from Colvir CBS (Oracle) database
with initDbSession(application='colvir_cbs').cursor() as cursor:
    # Query to get addresses from Oracle DB
    address_sql = """
        select g_pkgaddress.fGetFullAddr(msg.rcv_adr_id) rcv_address,
               g_pkgaddress.fGetFullAddr(msg.snd_adr_id) snd_address
        from  P_ORDROUTE P, C_USR U, P_ORDEXT E,
              P_SYS_STD S1, P_SYS_STD S2,
              T_BOP_STAT ST, T_BOP_DSCR DS, T_PROCESS PR, T_PROCMEM PM, T_VAL_STD V, T_ORD O, P_ORD J
              ,T_PROCDET PATTR
            , P_STFORD SF
            , P_STF_STD SS
            , P_ORDMSG MSG
        where msg.work_dep_id(+) = j.dep_id
          and msg.work_id(+) = j.id 
          and O.DEP_ID = J.DEP_ID
          and O.ID = J.ID
          and V.ID = O.VAL_ID
          and PM.ORD_ID = O.ID
          and PM.DEP_ID = O.DEP_ID
          and PM.MAINFL IN ('1', CASE WHEN ST.CODE = 'STF' AND DS.CODE IN ('PSP_IN', 'PSP_OUT') THEN '0' ELSE '1' END)
          and PR.ID = PM.ID
          and DS.ID = PR.BOP_ID
          and ST.ID = DS.ID
          and ST.NORD = PR.NSTAT
          and P.DEP_ID(+) = j.DEP_ID
          and P.ID(+) = J.ID
          and U.ID(+) = O.ID_US
          and E.ID(+) = J.EXT_ID
          and S1.ID(+) = J.PAYRCV_ID
          and S2.ID(+) = J.PAYSND_ID
          and SF.DEP_ID(+) = J.DEP_ID
          and SF.ORD_ID(+) = J.ID
          and SS.ID(+) = SF.STF_ID
          and O.PLANFL = 0
          and exists (
            select 1 from DUAL
           where C_PKGGRANT.FCHKGRNDEP(O.DEP_ID, O.ID, 3)=1)  
          and PATTR.ID(+) = PR.ID and PATTR.CODE(+) = 'POS'
          and BS_OPERATION.fIsParentWait(PR.ID) = 0 
          and ds.CODE||'' = 'PSP_OUT'
          and j.id = :id
          and j.dep_id = :dep_id
    """
    
    cursor.execute(address_sql, {'id': id, 'dep_id': dep_id})
    address_row = fetchone(cursor)
    if not address_row:
        raise UserException({
            'message': 'No data found for specified dep_id and id',
            'description': f'dep_id={dep_id}, id={id}'
        })
    
    rcv_address = address_row.get('RCV_ADDRESS', '')
    snd_address = address_row.get('SND_ADDRESS', '')
    
    logger.debug(f"Receiver address from Colvir CBS: {rcv_address}")
    logger.debug(f"Sender address from Colvir CBS: {snd_address}")

# Parse addresses using Claude AI
logger.info("Parsing receiver address with Claude AI...")
rcv_parsed = parse_address_with_llm(rcv_address)

logger.info("Parsing sender address with Claude AI...")
snd_parsed = parse_address_with_llm(snd_address)

# Write parsed data to PostgreSQL (default database)
with initDbSession(database='default').cursor() as c:
    # Insert/update parsed address fields
    insert_sql = """
        insert into swift_out_fields (
            dep_id, id, 
            rcv_postal_code, rcv_country, rcv_region, rcv_city, rcv_street, rcv_building,
            snd_postal_code, snd_country, snd_region, snd_city, snd_street, snd_building,
            modified
        )
        values (
            %(dep_id)s, %(id)s,
            %(rcv_postal_code)s, %(rcv_country)s, %(rcv_region)s, %(rcv_city)s, %(rcv_street)s, %(rcv_building)s,
            %(snd_postal_code)s, %(snd_country)s, %(snd_region)s, %(snd_city)s, %(snd_street)s, %(snd_building)s,
            now()
        )
        on conflict (dep_id, id)
        do update set
            rcv_postal_code = excluded.rcv_postal_code,
            rcv_country = excluded.rcv_country,
            rcv_region = excluded.rcv_region,
            rcv_city = excluded.rcv_city,
            rcv_street = excluded.rcv_street,
            rcv_building = excluded.rcv_building,
            snd_postal_code = excluded.snd_postal_code,
            snd_country = excluded.snd_country,
            snd_region = excluded.snd_region,
            snd_city = excluded.snd_city,
            snd_street = excluded.snd_street,
            snd_building = excluded.snd_building,
            modified = now();
    """
    
    c.execute(insert_sql, {
        'dep_id': dep_id,
        'id': id,
        'rcv_postal_code': rcv_parsed['postal_code'],
        'rcv_country': rcv_parsed['country'],
        'rcv_region': rcv_parsed['region'],
        'rcv_city': rcv_parsed['city'],
        'rcv_street': rcv_parsed['street'],
        'rcv_building': rcv_parsed['building'],
        'snd_postal_code': snd_parsed['postal_code'],
        'snd_country': snd_parsed['country'],
        'snd_region': snd_parsed['region'],
        'snd_city': snd_parsed['city'],
        'snd_street': snd_parsed['street'],
        'snd_building': snd_parsed['building']
    })
    
    
    # Commit transaction
    c.connection.commit()

import json
import logging
import requests
from apng_core.db import initDbSession, fetchone
from apng_core.exceptions import UserException
from apng_core.auth import getUser

# Initialize logger
logger = logging.getLogger('recalc')

# Together AI configuration
TOGETHER_API_KEY = "fb64c5f9af4418fa785aebcc1dd47b0d1462691be8a1e04d0c84dec490c4d18c"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
# Recommended models for structured output
TOGETHER_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"  # Good for JSON


def parse_address_with_llm(address_string):
    """Parse address using Together AI API with robust response handling"""
    
    if not address_string or not address_string.strip():
        return {
            'postal_code': None,
            'country': None,
            'region': None,
            'city': None,
            'street': None,
            'building': None
        }
    
    prompt = f"""Parse the following address into structured fields. Return ONLY a valid JSON object with these exact keys: postal_code, country, region, city, street, building.

Address: {address_string}

Rules:
- If a field is not present in the address, use null
- Extract postal/zip code if present
- Identify country (full name or code)
- Extract region/oblast/state if present
- Extract city/town name
- Extract street name
- Extract building/house number

Return ONLY valid JSON object, no explanations, no markdown, just pure JSON."""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that parses addresses into structured JSON format. Always return only valid JSON without any markdown formatting or explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1,
        "top_p": 0.9,
        "stop": ["```", "\n\n\n"]
    }
    
    response = requests.post(
        TOGETHER_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    
    logger.debug(f"Response status code: {response.status_code}")
    
    if response.status_code != 200:
        logger.error(f"Together API error: {response.status_code}")
        logger.error(f"Response: {response.text}")
        raise UserException({
            'message': f'Together API error: {response.status_code}',
            'description': response.text
        })
    
    response_data = response.json()
    logger.debug(f"Full response: {json.dumps(response_data, indent=2)}")
    raise Exception(response_data)
    # Extract text from response - handle different response formats
    response_text = None
    
    # Try to get content from choices
    if 'choices' in response_data and len(response_data['choices']) > 0:
        choice = response_data['choices'][0]
        
        # Check 'message' field
        if 'message' in choice:
            message = choice['message']
            
            # Priority 1: content field
            if 'content' in message and message['content']:
                response_text = message['content'].strip()
                logger.debug(f"Got response from 'content' field")
            
            # Priority 2: reasoning field (some models use this)
            elif 'reasoning' in message and message['reasoning']:
                response_text = message['reasoning'].strip()
                logger.debug(f"Got response from 'reasoning' field")
        
        # Check 'text' field directly in choice
        elif 'text' in choice and choice['text']:
            response_text = choice['text'].strip()
            logger.debug(f"Got response from 'text' field")
    
    if not response_text:
        logger.error(f"Could not extract text from response: {response_data}")
        raise UserException({
            'message': 'Empty response from AI',
            'description': 'No content found in API response'
        })
    
    logger.debug(f"Raw response text: {response_text}")
    
    # Clean up response - remove markdown
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif '```' in response_text:
        # Find JSON between first ``` and last ```
        parts = response_text.split('```')
        if len(parts) >= 3:
            response_text = parts[1].strip()
    
    # Remove JSON word at start if present
    if response_text.lower().startswith('json'):
        response_text = response_text[4:].strip()
    
    # Extract just the JSON object if there's text before/after
    if '{' in response_text and '}' in response_text:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        response_text = response_text[start_idx:end_idx + 1]
    
    # Попытка парсинга JSON
    parsed = None
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"First JSON parse failed: {e}")
        logger.debug(f"Failed text: {response_text}")
        
        # Try to fix common issues
        response_text_fixed = response_text.replace("'", '"')
        response_text_fixed = response_text_fixed.replace('None', 'null')
        response_text_fixed = response_text_fixed.replace('True', 'true')
        response_text_fixed = response_text_fixed.replace('False', 'false')
        
        try:
            parsed = json.loads(response_text_fixed)
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse JSON after fixes")
            logger.error(f"Original: {response_text}")
            logger.error(f"Fixed: {response_text_fixed}")
            
            # Return empty result instead of failing
            return {
                'postal_code': None,
                'country': None,
                'region': None,
                'city': None,
                'street': None,
                'building': None
            }
    
    # Формируем результат
    result = {
        'postal_code': parsed.get('postal_code'),
        'country': parsed.get('country'),
        'region': parsed.get('region'),
        'city': parsed.get('city'),
        'street': parsed.get('street'),
        'building': parsed.get('building')
    }
    
    logger.info(f"Successfully parsed address: {address_string}")
    logger.debug(f"Result: {result}")
    
    return result
    
    


# Main execution
user = getUser()
user_str = user.code

dep_id = parameters.get('app').get('record').get('DEP_ID')
id = parameters.get('app').get('record').get('ID')

if not dep_id or not id:
    raise UserException({'message': 'Missing dep_id or id in parameters'})

logger.debug(f"Processing dep_id={dep_id}, id={id}, user={user_str}")

# Read addresses from Colvir CBS
with initDbSession(application='colvir_cbs').cursor() as cursor:
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

# Parse addresses using Together AI
logger.info("Parsing receiver address with AI...")
rcv_parsed = parse_address_with_llm(rcv_address)

logger.info("Parsing sender address with AI...")
snd_parsed = parse_address_with_llm(snd_address)

# Write parsed data to PostgreSQL
with initDbSession(database='default').cursor() as c:
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
    
    c.connection.commit()

logger.info("✓ Address parsing and saving completed successfully")


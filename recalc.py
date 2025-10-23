from apng_core.db import fetchone
from apng_core.exceptions import UserException
from apng_core.auth import getUser
import time

with initDbSession(database='default').cursor() as c:
    SQL = """
        insert into swift_out_fields (dep_id, id, field1, field2)
        values (%(dep_id)s, %(id)s, %(field1)s, %(field2)s)
        on conflict (dep_id, id)
        do update set
            field1 = excluded.field1,
            field2 = excluded.field2;
    """
    #raise Exception( parameters)
    try:
      user = getUser()
      user_str = user.code
      
      field_1_new_val = str(time.time())
      field_2_new_val = str(time.time())
      
      c.execute(SQL, { 
            'dep_id': parameters.get('app').get('record').get('DEP_ID'), 
            'id': parameters.get('app').get('record').get('ID'), 
            'field1': field_1_new_val, 
            'field2': field_2_new_val 
          
      })
    except Exception as e:
      raise UserException({'message': str(e)})

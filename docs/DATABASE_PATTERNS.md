# Паттерны работы с базами данных

## Архитектура БД

Система использует две базы данных:

1. **PostgreSQL** (`database='default'`) - основная БД для SWIFT сообщений
2. **Oracle** (`application='colvir_cbs'`) - банковская система Colvir CBS

## Работа с PostgreSQL

### Основные таблицы

```sql
-- Главная таблица входящих сообщений
swift_input (
    id UUID PRIMARY KEY,
    file_name TEXT NOT NULL,
    state TEXT NOT NULL,
    msg_type TEXT,           -- pacs.008, pacs.009, camt.053, camt.054, camt.056
    msg_id TEXT,
    amount NUMERIC,
    currency_code TEXT,
    -- ... много других полей
)

-- Дополнительные поля для исходящих
swift_out_fields (
    dep_id INTEGER,
    id INTEGER,
    rcv_postal_code TEXT,    -- Распарсенный адрес получателя
    rcv_country TEXT,
    rcv_city TEXT,
    content TEXT,            -- Сгенерированный XML
    PRIMARY KEY (dep_id, id)
)

-- Управление процессами
process_type (code, name_en, name_ru, ...)
process_state (id, type_code, code, ...)
process_operation (id, type_code, code, ...)
process_operation_states (operation_id, state_id)
process (id, swift_input_id, state_id)
```

### Паттерны запросов PostgreSQL

#### Простой SELECT
```python
"methods": {
    "getList": {
        "sql": {
            "sqlType": "query",
            "database": "default",
            "sql": "SELECT * FROM swift_input WHERE state = :state ORDER BY imported DESC"
        }
    }
}
```

#### INSERT с возвратом ID
```python
"script": {
    "py": """
SQL = '''
    INSERT INTO swift_out_fields (dep_id, id, content)
    VALUES (%(dep_id)s, %(id)s, %(content)s)
    ON CONFLICT (dep_id, id) DO UPDATE SET
        content = EXCLUDED.content,
        modified = now()
    RETURNING dep_id, id
'''

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, parameters)
    data = fetchone(c)
"""
}
```

#### Фильтрация с параметрами
```python
"script": {
    "py": """
from apng_core.db import fetchall
from apng_core.aoa.services import filter as aoa

SQL = '''SELECT * FROM process_state WHERE 1=1'''
params = {}

# Добавление условий
if parameters.get('type_code'):
    SQL += ' AND type_code = %(type_code)s'
    params['type_code'] = parameters['type_code']

# Использование LIKE
if parameters.get('name'):
    SQL += ' AND UPPER(name_ru) LIKE UPPER(%(name)s)'
    params['name'] = f"%{parameters['name']}%"

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, params)
    data = fetchall(c)
"""
}
```

#### Работа с транзакциями
```python
"script": {
    "py": """
with initDbSession(database='default').cursor() as c:
    # Все операции в одной транзакции
    
    # 1. Удаляем старые связи
    c.execute('DELETE FROM process_operation_states WHERE operation_id = %(id)s', 
              {'id': operation_id})
    
    # 2. Добавляем новые
    for state_id in state_ids:
        c.execute('''
            INSERT INTO process_operation_states (operation_id, state_id)
            VALUES (%(op_id)s, %(st_id)s)
        ''', {'op_id': operation_id, 'st_id': state_id})
    
    # Транзакция автоматически коммитится при выходе из контекста
"""
}
```

## Работа с Oracle (Colvir CBS)

### Особенности Oracle

1. **Имена таблиц**: Используются префиксы (P_ORD, T_VAL, G_BNK и т.д.)
2. **Функции**: Вызов пакетных функций через точку (T_PKGMONEY.FTRNVALUETOMONEY)
3. **Операторы**: Конкатенация через `||`, не `+`
4. **Параметры**: Используется формат `:param` или `%(param)s`

### Паттерны запросов Oracle

#### Чтение данных из Colvir
```python
"methods": {
    "getList": {
        "sql": {
            "sqlType": "query", 
            "database": "colvir_cbs",
            "sql": """
                SELECT /*+ rule*/
                    J.DVAL,
                    J.DEP_ID,
                    J.ID,
                    T_PKGMONEY.FTRNVALUETOMONEY(J.SDOK) as SDOK,
                    V.CODE as VAL_CODE
                FROM P_ORD J, T_VAL V
                WHERE V.ID = J.VAL_ID
                  AND J.DVAL = to_date(:date_param, 'dd.mm.yyyy')
            """
        }
    }
}
```

#### Вызов хранимых процедур
```python
"script": {
    "py": """
with initDbSession(application='colvir_cbs').cursor() as c:
    SQL = '''
        DECLARE 
           sdep_id  INT := :dep_id;
           sid      INT := :id;
        BEGIN
            -- Вызов процедуры
            p_package.procedure_name(sdep_id, sid);
            
            -- Возврат результата
            :result := 'SUCCESS';
        END;
    '''
    
    # Подготовка OUT параметров
    result = c.var(str)
    
    c.execute(SQL, {
        'dep_id': parameters.get('dep_id'),
        'id': parameters.get('id'),
        'result': result
    })
    
    data = {'status': result.getvalue()}
"""
}
```

#### Сложные запросы с джойнами
```python
"sql": """
SELECT 
    T_VAL.CODE VAL_CODE,
    G_ACCBLN.CODE ACC_CODE,
    G_BNK.CODE BANK,
    substr(g_pkgBnk.fGetLongNameBnk_Id(G_BNK.ID), 1, 250) BANK_NAME
FROM 
    T_PROCESS, T_PROCMEM, T_BOP_STAT, T_DEA, T_DEACLS,
    G_ACCBLN, G_BNK, P_ACCDSC, T_VAL, 
    P_BNKACC, I_BNKREL, I_DEAREL
WHERE I_DEAREL.COR_ID = I_BNKREL.ID
  AND I_BNKREL.ID = P_BNKACC.ID
  AND P_BNKACC.DEP_ID = G_ACCBLN.DEP_ID (+)  -- LEFT JOIN
  AND P_BNKACC.LINK_ID = G_ACCBLN.ID (+)
  -- ... остальные условия
"""
```

## Смешанные запросы (PostgreSQL + Oracle)

Часто требуется получить данные из обеих БД:

```python
"script": {
    "py": """
# 1. Получаем данные из Oracle
with initDbSession(application='colvir_cbs').cursor() as c:
    c.execute('''
        SELECT J.DEP_ID, J.ID, J.SDOK as amount, V.CODE as currency
        FROM P_ORD J, T_VAL V
        WHERE V.ID = J.VAL_ID AND J.ID = %(id)s
    ''', {'id': parameters['id']})
    oracle_data = fetchone(c)

# 2. Обновляем PostgreSQL
with initDbSession(database='default').cursor() as c:
    c.execute('''
        UPDATE swift_out_fields 
        SET amount = %(amount)s, currency = %(currency)s
        WHERE id = %(id)s
    ''', {
        'id': parameters['id'],
        'amount': oracle_data['AMOUNT'],
        'currency': oracle_data['CURRENCY']
    })

data = {'success': True}
"""
}
```

## Обработка ошибок

### UserException для пользовательских ошибок
```python
from apng_core.exceptions import UserException

try:
    # операция
except Exception as e:
    raise UserException({
        'message': 'Ошибка сохранения',
        'description': str(e)
    })
```

### Проверка существования данных
```python
SQL = "SELECT * FROM swift_input WHERE id = %(id)s"
c.execute(SQL, {'id': parameters['id']})
data = fetchone(c)

if not data:
    raise UserException({
        'message': 'Запись не найдена',
        'description': f'ID: {parameters["id"]}'
    })
```

## Оптимизация запросов

### Использование индексов
```sql
-- В схеме БД созданы индексы
CREATE INDEX idx_swift_input_msg_type ON swift_input(msg_type);
CREATE INDEX idx_swift_input_state ON swift_input(state);
```

### Ограничение выборки
```python
# Пагинация для больших списков
if request and request.get('startRow') is not None:
    startRow = int(request.get('startRow'))
    endRow = int(request.get('endRow'))
    SQL += ' OFFSET %s ROWS FETCH NEXT %s ROWS ONLY' % (
        startRow, endRow - startRow + 1
    )
```

### Кеширование
```javascript
// В JavaScript коде
backend.post('/aoa/execObjectMethod', {
    object: 'settings',
    method: 'get'
}, {
    useCache: true,      // Включить кеширование
    silent: true         // Не показывать индикатор загрузки
})
```

## Специфичные паттерны

### Работа с UUID
```python
import uuid

# Генерация нового UUID
new_id = str(uuid.uuid4())

# В SQL
c.execute('INSERT INTO table (id) VALUES (%(id)s::uuid)', 
          {'id': new_id})
```

### Работа с JSON в PostgreSQL
```python
# Сохранение JSON
availability_condition = json.dumps({
    'target_state': 'PROCESSED',
    'available_in_states': ['LOADED']
})

# Чтение и парсинг
condition = json.loads(row['availability_condition'])
```

### Динамическое построение SQL
```python
# Безопасное построение WHERE условий
conditions = []
params = {}

if filter_data.get('state'):
    conditions.append('state = %(state)s')
    params['state'] = filter_data['state']

if filter_data.get('amount_from'):
    conditions.append('amount >= %(amount_from)s')
    params['amount_from'] = filter_data['amount_from']

where_clause = ' AND '.join(conditions) if conditions else '1=1'
SQL = f'SELECT * FROM table WHERE {where_clause}'
```

## Рекомендации

1. **Всегда используйте параметризованные запросы** - никогда не конкатенируйте значения в SQL
2. **Проверяйте типы БД** - `database='default'` для PostgreSQL, `application='colvir_cbs'` для Oracle
3. **Используйте контекстные менеджеры** - `with initDbSession()` для автоматического управления транзакциями
4. **Обрабатывайте NULL значения** - используйте `row.get('field')` вместо `row['field']`
5. **Логируйте важные операции** - используйте `logging.getLogger()`
6. **Не изменяйте данные в Oracle** - только чтение из Colvir CBS
7. **Соблюдайте соглашения об именовании** - snake_case для PostgreSQL, UPPER_CASE для Oracle

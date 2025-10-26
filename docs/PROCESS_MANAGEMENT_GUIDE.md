# Система управления процессами (Process Management)

## Общая концепция

Система управления процессами в SWIFT Processing обеспечивает workflow для обработки различных типов SWIFT сообщений. Каждое сообщение проходит через определенные состояния (states) с помощью операций (operations).

## Компоненты системы

### 1. Process Type (Типы процессов)

Определяют типы SWIFT сообщений, которые может обрабатывать система:

```sql
process_type (
    code TEXT PRIMARY KEY,      -- pacs.008, pacs.009, camt.053, camt.054, camt.056
    name_en TEXT,              -- Английское название
    name_ru TEXT,              -- Русское название  
    name_combined TEXT,        -- Комбинированное название
    resource_url TEXT          -- URL для открытия формы
)
```

Текущие типы:
- `pacs.008` - Customer Credit Transfer (Клиентский кредитовый перевод)
- `pacs.009` - Financial Institution Credit Transfer (Межбанковский перевод)
- `camt.053` - Bank to Customer Statement (Банковская выписка)
- `camt.054` - Bank to Customer Debit/Credit Notification (Уведомление)
- `camt.056` - FI to FI Payment Cancellation Request (Запрос на отмену)

### 2. Process State (Состояния процессов)

Определяют возможные состояния для каждого типа процесса:

```sql
process_state (
    id UUID PRIMARY KEY,
    type_code TEXT,            -- Ссылка на process_type
    code TEXT,                 -- Код состояния (LOADED, PROCESSED, etc)
    name_en TEXT,
    name_ru TEXT,
    name_combined TEXT,
    color_code TEXT,           -- Цвет для UI (#FF8C00)
    allow_edit BOOLEAN,        -- Разрешено редактирование
    allow_delete BOOLEAN,      -- Разрешено удаление
    start BOOLEAN             -- Начальное состояние
)
```

Примеры состояний:
- `LOADED` - Загружен (начальное, #FF8C00)
- `PROCESSED` - Обработан (#00AA44)
- `PAYMENT_CREATED` - Платеж создан (#008000)

### 3. Process Operation (Операции)

Определяют действия, доступные в определенных состояниях:

```sql
process_operation (
    id UUID PRIMARY KEY,
    type_code TEXT,
    code TEXT,                      -- Код операции
    name_en TEXT,
    name_ru TEXT, 
    name_combined TEXT,
    icon TEXT,                      -- Иконка (check, undo, payment)
    resource_url TEXT,              -- Процедура/URL
    availability_condition TEXT,    -- JSON с условиями доступности
    cancel BOOLEAN,                 -- Операция отмены
    to_state TEXT,                  -- Целевое состояние
    database TEXT                   -- БД для выполнения
)
```

### 4. Process Operation States (Связь операций и состояний)

Many-to-many связь между операциями и состояниями:

```sql
process_operation_states (
    operation_id UUID,
    state_id UUID,
    PRIMARY KEY (operation_id, state_id)
)
```

### 5. Process (Экземпляры процессов)

Конкретные экземпляры процессов для каждого SWIFT сообщения:

```sql
process (
    id UUID PRIMARY KEY,
    doc_id UUID,      -- Ссылка на сообщение
    state_id UUID             -- Текущее состояние
)
```

## Объект processManagement

Центральный объект для управления процессами (`processManagement.json`):

### Списки (Lists)

#### typeList - Список типов процессов
```json
{
    "getList": "getTypeList",
    "columns": {
        "code": {"title": "Code", "width": 150},
        "name_combined": {"title": "Name", "flex": 1}
    },
    "actions": [
        // Добавить, редактировать, удалить типы
    ]
}
```

#### stateList - Список состояний
```json
{
    "getList": "getStateList",
    "getRowStyle": "{background: data?.color_code}",  // Цвет строки
    "columns": {
        "type_code": {"title": "Type"},
        "code": {"title": "State Code"},
        "color_code": {"title": "Color"},
        "allow_edit": {"control": "checkbox"}
    }
}
```

#### operationList - Список операций
```json
{
    "getList": "getOperationList",
    "columns": {
        "type_code": {"title": "Type"},
        "code": {"title": "Operation Code"},
        "icon": {"title": "Icon"},
        "resource_url": {"title": "Resource URL"}
    }
}
```

### Формы (Forms)

#### editType - Редактирование типа процесса
```json
{
    "$": {
        "code": {
            "label": "Code",
            "control": "TextEdit",
            "required": true,
            "readOnly$": "!!mem.original_code"  // Нельзя менять код
        },
        "name_en": {"label": "English Name"},
        "name_ru": {"label": "Russian Name"},
        "resource_url": {"label": "Resource URL"}
    }
}
```

#### editState - Редактирование состояния
```json
{
    "$": {
        "type_code": {
            "label": "Type",
            "control": "ObjectReference",
            "controlProps": {
                "object": "processType"
            }
        },
        "code": {"label": "State Code"},
        "color_code": {
            "label": "Color Code (hex)",
            "placeholder": "#RRGGBB"
        },
        "@flags": {
            "$": {
                "allow_edit": {"control": "Checkbox"},
                "allow_delete": {"control": "Checkbox"}
            }
        },
        "@form-1": {
            "form": "operInnerList"  // Список операций для состояния
        }
    }
}
```

#### editOperation - Редактирование операции
```json
{
    "$": {
        "type_code": {"control": "ObjectReference"},
        "code": {"label": "Operation Code"},
        "icon": {
            "label": "Icon",
            "placeholder": "e.g. send, check, approve"
        },
        "resource_url": {
            "label": "Procedure",
            "control": "TextEdit",
            "controlProps": {"multiline": true}
        },
        "availability_condition": {
            "label": "Availability Condition (JSON)",
            "control": "TextArea"
        },
        "state_codes": {
            "label": "Available in States",
            "control": "TextArea",
            "placeholder": "Enter state codes, one per line"
        }
    }
}
```

## Workflow процесса

### 1. Создание процесса

При импорте SWIFT сообщения:
1. Создается запись в `swift_input`
2. Определяется тип процесса по `msg_type`
3. Создается экземпляр в `process` с начальным состоянием

### 2. Выполнение операций

Операции выполняются автоматически через унифицированный метод `runOperations`. Система сама определяет доступные операции на основе текущего состояния процесса.

```javascript
// Операции вызываются через стандартный механизм
backend.post('/aoa/execObjectMethod', {
    object: 'swiftIncome',
    method: 'runOperations',
    params: {
        process_id: processId,
        operation_code: 'MARK_AS_PROCESSED'
    }
})
```

**Важно**: Вам НЕ нужно создавать отдельные методы для каждой операции!

### 3. Смена состояний

Операция может перевести процесс в новое состояние:

```python
# В методе executeOperation
def change_state(process_id, new_state_code):
    SQL = """
        UPDATE process 
        SET state_id = (
            SELECT id FROM process_state 
            WHERE code = %(state_code)s 
            AND type_code = (
                SELECT ps.type_code 
                FROM process p
                JOIN process_state ps ON p.state_id = ps.id
                WHERE p.id = %(process_id)s
            )
        )
        WHERE id = %(process_id)s
    """
```

## Условия доступности операций

### availability_condition

JSON объект, определяющий условия доступности операции:

```json
{
    "target_state": "PROCESSED",
    "available_in_states": ["LOADED"],
    "custom_condition": "hasPaymentDetails"
}
```

### Проверка доступности в UI

```javascript
// В действиях списка
"disabled$": "!isOperationAvailable($listRow.state, 'MARK_AS_PROCESSED')"

// Или динамическое построение меню
"actions$": "getAvailableOperations($listRow.state)"
```

## Примеры операций

### MARK_AS_PROCESSED
```json
{
    "code": "MARK_AS_PROCESSED",
    "name_ru": "Отметить как обработанный",
    "icon": "check",
    "to_state": "PROCESSED",
    "availability_condition": {
        "available_in_states": ["LOADED"]
    }
}
```

### CANCEL_PROCESSING
```json
{
    "code": "CANCEL_PROCESSING", 
    "name_ru": "Отменить обработку",
    "icon": "undo",
    "cancel": true,
    "to_state": "LOADED",
    "availability_condition": {
        "available_in_states": ["PROCESSED"]
    }
}
```

### CREATE_PAYMENT
```json
{
    "code": "CREATE_PAYMENT",
    "name_ru": "Создать платеж",
    "icon": "payment",
    "to_state": "PAYMENT_CREATED",
    "resource_url": "declare p_dep_id int := 100; ...",  // PL/SQL код
    "availability_condition": {
        "available_in_states": ["LOADED"],
        "custom_check": "hasRequiredFields"
    }
}
```

## Интеграция с UI

### Отображение состояния в списке
```json
"STATE_CODE": {
    "title": "Состояние",
    "control": "chip",
    "decode": {
        "LOADED": {
            "value": "Загружен",
            "color": "#FF8C00"
        },
        "PROCESSED": {
            "value": "Обработан",
            "color": "#00AA44"
        }
    }
}
```

### Кнопка операций
```json
{
    "title": "Операции",
    "split": true,
    "actions": [
        {
            "title": "Отметить обработанным",
            "command": {
                "type": "js",
                "js": "executeOperation('MARK_AS_PROCESSED')"
            },
            "visible$": "$listRow.STATE_CODE === 'LOADED'"
        }
    ]
}
```

## Расширение системы

### Добавление нового типа процесса

1. Добавить запись в `process_type`:
```sql
INSERT INTO process_type (code, name_en, name_ru, name_combined)
VALUES ('pain.001', 'Customer Payment Initiation', 'Инициация платежа', 
        'Customer Payment Initiation (Инициация платежа)');
```

2. Создать состояния для типа:
```sql
INSERT INTO process_state (type_code, code, name_en, name_ru, color_code, start)
VALUES 
    ('pain.001', 'DRAFT', 'Draft', 'Черновик', '#CCCCCC', true),
    ('pain.001', 'SENT', 'Sent', 'Отправлен', '#0088CC', false);
```

3. Создать операции:
```sql
INSERT INTO process_operation (type_code, code, name_en, name_ru, to_state)
VALUES ('pain.001', 'SEND', 'Send', 'Отправить', 'SENT');
```

4. Связать операции с состояниями:
```sql
INSERT INTO process_operation_states (operation_id, state_id)
SELECT o.id, s.id 
FROM process_operation o, process_state s
WHERE o.code = 'SEND' AND s.code = 'DRAFT';
```

### Кастомная логика операций

В методах объекта можно реализовать специальную логику:

```python
def executeCustomOperation(parameters):
    operation = parameters.get('operation')
    
    if operation == 'VALIDATE_PAYMENT':
        # Проверка полей
        if not validate_payment_fields():
            raise UserException('Недостаточно данных для платежа')
    
    elif operation == 'GENERATE_RESPONSE':
        # Генерация ответного сообщения
        generate_pacs_002_response()
    
    # Смена состояния
    change_process_state(to_state)
```

## Рекомендации

1. **Атомарность операций** - операция должна либо полностью выполниться, либо откатиться
2. **Проверка прав** - проверяйте права пользователя на выполнение операций
3. **Логирование** - логируйте все изменения состояний
4. **Идемпотентность** - повторное выполнение операции не должно менять результат
5. **Валидация** - проверяйте возможность перехода перед выполнением
6. **Уведомления** - информируйте пользователя о результате операции
7. **Откат** - предусмотрите возможность отмены операций
8. **Параллельность** - учитывайте возможность одновременных операций

# Примеры типовых задач

Этот документ содержит пошаговые примеры выполнения типовых задач в системе SWIFT Processing.

## 1. Создание нового списка

### Задача
Добавить новый список "Архив сообщений" в объект swiftIncome для просмотра обработанных сообщений.

### Решение

1. Откройте файл `swift.objects/ao/swiftIncome.json`
2. В секцию `"lists"` добавьте новый список:

```json
"lists": {
    "default": {
        // существующий список
    },
    "archive": {
        "getList": "getArchiveList",
        "columns": {
            "imported": {
                "title": "Дата импорта",
                "width": 150,
                "format": "datetime"
            },
            "msg_type": {
                "title": "Тип",
                "width": 100
            },
            "msg_id": {
                "title": "ID сообщения",
                "flex": 1
            },
            "amount": {
                "title": "Сумма",
                "width": 150,
                "format": "currency",
                "cellStyle": {
                    "textAlign": "right"
                }
            },
            "state": {
                "title": "Состояние",
                "width": 120,
                "control": "chip",
                "decode": {
                    "processed": {
                        "value": "Обработан",
                        "color": "#00AA44"
                    },
                    "error": {
                        "value": "Ошибка",
                        "color": "#FF0000"
                    }
                }
            }
        },
        "id": "id",
        "actions": [
            {
                "title": "Обновить",
                "icon": "refresh",
                "mini": true,
                "command": {
                    "type": "standard",
                    "call": "refresh"
                }
            },
            {
                "title": "Просмотр",
                "icon": "visibility",
                "command": {
                    "type": "task",
                    "call": "/aoa/ObjectTask",
                    "params": {
                        "object": "swiftIncome",
                        "form": "viewArchived",
                        "objectKey$": "{id: $listRow.id}"
                    }
                },
                "disabled$": "!$listRow"
            }
        ],
        "filter": {
            "form": {
                "style": {"width": "360px"},
                "className": "panel vertical",
                "$": {
                    "@period": {
                        "className": "vertical",
                        "$": {
                            "dateFrom": {
                                "label": "С даты",
                                "control": "DateEdit"
                            },
                            "dateTo": {
                                "label": "По дату",
                                "control": "DateEdit"
                            }
                        }
                    },
                    "msg_type": {
                        "label": "Тип сообщения",
                        "control": "SelectEdit",
                        "controlProps": {
                            "object": "processType",
                            "valueField": "code",
                            "displayField": "name_combined"
                        }
                    }
                }
            },
            "query": {
                "dateFrom": {
                    "sql": "imported >= %(dateFrom)s"
                },
                "dateTo": {
                    "sql": "imported <= %(dateTo)s + interval '1 day'"
                },
                "msg_type": {
                    "sql": "msg_type = %(msg_type)s"
                }
            }
        }
    }
}
```

3. В секцию `"methods"` добавьте метод получения данных:

```json
"methods": {
    "getArchiveList": {
        "script": {
            "py": """
from apng_core.db import fetchall

SQL = '''
    SELECT 
        id,
        file_name,
        msg_type,
        msg_id,
        amount,
        currency_code,
        state,
        imported,
        cre_dt_tm
    FROM swift_input
    WHERE state IN ('processed', 'error')
    ORDER BY imported DESC
'''

# Применяем фильтры
request = parameters.get('request', {})
filterModel = request.get('filterModel2', {})
queryParams = {}

if filterModel:
    from apng_core.aoa.services import filter as aoa
    filterDef = aoa.buildFilterSql({
        'objectCode': 'swiftIncome',
        'filterData': filterModel.get('filterData', filterModel)
    })
    
    filter_sql = filterDef['sql'].replace('"', '')
    SQL = f'SELECT * FROM ({SQL}) t {filter_sql}'
    queryParams = filterDef['params']

# Пагинация
if request.get('startRow') is not None:
    startRow = int(request.get('startRow'))
    endRow = int(request.get('endRow'))
    SQL += f' OFFSET {startRow} ROWS FETCH NEXT {endRow - startRow + 1} ROWS ONLY'

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, queryParams)
    data = fetchall(c)
"""
        }
    }
}
```

4. Добавьте пункт меню в `workplace/swift.manager.xml`:

```xml
<menu name="Архив сообщений" call="/aoa/ObjectListTask">
    <p name="object" value="swiftIncome" />
    <p name="list" value="archive" />
</menu>
```

## 2. Создание новой формы редактирования

### Задача
Создать форму для редактирования настроек обработки SWIFT сообщений.

### Решение

В секцию `"forms"` объекта `swiftIncome.json` добавьте:

```json
"forms": {
    "settings": {
        "title": "Настройки обработки SWIFT",
        "className": "vertical",
        "style": {
            "width": "700px",
            "padding": "16px"
        },
        "$": {
            "@general": {
                "title": "Основные настройки",
                "className": "vertical",
                "$": {
                    "@folders": {
                        "className": "vertical",
                        "$": {
                            "folder_in": {
                                "label": "Папка входящих файлов",
                                "control": "TextEdit",
                                "required": true,
                                "placeholder": "/path/to/input",
                                "style": {"width": "100%"}
                            },
                            "folder_out": {
                                "label": "Папка исходящих файлов",
                                "control": "TextEdit",
                                "required": true,
                                "placeholder": "/path/to/output",
                                "style": {"width": "100%"}
                            },
                            "folder_unprocessed": {
                                "label": "Папка необработанных",
                                "control": "TextEdit",
                                "placeholder": "/path/to/unprocessed",
                                "style": {"width": "100%"}
                            }
                        }
                    },
                    "@processing": {
                        "title": "Параметры обработки",
                        "className": "horizontal",
                        "style": {"marginTop": "16px"},
                        "$": {
                            "auto_process": {
                                "label": "Автоматическая обработка",
                                "control": "Checkbox"
                            },
                            "process_interval": {
                                "label": "Интервал (сек)",
                                "control": "TextEdit",
                                "style": {"width": "100px", "marginLeft": "16px"},
                                "visible$": "mem.auto_process"
                            }
                        }
                    }
                }
            },
            "@advanced": {
                "title": "Дополнительные параметры",
                "className": "vertical",
                "style": {"marginTop": "16px"},
                "$": {
                    "llm_enabled": {
                        "label": "Использовать AI для парсинга адресов",
                        "control": "Checkbox"
                    },
                    "@llm_settings": {
                        "className": "vertical",
                        "visible$": "mem.llm_enabled",
                        "$": {
                            "llm_api_key": {
                                "label": "API ключ",
                                "control": "TextEdit",
                                "controlProps": {
                                    "type": "password"
                                },
                                "style": {"width": "100%"}
                            },
                            "llm_model": {
                                "label": "Модель",
                                "control": "SelectList",
                                "controlProps": {
                                    "list": [
                                        {"value": "llama3.1-8b", "name": "Llama 3.1 8B"},
                                        {"value": "gpt-3.5", "name": "GPT-3.5"},
                                        {"value": "gpt-4", "name": "GPT-4"}
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            "@buttons": {
                "className": "horizontal",
                "style": {
                    "justifyContent": "flex-end",
                    "marginTop": "24px"
                },
                "$": {
                    "btnCancel": {
                        "label": "Отмена",
                        "control": "Button",
                        "controlProps": {
                            "variant": "outlined"
                        },
                        "action": {
                            "js": "frontend.closeTask()"
                        }
                    },
                    "btnSave": {
                        "label": "Сохранить",
                        "control": "Button",
                        "controlProps": {
                            "variant": "contained",
                            "color": "primary"
                        },
                        "action": [
                            {
                                "js": "if (!validate()) throw 'Заполните обязательные поля'"
                            },
                            {
                                "js": "return backend.post('/aoa/execObjectMethod', {object: 'swiftIncome', method: 'saveSettings', params: mem})"
                            },
                            {
                                "js": "frontend.showMessage('Настройки сохранены')"
                            },
                            {
                                "js": "frontend.closeTask()"
                            }
                        ]
                    }
                }
            }
        },
        "actions": {
            "onTaskCreated": [
                {
                    "js": "backend.post('/aoa/execObjectMethod', {object: 'swiftIncome', method: 'getSettings'}).then(r => {Object.assign(mem, r); forceUpdate()})"
                }
            ]
        }
    }
}
```

## 3. Добавление новой операции в процесс

### Задача
Добавить операцию "Отправить уведомление" для типа сообщений pacs.008.

### Решение

1. Создайте операцию через UI или SQL:

```sql
-- Добавляем операцию
INSERT INTO process_operation (
    id, type_code, code, name_en, name_ru, name_combined,
    icon, resource_url, to_state
) VALUES (
    gen_random_uuid(),
    'pacs.008',
    'SEND_NOTIFICATION',
    'Send Notification',
    'Отправить уведомление',
    'Send Notification (Отправить уведомление)',
    'send',
    '/sendNotification',
    'PROCESSED'
);

-- Связываем с состоянием LOADED
INSERT INTO process_operation_states (operation_id, state_id)
SELECT o.id, s.id
FROM process_operation o, process_state s
WHERE o.code = 'SEND_NOTIFICATION' 
  AND s.type_code = 'pacs.008' 
  AND s.code = 'LOADED';
```

2. Добавьте метод в объект:

```json
"methods": {
    "sendNotification": {
        "script": {
            "py": """
from apng_core.db import fetchone
from apng_core.exceptions import UserException
import requests
import json

# Получаем данные сообщения
swift_id = parameters.get('swift_input_id')

SQL = '''
    SELECT 
        id, msg_id, amount, currency_code,
        snd_name, rcv_name
    FROM swift_input
    WHERE id = %(id)s
'''

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, {'id': swift_id})
    swift_data = fetchone(c)
    
if not swift_data:
    raise UserException('Сообщение не найдено')

# Формируем уведомление
notification = {
    'type': 'SWIFT_PAYMENT',
    'message_id': swift_data['msg_id'],
    'amount': float(swift_data['amount']),
    'currency': swift_data['currency_code'],
    'sender': swift_data['snd_name'],
    'receiver': swift_data['rcv_name']
}

# Отправляем уведомление (пример)
try:
    # response = requests.post('https://api.example.com/notify', json=notification)
    # if response.status_code != 200:
    #     raise Exception(f'API error: {response.status_code}')
    
    # Для примера просто логируем
    print(f"Notification sent: {json.dumps(notification)}")
    
    # Обновляем состояние
    SQL_UPDATE = '''
        UPDATE process 
        SET state_id = (
            SELECT id FROM process_state 
            WHERE type_code = 'pacs.008' AND code = 'PROCESSED'
        )
        WHERE swift_input_id = %(swift_id)s
    '''
    c.execute(SQL_UPDATE, {'swift_id': swift_id})
    
    data = {'success': True, 'message': 'Уведомление отправлено'}
    
except Exception as e:
    raise UserException({
        'message': 'Ошибка отправки уведомления',
        'description': str(e)
    })
"""
        }
    }
}
```

3. Добавьте кнопку операции в список:

```json
"actions": [
    {
        "title": "Операции",
        "split": true,
        "actions": [
            {
                "title": "Отправить уведомление",
                "icon": "send",
                "command": {
                    "type": "js",
                    "js": "backend.post('/aoa/execObjectMethod', {object: 'swiftIncome', method: 'sendNotification', params: {swift_input_id: $listRow.id}}).then(() => forceRefreshList())"
                },
                "visible$": "$listRow.msg_type === 'pacs.008' && $listRow.state === 'new'",
                "confirm": {
                    "message": "Отправить уведомление о платеже?",
                    "yes": "Да",
                    "no": "Отмена"
                }
            }
        ]
    }
]
```

## 4. Создание нового справочника

### Задача
Создать справочник банков-корреспондентов.

### Решение

1. Создайте таблицу в БД:

```sql
CREATE TABLE correspondent_banks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bic VARCHAR(11) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL,
    city VARCHAR(100),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_correspondent_banks_bic ON correspondent_banks(bic);
CREATE INDEX idx_correspondent_banks_country ON correspondent_banks(country);
```

2. Создайте новый объект `correspondentBanks.json`:

```json
{
    "lists": {
        "default": {
            "getList": "getBanksList",
            "columns": {
                "bic": {
                    "title": "BIC",
                    "width": 120
                },
                "name": {
                    "title": "Название",
                    "flex": 1
                },
                "country": {
                    "title": "Страна",
                    "width": 80
                },
                "city": {
                    "title": "Город",
                    "width": 150
                },
                "active": {
                    "title": "Активен",
                    "width": 80,
                    "control": "checkbox",
                    "readonly": true
                }
            },
            "id": "id",
            "actions": [
                {
                    "title": "Добавить",
                    "icon": "add",
                    "command": {
                        "type": "task",
                        "call": "/aoa/ObjectTask",
                        "params": {
                            "object": "correspondentBanks",
                            "form": "editBank",
                            "objectKey": null
                        }
                    }
                }
            ]
        }
    },
    "forms": {
        "editBank": {
            "title$": "mem.id ? `Редактирование: ${mem.name}` : 'Новый банк'",
            "className": "vertical",
            "style": {"width": "600px", "padding": "16px"},
            "$": {
                "@fields": {
                    "className": "vertical",
                    "$": {
                        "bic": {
                            "label": "BIC код",
                            "control": "TextEdit",
                            "required": true,
                            "placeholder": "AAAABBCCDDD",
                            "style": {"width": "200px"}
                        },
                        "name": {
                            "label": "Название банка",
                            "control": "TextEdit",
                            "required": true,
                            "style": {"width": "100%"}
                        },
                        "@location": {
                            "className": "horizontal",
                            "$": {
                                "country": {
                                    "label": "Страна (ISO)",
                                    "control": "TextEdit",
                                    "required": true,
                                    "placeholder": "UZ",
                                    "style": {"width": "100px"}
                                },
                                "city": {
                                    "label": "Город",
                                    "control": "TextEdit",
                                    "style": {"flex": 1, "marginLeft": "16px"}
                                }
                            }
                        },
                        "active": {
                            "label": "Активен",
                            "control": "Checkbox"
                        }
                    }
                },
                "@buttons": {
                    "className": "horizontal",
                    "style": {"justifyContent": "flex-end", "marginTop": "16px"},
                    "$": {
                        "btnCancel": {
                            "label": "Отмена",
                            "control": "Button",
                            "controlProps": {"variant": "outlined"},
                            "action": {"js": "frontend.closeTask()"}
                        },
                        "btnSave": {
                            "label": "Сохранить",
                            "control": "Button",
                            "controlProps": {
                                "variant": "contained",
                                "color": "primary"
                            },
                            "action": [
                                {"js": "if (!validate()) throw 'Validation failed'"},
                                {"js": "return backend.post('/aoa/execObjectMethod', {object: 'correspondentBanks', method: 'saveBank', params: mem})"},
                                {"js": "frontend.closeTask()"}
                            ]
                        }
                    }
                }
            }
        }
    },
    "methods": {
        "getBanksList": {
            "sql": {
                "sqlType": "query",
                "database": "default",
                "sql": "SELECT * FROM correspondent_banks ORDER BY name"
            }
        },
        "saveBank": {
            "script": {
                "py": """
SQL = '''
    INSERT INTO correspondent_banks (bic, name, country, city, active)
    VALUES (%(bic)s, %(name)s, %(country)s, %(city)s, %(active)s)
    ON CONFLICT (bic) DO UPDATE SET
        name = EXCLUDED.name,
        country = EXCLUDED.country,
        city = EXCLUDED.city,
        active = EXCLUDED.active
    RETURNING id
'''

parameters['active'] = parameters.get('active', True)

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, parameters)
    data = fetchone(c)
"""
            }
        }
    },
    "references": {
        "default": {
            "form": {
                "style": {"width": "800px", "height": "500px"},
                "columns": [
                    {"title": "BIC", "field": "bic", "width": 120},
                    {"title": "Название", "field": "name", "flex": 1},
                    {"title": "Страна", "field": "country", "width": 80}
                ],
                "keyField": "bic",
                "titleField": "name",
                "method": "getBanksList"
            }
        }
    }
}
```

3. Добавьте объект в `.package.info` и зарегистрируйте в системе.

## 5. Добавление валидации и бизнес-логики

### Задача
Добавить проверку корректности IBAN при сохранении платежа.

### Решение

```python
"methods": {
    "validateAndSave": {
        "script": {
            "py": """
import re
from apng_core.exceptions import UserException

def validate_iban(iban):
    '''Проверка корректности IBAN'''
    if not iban:
        return False
    
    # Убираем пробелы
    iban = iban.replace(' ', '').upper()
    
    # Проверяем длину для разных стран
    iban_lengths = {
        'UZ': 20, 'RU': 33, 'KZ': 20,
        'DE': 22, 'FR': 27, 'GB': 22
    }
    
    country = iban[:2]
    expected_length = iban_lengths.get(country)
    
    if not expected_length or len(iban) != expected_length:
        return False
    
    # Переставляем первые 4 символа в конец
    iban_rearranged = iban[4:] + iban[:4]
    
    # Заменяем буквы на числа (A=10, B=11, ..., Z=35)
    iban_numeric = ''
    for char in iban_rearranged:
        if char.isdigit():
            iban_numeric += char
        else:
            iban_numeric += str(ord(char) - ord('A') + 10)
    
    # Проверяем контрольную сумму
    return int(iban_numeric) % 97 == 1

# Валидация данных
rcv_acc = parameters.get('rcv_acc', '')
snd_acc = parameters.get('snd_acc', '')

errors = []

# Проверяем счета получателя и отправителя
if rcv_acc and len(rcv_acc) > 15:
    if not validate_iban(rcv_acc):
        errors.append('Некорректный IBAN получателя')

if snd_acc and len(snd_acc) > 15:
    if not validate_iban(snd_acc):
        errors.append('Некорректный IBAN отправителя')

# Проверяем сумму
amount = parameters.get('amount', 0)
if amount <= 0:
    errors.append('Сумма должна быть больше нуля')

# Проверяем обязательные поля
if not parameters.get('rcv_name'):
    errors.append('Не указано имя получателя')

if not parameters.get('snd_name'):
    errors.append('Не указано имя отправителя')

# Если есть ошибки - выбрасываем исключение
if errors:
    raise UserException({
        'message': 'Ошибки валидации',
        'description': '\\n'.join(errors)
    })

# Если все ок - сохраняем
SQL = '''
    INSERT INTO swift_payment_draft (
        rcv_acc, rcv_name, snd_acc, snd_name, amount, currency
    ) VALUES (
        %(rcv_acc)s, %(rcv_name)s, %(snd_acc)s, %(snd_name)s, 
        %(amount)s, %(currency)s
    ) RETURNING id
'''

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, parameters)
    result = fetchone(c)
    data = {'id': result['id'], 'success': True}
"""
        }
    }
}
```

## Общие рекомендации

1. **Следуйте существующим паттернам** - изучите похожие элементы перед созданием новых
2. **Тестируйте изменения** - проверяйте работу после каждого изменения
3. **Документируйте** - добавляйте комментарии к сложной логике
4. **Версионируйте** - используйте git для отслеживания изменений
5. **Валидируйте данные** - всегда проверяйте входные данные
6. **Обрабатывайте ошибки** - предусматривайте обработку исключений
7. **Оптимизируйте запросы** - используйте индексы и ограничивайте выборки
8. **Соблюдайте безопасность** - используйте параметризованные запросы

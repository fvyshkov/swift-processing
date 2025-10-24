# Практические паттерны SWIFT Processing

Этот документ содержит реальные паттерны из существующих объектов системы.

## Типы контролов (из анализа системы)

### Текстовые контролы
- `TextEdit` - базовое текстовое поле
- `TextArea` - многострочный текст
- `AceEditor` - редактор кода с подсветкой синтаксиса

### Контролы выбора
- `SelectEdit` - выпадающий список с поиском
- `SelectList` - простой выпадающий список
- `Checkbox` - флажок
- `ObjectReference` - ссылка на объект системы

### Числовые и даты
- `CurrencyField` - поле для денежных сумм
- `DateEdit` - выбор даты

### Контролы отображения
- `Chip` - чип для статусов (в колонках таблиц)
- `ListTable` - встроенная таблица
- `ActionPanel` - панель с действиями

### Кнопки
- `Button` - обычная кнопка
- `IconButton` - кнопка с иконкой

## Python скрипты в JSON

### Правильный формат (одна строка с \n)

```json
"script": {
    "py": "from apng_core.db import fetchall\nfrom apng_core.aoa.services import filter as aoa\n\nSQL = '''\n    SELECT id, type_code, code, name_en, name_ru\n    FROM process_state\n    WHERE type_code = %(type_code)s\n'''\n\nwith initDbSession(database='default').cursor() as c:\n    c.execute(SQL, parameters)\n    data = fetchall(c)\n"
}
```

### Типичные импорты

```python
from apng_core.db import fetchall, fetchone, initDbSession
from apng_core.exceptions import UserException
from apng_core.auth import getUser
from apng_core.aoa.services import filter as aoa
import logging
import json
import uuid
from datetime import datetime
from decimal import Decimal
```

## Паттерны списков (lists)

### Базовый список с фильтром

```json
"default": {
    "getList": "getList",
    "columns": {
        "imported": {
            "title": "Дата",
            "width": 170,
            "fields": {
                "imported": {
                    "format": "datetimesec"
                }
            }
        },
        "state": {
            "title": "Состояние",
            "control": "chip",
            "decode": {
                "new": {
                    "value": "Новый",
                    "color": "#2196F3"
                },
                "processed": {
                    "value": "Обработан",
                    "color": "#4CAF50"
                }
            }
        }
    },
    "id": "id",
    "actions": [
        {
            "title": "Refresh",
            "icon": "refresh",
            "mini": true,
            "command": {
                "type": "standard",
                "call": "refresh"
            }
        }
    ]
}
```

### Список с цветными строками

```json
"stateList": {
    "getList": "getStateList",
    "getRowStyle": "{background: data?.color_code}",
    "columns": {
        // ...
    }
}
```

## Паттерны форм (forms)

### Стандартная форма редактирования

```json
"editForm": {
    "title": "Редактирование",
    "className": "vertical",
    "style": {
        "width": "800px",
        "padding": "16px"
    },
    "$": {
        "@fields": {
            "className": "vertical",
            "$": {
                // Поля формы
            }
        },
        "@buttons": {
            "className": "horizontal",
            "style": {
                "justifyContent": "flex-end",
                "marginTop": "16px"
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
                        {"js": "if (!validate()) throw 'Validation failed'"},
                        {"js": "return backend.post('/aoa/execObjectMethod', {object: 'objectName', method: 'save', params: mem})"},
                        {"js": "frontend.closeTask()"}
                    ]
                }
            }
        }
    }
}
```

### Форма с вложенными секциями

```json
"$": {
    "@mainInfo": {
        "title": "Основная информация",
        "className": "vertical",
        "$": {
            "@row1": {
                "className": "horizontal",
                "$": {
                    "field1": {
                        "label": "Поле 1",
                        "control": "TextEdit",
                        "style": {"width": "300px"}
                    },
                    "field2": {
                        "label": "Поле 2",
                        "control": "DateEdit",
                        "style": {"width": "200px", "marginLeft": "16px"}
                    }
                }
            }
        }
    }
}
```

## Паттерны действий (actions)

### Загрузка данных при открытии формы

```json
"onTaskCreated": [
    {
        "js": "if (task.params?.objectKey) { return backend.post('/aoa/execObjectMethod', {object: 'objectName', method: 'get', params: task.params.objectKey}).then((r) => { Object.assign(mem, r); forceUpdate(); }); }"
    }
]
```

### Обработчик изменения поля

```json
"onChange": [
    {
        "js": "const copy = { ...params.row }; mem.field1 = copy.value1; mem.field2 = copy.value2; forceUpdate();"
    }
]
```

### Динамические действия в списке

```json
{
    "title": "Операции",
    "split": true,
    "actions$": "context.operations?.map(op => ({title: op.name, command: {type: 'js', js: `executeOperation('${op.code}')`}}))",
    "disabled$": "!$listRow"
}
```

## Паттерны фильтров

### Фильтр с периодом дат

```json
"filter": {
    "form": {
        "style": {"width": "360px"},
        "className": "panel vertical",
        "$": {
            "@period": {
                "$": {
                    "@chips": {
                        "$": {
                            "week": {
                                "label": "Неделя",
                                "control": "Chip",
                                "action": {
                                    "name": "setWeek"
                                }
                            }
                        }
                    },
                    "@dates": {
                        "className": "horizontal",
                        "$": {
                            "fromDate": {
                                "label": "С",
                                "control": "DateEdit"
                            },
                            "toDate": {
                                "label": "По",
                                "control": "DateEdit"
                            }
                        }
                    }
                }
            }
        }
    },
    "query": {
        "fromDate": {
            "sql": "imported >= %(fromDate)s"
        },
        "toDate": {
            "sql": "imported <= %(toDate)s + interval '1 day'"
        }
    }
}
```

## ObjectReference паттерны

### Базовое использование

```json
"bank_account": {
    "label": "Счет",
    "control": "ObjectReference",
    "controlProps": {
        "object": "swiftBankAccount"
    },
    "actions": {
        "onChange": [
            {
                "js": "const row = params.row; mem.bank = row.BANK; mem.currency = row.VAL_CODE;"
            }
        ]
    }
}
```

### С дополнительными параметрами справочника

```json
"type_code": {
    "label": "Тип",
    "control": "ObjectReference",
    "controlProps": {
        "object": "processType",
        "reference": "default"
    },
    "required": true
}
```

## Встроенные таблицы (ListTable)

```json
"|operList": {
    "control": "ListTable",
    "controlOpts": {
        "columns!": {
            "name": {
                "label": "Операция",
                "flex": 1
            },
            "icon": {
                "label": "Иконка",
                "width": 100
            }
        }
    },
    "controlProps": {
        "gridOptions": {
            "headerHeight": 40
        }
    }
}
```

## Условная видимость и доступность

### Примеры из системы

```json
// Поле видно только если включен флажок
"visible$": "mem.llm_enabled"

// Кнопка отключена если нет выбранной строки
"disabled$": "!$listRow"

// Readonly если есть ID (редактирование)
"readOnly$": "!!mem.id"

// Сложное условие видимости
"visible$": "$listRow.STATE_CODE === 'LOADED' && !$listRow.locked"

// Динамический заголовок
"title$": "`Редактирование: ${mem.name}`"
```

## Паттерны методов

### Метод с фильтрацией

```python
SQL = '''SELECT * FROM table WHERE 1=1'''
params = {}

if parameters.get('filter_field'):
    SQL += ' AND field = %(filter_field)s'
    params['filter_field'] = parameters['filter_field']

# Применение фильтра из UI
if parameters.get('request'):
    filterModel = parameters['request'].get('filterModel2', {})
    if filterModel:
        from apng_core.aoa.services import filter as aoa
        filterDef = aoa.buildFilterSql({
            'objectCode': 'objectName',
            'filterData': filterModel
        })
        SQL = f'SELECT * FROM ({SQL}) t {filterDef["sql"]}'
        params.update(filterDef['params'])
```

### Сохранение с конфликтом

```python
SQL = '''
    INSERT INTO table (id, field1, field2)
    VALUES (%(id)s, %(field1)s, %(field2)s)
    ON CONFLICT (id) DO UPDATE SET
        field1 = EXCLUDED.field1,
        field2 = EXCLUDED.field2,
        modified = now()
    RETURNING id
'''
```

## Часто используемые иконки

- `refresh` - обновить
- `add` - добавить
- `edit` - редактировать
- `delete` - удалить
- `check` - галочка
- `undo` - отменить
- `send` - отправить
- `visibility` - просмотр
- `payment` - платеж
- `save` - сохранить

## Важные замечания

1. **Префикс `!` в columns** означает переопределение колонок
2. **Суффикс `$`** всегда означает динамическое выражение
3. **backend.post** всегда возвращает Promise - используйте .then()
4. **forceUpdate()** нужен после изменения mem для обновления UI
5. **validate()** проверяет все required поля формы

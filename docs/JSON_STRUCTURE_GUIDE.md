# Руководство по структуре JSON объектов

## Общая структура JSON объекта

Каждый файл в папке `ao/` представляет собой прикладной объект со стандартной структурой:

```json
{
    "lists": {},      // Табличные представления данных
    "forms": {},      // Формы редактирования и диалоги
    "methods": {},    // Серверные методы обработки данных
    "references": {}, // Справочники для выбора значений
    "js": {},        // JavaScript функции и вспомогательный код
    "actions": {},    // Глобальные действия объекта
    "filter": {}      // Глобальные фильтры объекта
}
```

## 1. Lists (Списки)

### Структура списка

```json
"lists": {
    "default": {
        // Определение колонок
        "columns": {
            "column_name": {
                "title": "Заголовок колонки",
                "width": 120,              // Фиксированная ширина
                "flex": 1,                  // Или гибкая ширина
                "control": "chip",          // Специальный контрол для отображения
                "format": "date",           // Форматирование значения
                "fields": {                 // Составные поля
                    "field1": {},
                    "field2": {}
                },
                "cellStyle": {              // Стили ячейки
                    "textAlign": "right"
                },
                "decode": {                 // Декодирование значений
                    "VALUE": {
                        "value": "Отображаемый текст",
                        "color": "#FF0000"
                    }
                }
            }
        },
        
        "id": "ID",                        // Ключевое поле
        "getList": "methodName",           // Метод получения данных
        "getRowStyle": "{background: data?.color_code}", // Динамические стили строк
        
        // Действия над списком
        "actions": [
            {
                "title": "Refresh",
                "icon": "refresh",
                "mini": true,
                "command": {
                    "type": "standard",
                    "call": "refresh"
                }
            },
            {
                "title": "Add",
                "icon": "add", 
                "command": {
                    "type": "task",
                    "call": "/aoa/ObjectTask",
                    "params": {
                        "object": "objectName",
                        "form": "formName",
                        "objectKey": null
                    }
                }
            },
            {
                "title": "Edit",
                "icon": "edit",
                "command": {
                    "type": "task",
                    "call": "/aoa/ObjectTask",
                    "title$": "`Edit: ${$listRow.name}`",  // Динамический заголовок
                    "params": {
                        "object": "objectName",
                        "form": "formName",
                        "objectKey$": "{id: $listRow.id}"  // Динамические параметры
                    }
                },
                "disabled$": "!$listRow"           // Условное отключение
            },
            {
                "title": "Operations",
                "split": true,                     // Кнопка с подменю
                "actions": [
                    {
                        "title": "Sub action",
                        "command": {},
                        "visible$": "condition"    // Условная видимость
                    }
                ],
                "confirm": {                       // Подтверждение действия
                    "message$": "`Delete ${$listRow.name}?`",
                    "yes": "Yes",
                    "no": "No"
                }
            }
        ],
        
        // Фильтрация
        "filter": {
            "form": {
                "style": {
                    "width": "360px"
                },
                "title": "Filter",
                "className": "panel vertical",
                "$": {
                    "field_name": {
                        "label": "Label",
                        "control": "TextEdit"
                    }
                }
            },
            "query": {
                "field_name": {
                    "sql": "column_name = :field_name"
                }
            }
        },
        
        // События
        "events": {
            "onTaskCreated": [
                {
                    "js": "JavaScript code"
                }
            ],
            "onRowDoubleClicked": {
                "js": "JavaScript code"
            }
        }
    }
}
```

### Типы команд (command)

1. **standard** - стандартные команды
   ```json
   {
       "type": "standard",
       "call": "refresh"    // refresh, close, etc.
   }
   ```

2. **task** - открытие задачи
   ```json
   {
       "type": "task",
       "call": "/aoa/ObjectTask",
       "title": "Task Title",
       "params": {
           "object": "objectName",
           "form": "formName",
           "objectKey": {id: 123}
       }
   }
   ```

3. **js** - выполнение JavaScript
   ```json
   {
       "type": "js",
       "js": "backend.post('/aoa/execObjectMethod', {...})"
   }
   ```

## 2. Forms (Формы)

### Структура формы

```json
"forms": {
    "editForm": {
        "title": "Form Title",
        "title$": "`Dynamic ${mem.value}`",    // Динамический заголовок
        "className": "vertical",                // vertical, horizontal
        "style": {
            "width": "800px",
            "padding": "16px"
        },
        
        // Элементы формы
        "$": {
            // Простое поле
            "field_name": {
                "label": "Field Label",
                "control": "TextEdit",
                "required": true,
                "readOnly$": "!!mem.id",        // Динамический readonly
                "visible$": "condition",         // Динамическая видимость
                "placeholder": "Enter value",
                "style": {
                    "width": "300px"
                },
                "actions": {
                    "onChange": [
                        {
                            "js": "mem.otherField = params.value"
                        }
                    ]
                }
            },
            
            // Группировка полей
            "@section": {
                "title": "Section Title",
                "className": "vertical",
                "style": {},
                "$": {
                    // Вложенные поля
                }
            },
            
            // Горизонтальная группа
            "@row": {
                "className": "horizontal",
                "$": {
                    "field1": {},
                    "field2": {}
                }
            },
            
            // Вложенная форма
            "@inner-form": {
                "form": "innerFormName",
                "style": {}
            },
            
            // Список внутри формы
            "|listField": {
                "control": "ListTable",
                "controlOpts": {
                    "columns!": {
                        "name": {
                            "label": "Name",
                            "flex": 1
                        }
                    }
                }
            },
            
            // Кнопки
            "@buttons": {
                "className": "horizontal",
                "style": {
                    "justifyContent": "flex-end"
                },
                "$": {
                    "btnCancel": {
                        "label": "Cancel",
                        "control": "Button",
                        "controlProps": {
                            "variant": "outlined"
                        },
                        "action": {
                            "js": "frontend.closeTask()"
                        }
                    },
                    "btnSave": {
                        "label": "Save",
                        "control": "Button",
                        "controlProps": {
                            "variant": "contained",
                            "color": "primary"
                        },
                        "action": [
                            {
                                "js": "if (!validate()) throw 'Validation failed'"
                            },
                            {
                                "js": "return backend.post(...)"
                            },
                            {
                                "js": "frontend.closeTask()"
                            }
                        ]
                    }
                }
            }
        },
        
        // Действия формы
        "actions": {
            "onTaskCreated": [
                {
                    "js": "// Load data when form opens"
                }
            ],
            "customAction": {
                "js": "// Custom action code"
            }
        }
    }
}
```

### Типы контролов

1. **Текстовые поля**
   - `TextEdit` - однострочное текстовое поле
   - `TextArea` - многострочное текстовое поле
   ```json
   {
       "control": "TextEdit",
       "controlProps": {
           "multiline": true,
           "minRows": 3
       }
   }
   ```

2. **Числовые поля**
   - `CurrencyField` - поле для ввода денежных сумм
   ```json
   {
       "control": "CurrencyField",
       "controlOpts": {
           "currencyAttr": "currency_code"
       }
   }
   ```

3. **Даты**
   - `DateEdit` - выбор даты
   ```json
   {
       "control": "DateEdit"
   }
   ```

4. **Выбор значений**
   - `SelectEdit` - выпадающий список с возможностью поиска
   - `SelectList` - простой выпадающий список
   - `Checkbox` - флажок
   - `ObjectReference` - ссылка на объект системы
   ```json
   {
       "control": "ObjectReference",
       "controlProps": {
           "object": "objectName",
           "reference": "default"
       }
   }
   ```

5. **Специальные**
   - `ListTable` - таблица
   - `AceEditor` - редактор кода
   - `Chip` - чип для отображения статусов
   - `Button` - кнопка
   - `ActionPanel` - панель действий

### Префиксы элементов формы

- Без префикса - обычное поле: `"fieldName": {}`
- `@` - группа элементов: `"@section": {}`
- `|` - список/таблица: `"|items": {}`
- `.` - системные элементы: `".btnSave": {}`

## 3. Methods (Методы)

### SQL методы

```json
"methods": {
    "getList": {
        "sql": {
            "sqlType": "query",      // query, script
            "database": "default",   // default (PostgreSQL), colvir_cbs (Oracle)
            "sql": "SELECT * FROM table WHERE condition = :param",
            "params": ["param"]
        }
    }
}
```

### Python методы

```json
"methods": {
    "saveData": {
        "script": {
            "py": """
from apng_core.db import fetchall, fetchone
from apng_core.exceptions import UserException

# Доступные переменные:
# - parameters: входные параметры
# - initDbSession: создание сессии БД

SQL = '''
    INSERT INTO table (field1, field2)
    VALUES (%(field1)s, %(field2)s)
    RETURNING id
'''

with initDbSession(database='default').cursor() as c:
    c.execute(SQL, parameters)
    data = fetchone(c)
    
# data - результат выполнения метода
"""
        }
    }
}
```

### Комбинированные методы

```json
"methods": {
    "complexMethod": {
        "sql": {},      // SQL часть
        "script": {}    // Python часть
    }
}
```

## 4. References (Справочники)

```json
"references": {
    "default": {
        "form": {
            "style": {
                "width": "1000px",
                "height": "600px"
            },
            "columns": [
                {
                    "title": "Code",
                    "field": "code",
                    "width": 200
                }
            ],
            "primaryKey": "id",
            "titleField": "name",
            "valueField": "code",
            "displayField": "name",
            "fastFilter": true,
            "filter": {
                // Структура фильтра как в lists
            }
        },
        "method": {
            // Метод получения данных
        }
    }
}
```

## 5. JavaScript контекст

В JavaScript коде доступны следующие объекты:

### Frontend объекты:
- `mem` - память формы (хранит данные)
- `context` - контекст выполнения
- `$listRow` - текущая строка списка
- `task` - текущая задача
- `dialog` - текущий диалог
- `params` - параметры вызова
- `forceUpdate()` - принудительное обновление UI

### Backend вызовы:
```javascript
// Вызов метода объекта
backend.post('/aoa/execObjectMethod', {
    object: 'objectName',
    method: 'methodName',
    params: {param1: value1}
}).then((result) => {
    // Обработка результата
});
```

### Frontend функции:
```javascript
// Открыть задачу
frontend.newTask({
    path: '/aoa/ObjectTask',
    title: 'Task Title',
    params: {
        object: 'objectName',
        form: 'formName',
        objectKey: {id: 123}
    }
});

// Закрыть текущую задачу
frontend.closeTask();

// Открыть диалог
frontend.dialog({
    object: 'objectName',
    form: 'dialogForm',
    mem: {data: value}
});
```

### Task Manager (tm):
```javascript
// Установить заголовок задачи
tm.setTaskTitle(task.key, 'New Title');

// Получить активную задачу
tm.getActiveTask();
```

### Валидация:
```javascript
// Проверить валидность формы
if (!validate()) {
    throw 'Validation failed';
}
```

## Динамические выражения

Поля с суффиксом `$` поддерживают динамические выражения:

```json
{
    "readOnly$": "!!mem.id",                    // Boolean выражение
    "visible$": "mem.type === 'special'",       // Условие видимости
    "disabled$": "!$listRow || $listRow.locked", // Сложное условие
    "title$": "`Item: ${mem.name}`",            // Template string
    "objectKey$": "{id: $listRow.id}"           // Объект
}
```

## Важные паттерны

1. **Загрузка данных при открытии формы:**
   ```json
   "onTaskCreated": [
       {
           "js": "if (task.params?.objectKey) { /* load data */ }"
       }
   ]
   ```

2. **Сохранение с валидацией:**
   ```json
   "action": [
       {"js": "if (!validate()) throw 'Validation failed'"},
       {"js": "return backend.post(...)"},
       {"js": "frontend.closeTask()"}
   ]
   ```

3. **Обновление связанных полей:**
   ```json
   "onChange": [
       {
           "js": "const row = params.row; mem.field1 = row.value1; mem.field2 = row.value2;"
       }
   ]
   ```

4. **Фильтрация списков:**
   ```json
   "query": {
       "fieldName": {
           "sql": "UPPER(column) LIKE '%' || UPPER(:fieldName) || '%'"
       }
   }
   ```

## Рекомендации

1. Всегда следуйте существующим паттернам
2. Используйте префиксы элементов правильно
3. Не изменяйте названия стандартных полей
4. Проверяйте типы БД в методах
5. Используйте транзакции для изменения данных
6. Добавляйте обработку ошибок в Python скриптах
7. Документируйте сложную логику комментариями

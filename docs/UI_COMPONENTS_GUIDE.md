# Руководство по UI компонентам

## Общие принципы построения UI

Пользовательский интерфейс в системе SWIFT Processing строится декларативно через JSON конфигурации. Каждый элемент описывается объектом с параметрами.

## Основные компоненты

### 1. Контролы ввода данных

#### TextEdit - Текстовое поле
```json
{
    "label": "Название поля",
    "control": "TextEdit",
    "required": true,
    "placeholder": "Введите значение",
    "readOnly$": "!!mem.id",              // Динамическое условие
    "style": {
        "width": "300px"
    },
    "controlProps": {
        "multiline": true,                 // Многострочное поле
        "minRows": 3,                      // Минимум строк
        "maxLength": 255                   // Максимальная длина
    }
}
```

#### TextArea - Многострочный текст
```json
{
    "label": "Описание",
    "control": "TextArea", 
    "controlProps": {
        "rows": 5                          // Количество строк
    }
}
```

#### DateEdit - Выбор даты
```json
{
    "label": "Дата платежа",
    "control": "DateEdit",
    "required": true,
    "actions": {
        "onChange": [
            {
                "js": "mem.dateFormatted = params.value?.toISOString().substring(0,10)"
            }
        ]
    }
}
```

#### CurrencyField - Денежная сумма
```json
{
    "label": "Сумма",
    "control": "CurrencyField",
    "controlOpts": {
        "currencyAttr": "currency_code"    // Поле с кодом валюты
    },
    "style": {
        "width": "200px"
    }
}
```

#### Checkbox - Флажок
```json
{
    "label": "Разрешить редактирование",
    "control": "Checkbox",
    "actions": {
        "onChange": [
            {
                "js": "mem.readOnlyMode = !params.value"
            }
        ]
    }
}
```

### 2. Контролы выбора

#### SelectEdit - Выпадающий список с поиском
```json
{
    "label": "Тип документа",
    "control": "SelectEdit",
    "required": true,
    "controlProps": {
        "object": "processType",           // Объект-источник
        "method": "getItemList",           // Метод получения данных
        "valueField": "code",              // Поле значения
        "displayField": "name_combined"    // Поле отображения
    }
}
```

#### SelectList - Простой выпадающий список
```json
{
    "label": "Валюта",
    "control": "SelectList",
    "controlProps": {
        "list": [
            {"name": "UZS", "value": "UZS"},
            {"name": "USD", "value": "USD"},
            {"name": "EUR", "value": "EUR"}
        ]
    }
}
```

#### ObjectReference - Ссылка на объект
```json
{
    "label": "Корреспондентский счет",
    "control": "ObjectReference",
    "controlProps": {
        "object": "swiftBankAccount",
        "reference": "default"             // Имя справочника
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

### 3. Контролы отображения

#### Chip - Чип для статусов
```json
{
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

#### AceEditor - Редактор кода
```json
{
    "style": {
        "height": "400px",
        "width": "100%"
    },
    "control": "AceEditor",
    "controlProps": {
        "editorId": "xmlEditor",
        "mode": "xml"                      // xml, json, python, sql
    }
}
```

### 4. Контролы действий

#### Button - Кнопка
```json
{
    "label": "Сохранить",
    "control": "Button",
    "controlProps": {
        "variant": "contained",            // contained, outlined, text
        "color": "primary",                // primary, secondary, error
        "size": "medium"                   // small, medium, large
    },
    "action": {
        "js": "backend.post(...)"
    },
    "disabled$": "!validate()"            // Условное отключение
}
```

#### ActionPanel - Панель действий
```json
{
    "control": "ActionPanel",
    "controlOpts": {
        "actions": [
            {
                "title": "Добавить",
                "icon": "add",
                "split": true,             // Кнопка с подменю
                "actions$": "context.availableActions"  // Динамические действия
            }
        ]
    }
}
```

### 5. Контейнеры и группировка

#### ListTable - Таблица
```json
{
    "control": "ListTable",
    "controlOpts": {
        "columns!": {                      // ! означает переопределение
            "name": {
                "label": "Название",
                "flex": 1
            },
            "amount": {
                "label": "Сумма",
                "width": 120,
                "format": "currency"
            }
        }
    },
    "controlProps": {
        "gridOptions": {
            "headerHeight": 40,
            "rowHeight": 35
        }
    },
    "actions": {
        "onRowDoubleClicked": {
            "js": "// открыть детали"
        }
    }
}
```

## Компоновка элементов

### Вертикальная группировка
```json
"@section": {
    "title": "Информация о платеже",
    "className": "vertical",
    "style": {
        "padding": "8px",
        "marginTop": "16px"
    },
    "$": {
        "field1": {},
        "field2": {}
    }
}
```

### Горизонтальная группировка
```json
"@row": {
    "className": "horizontal",
    "style": {
        "gap": "8px"
    },
    "$": {
        "dateFrom": {
            "label": "С",
            "control": "DateEdit",
            "style": {"flexGrow": 1}
        },
        "dateTo": {
            "label": "По",
            "control": "DateEdit", 
            "style": {"flexGrow": 1}
        }
    }
}
```

### Вложенные формы
```json
"@details": {
    "form": "innerFormName",
    "style": {
        "border": "1px solid #ccc",
        "padding": "8px"
    }
}
```

## Динамические свойства

Свойства с суффиксом `$` вычисляются динамически:

```json
{
    // Условная видимость
    "visible$": "mem.showAdvanced === true",
    
    // Условное отключение
    "disabled$": "!$listRow || mem.readOnly",
    
    // Динамический заголовок
    "title$": "`Платеж №${mem.paymentNumber}`",
    
    // Динамические стили
    "style$": "{color: mem.isError ? 'red' : 'black'}",
    
    // Динамическое значение
    "value$": "mem.amount * mem.rate"
}
```

## Обработка событий

### onChange - Изменение значения
```json
{
    "actions": {
        "onChange": [
            {
                "js": "console.log('New value:', params.value)"
            },
            {
                "js": "mem.calculated = params.value * 1.2"
            }
        ]
    }
}
```

### onClick - Клик по элементу
```json
{
    "action": {
        "js": "frontend.dialog({...})"
    }
}
```

### onRowDoubleClicked - Двойной клик по строке
```json
{
    "onRowDoubleClicked": {
        "js": "tm.newTask({object: 'swift', form: 'edit', objectKey: {id: params.selectedRow.id}})"
    }
}
```

## Стандартные паттерны UI

### 1. Форма редактирования с кнопками
```json
{
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
                        {"js": "return backend.post(...)"},
                        {"js": "frontend.closeTask()"}
                    ]
                }
            }
        }
    }
}
```

### 2. Список с фильтром
```json
{
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
        }
    }
}
```

### 3. Диалог выбора
```json
{
    "title": "Выбор счета",
    "className": "vertical",
    "style": {
        "width": "800px",
        "height": "500px"
    },
    "$": {
        "|list": {
            "control": "ListTable",
            "style": {"flex": 1}
        },
        "@buttons": {
            "className": "horizontal",
            "$": {
                "btnSelect": {
                    "label": "Выбрать",
                    "control": "Button",
                    "action": {
                        "js": "dialog.resolve(context.selectedItem)"
                    },
                    "disabled$": "!context.selectedItem"
                }
            }
        }
    }
}
```

## Рекомендации по UI

1. **Группируйте связанные поля** - используйте секции с заголовками
2. **Добавляйте подсказки** - placeholder и tooltip помогают пользователю
3. **Используйте правильные контролы** - DateEdit для дат, CurrencyField для сумм
4. **Валидируйте на лету** - показывайте ошибки сразу при вводе
5. **Отключайте недоступные действия** - используйте disabled$ условия
6. **Показывайте состояние** - индикаторы загрузки, прогресс операций
7. **Следуйте паттернам** - единообразие важно для пользователя
8. **Адаптивность** - используйте flex вместо фиксированной ширины где возможно
9. **Доступность** - всегда добавляйте label к полям ввода
10. **Производительность** - не создавайте слишком сложные формы

## Специальные возможности

### Условная компоновка
```json
{
    "className$": "mem.isCompact ? 'horizontal' : 'vertical'"
}
```

### Динамические списки действий
```json
{
    "actions$": "mem.operations.map(op => ({title: op.name, command: {type: 'js', js: `executeOp('${op.code}')`}}))"
}
```

### Вычисляемые свойства контролов
```json
{
    "controlProps$": "{disabled: mem.isLocked, options: mem.availableOptions}"
}
```

# Архитектура системы SWIFT Processing

## Общий обзор

Система SWIFT Processing представляет собой модульную платформу для обработки банковских SWIFT сообщений стандарта ISO 20022. Система построена на JSON-конфигурациях, которые описывают пользовательский интерфейс, бизнес-логику и взаимодействие с базами данных.

## Структура проекта

```
swift.objects/
├── ao/                           # Прикладные объекты (Application Objects)
│   ├── swiftIncome.json         # Входящие SWIFT сообщения  
│   ├── swiftOutcome.json        # Исходящие SWIFT сообщения
│   ├── swiftBankAccount.json    # Справочник банковских счетов
│   ├── processManagement.json   # Управление процессами
│   ├── processType.json         # Типы процессов (pacs.008, camt.053 и др.)
│   ├── processState.json        # Состояния процессов
│   └── processOperation.json    # Операции над процессами
├── workplace/                    # Конфигурация рабочих мест
│   └── swift.manager.xml        # Меню и структура рабочего места
└── .package.info                # Метаинформация о пакете
```

## Архитектура баз данных

### 1. PostgreSQL (database='default')
Основная БД для хранения SWIFT сообщений и управления процессами:

**Основные таблицы:**
- `swift_input` - входящие SWIFT сообщения (родительская таблица)
- `swift_out_fields` - дополнительные поля для исходящих сообщений
- `swift_settings` - настройки системы
- `process_type` - типы сообщений (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- `process_state` - состояния обработки (LOADED, PROCESSED, PAYMENT_CREATED)
- `process_operation` - доступные операции
- `process_operation_states` - связь операций и состояний (many-to-many)
- `process` - экземпляры процессов

**Дочерние таблицы для camt.053:**
- `swift_stmt_bal` - балансы
- `swift_stmt_ntry` - записи выписки
- `swift_entry_tx_dtls` - детали транзакций

**Дочерние таблицы для camt.054:**
- `swift_ntfctn_ntry` - записи уведомлений
- `swift_ntfctn_tx_dtls` - детали транзакций уведомлений

### 2. Oracle (application='colvir_cbs')
Банковская система Colvir CBS - источник данных о платежах, клиентах, счетах.

## Структура JSON объектов

Каждый JSON объект в папке `ao/` имеет стандартную структуру:

```json
{
    "lists": {
        // Определения списков (таблиц)
    },
    "forms": {
        // Определения форм редактирования
    },
    "methods": {
        // Серверные методы (SQL/Python)
    },
    "references": {
        // Справочники для выбора значений
    },
    "js": {
        // JavaScript функции
    },
    "actions": {
        // Действия уровня объекта
    },
    "filter": {
        // Глобальные фильтры
    }
}
```

### Компоненты объекта

#### 1. Lists (Списки)
Определяют табличные представления данных:

```json
"lists": {
    "default": {
        "columns": {
            "field_name": {
                "title": "Заголовок",
                "width": 120,
                "flex": 1,
                "control": "chip",
                "format": "date"
            }
        },
        "id": "ID",                    // Ключевое поле
        "actions": [],                 // Действия над списком
        "filter": {},                  // Форма фильтрации
        "events": {}                   // Обработчики событий
    }
}
```

#### 2. Forms (Формы)
Определяют формы редактирования и диалоги:

```json
"forms": {
    "editForm": {
        "title": "Заголовок формы",
        "className": "vertical",
        "style": {
            "width": "800px"
        },
        "$": {
            // Иерархия элементов формы
            "@section": {
                "title": "Секция",
                "$": {
                    "field_name": {
                        "label": "Метка",
                        "control": "TextEdit",
                        "required": true,
                        "readOnly$": "expression"
                    }
                }
            }
        },
        "actions": {
            "onTaskCreated": [],
            "customAction": {}
        }
    }
}
```

#### 3. Methods (Методы)
Серверная бизнес-логика:

```json
"methods": {
    "getList": {
        "sql": {
            "sqlType": "query",
            "database": "default",
            "sql": "SELECT * FROM table"
        },
        "script": {
            "py": "Python code here"
        }
    }
}
```

## Система управления процессами

### Process Types (Типы процессов)
- `pacs.008` - Customer Credit Transfer
- `pacs.009` - Financial Institution Credit Transfer (COV)
- `camt.053` - Bank to Customer Statement
- `camt.054` - Bank to Customer Debit/Credit Notification
- `camt.056` - FI to FI Payment Cancellation Request

### Process States (Состояния)
Каждый тип процесса имеет свои состояния:
- `LOADED` - Загружен (начальное состояние)
- `PROCESSED` - Обработан
- `PAYMENT_CREATED` - Платеж создан (для pacs.008)

### Process Operations (Операции)
Операции доступны в определенных состояниях:
- `MARK_AS_PROCESSED` - Отметить как обработанный
- `CANCEL_PROCESSING` - Отменить обработку
- `CREATE_PAYMENT` - Создать платеж

## Контролы и UI элементы

### Базовые контролы:
- `TextEdit` - текстовое поле
- `DateEdit` - выбор даты
- `SelectEdit` / `SelectList` - выпадающий список
- `Checkbox` - флажок
- `Button` - кнопка
- `CurrencyField` - поле для валюты
- `ObjectReference` - ссылка на объект
- `ListTable` - таблица
- `AceEditor` - редактор кода

### Специальные возможности:
- `readOnly$` - динамическое вычисление состояния readonly
- `visible$` - динамическое управление видимостью
- `disabled$` - динамическое управление доступностью
- `actions` - обработчики событий

## Жизненный цикл обработки SWIFT сообщения

1. **Импорт**: Файл загружается в систему, создается запись в `swift_input`
2. **Парсинг**: Извлечение данных из XML, заполнение полей
3. **Создание процесса**: Создается экземпляр в таблице `process`
4. **Обработка**: Выполнение операций согласно workflow
5. **Формирование ответа**: Генерация исходящих сообщений
6. **Отправка**: Экспорт файлов в целевую систему

## Важные правила и ограничения

1. **Стандартные поля**: Не изменяйте названия стандартных полей - движок обрабатывает их специальным образом
2. **База данных**: Новые таблицы создавайте только в PostgreSQL
3. **Паттерны**: Строго следуйте существующим паттернам при добавлении функциональности
4. **Контекст**: Используйте правильные объекты контекста (mem, context, $listRow)
5. **Транзакции**: Python скрипты автоматически выполняются в транзакции

## Дальнейшие разделы

- Примеры типовых задач
- Подробное описание каждого объекта
- API движка и доступные функции
- Рекомендации по разработке

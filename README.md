# SWIFT Processing System

Система обработки банковских SWIFT сообщений стандарта ISO 20022.

## ⚠️ ВАЖНО

Это **специфический внутренний фреймворк**, не общеизвестная система. Все задачи реализуются строго по существующим паттернам.

## 📚 Документация

Вся документация находится в папке [`docs/`](./docs/):

- [**Краткий справочник**](./docs/QUICK_REFERENCE.md) 🚀 - быстрые шаблоны и примеры
- [Руководство разработчика](./docs/SWIFT_DEVELOPER_GUIDE.md) - начните отсюда
- [Справочник зарезервированных слов](./docs/RESERVED_WORDS_REFERENCE.md) ⚠️ **КРИТИЧЕСКИ ВАЖНО**
- [Практические паттерны](./docs/PRACTICAL_PATTERNS.md) - реальные примеры из системы
- [Архитектура системы](./docs/SWIFT_PROCESSING_ARCHITECTURE.md)
- [Структура JSON объектов](./docs/JSON_STRUCTURE_GUIDE.md)
- [Работа с БД](./docs/DATABASE_PATTERNS.md)
- [UI компоненты](./docs/UI_COMPONENTS_GUIDE.md)
- [Управление процессами](./docs/PROCESS_MANAGEMENT_GUIDE.md)
- [Примеры типовых задач](./docs/COMMON_TASKS_EXAMPLES.md)

## 🚀 Быстрый старт

1. Изучите существующие объекты в `swift.objects/ao/`
2. Найдите похожий паттерн
3. Скопируйте и адаптируйте
4. **Никогда не изобретайте новое!**

## 🔴 Критические правила

1. **НЕ меняйте зарезервированные слова** (`columns`, `title`, `width`, `control`, etc.)
2. **НЕ переименовывайте поля БД** (`imported`, `msg_type`, `file_name`, etc.)
3. **НЕ изменяйте данные в Oracle** - только чтение
4. **ВСЕГДА следуйте существующим паттернам**
5. **Python в JSON** - одна строка с `\n` для переводов
6. **Операции процессов** - используйте `runOperations`, НЕ создавайте отдельные методы!

## 📁 Структура проекта

```
swift-processing/
├── swift.objects/              # Конфигурации системы
│   ├── ao/                    # Прикладные объекты (JSON)
│   │   ├── swiftIncome.json   # Входящие сообщения
│   │   ├── swiftOutcome.json  # Исходящие сообщения
│   │   └── ...
│   └── workplace/             # Рабочие места (XML)
├── docs/                      # Документация
├── test_data/                 # Тестовые данные
└── db_schema_full.sql        # Схема БД PostgreSQL
```

## 🔧 Основные компоненты

- **lists** - табличные представления данных
- **forms** - формы редактирования
- **methods** - серверная логика (Python/SQL)
- **references** - справочники для выбора

## 💡 Контекстные переменные

- `mem` - данные текущей формы
- `$listRow` - выбранная строка в списке
- `context` - общий контекст для хранения данных
- `params` - параметры вызова
- `task` - текущая задача

## ⚡ Примеры

### Вызов метода
```javascript
backend.post('/aoa/execObjectMethod', {
    object: 'swiftIncome',
    method: 'getList',
    params: {filter: 'active'}
})
```

### Вызов операции процесса
```javascript
// ВСЕГДА через runOperations!
backend.post('/aoa/execObjectMethod', {
    object: 'swiftIncome',
    method: 'runOperations',
    params: {
        process_id: processId,
        operation_code: 'MARK_AS_PROCESSED'
    }
})
```

### Python в JSON (одна строка!)
```json
"script": {
    "py": "from apng_core.db import fetchall\n\nSQL = 'SELECT * FROM table'\nwith initDbSession(database='default').cursor() as c:\n    c.execute(SQL)\n    data = fetchall(c)"
}
```

---

**Помните**: Это не React, не Vue, не Angular. Это уникальная система со своими правилами!

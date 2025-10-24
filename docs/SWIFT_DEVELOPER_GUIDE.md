# Руководство разработчика SWIFT Processing

## Содержание

1. [Введение](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Архитектура системы](#архитектура-системы)
4. [Структура JSON объектов](#структура-json-объектов)
5. [Работа с базами данных](#работа-с-базами-данных)
6. [UI компоненты](#ui-компоненты)
7. [Управление процессами](#управление-процессами)
8. [Типовые задачи](#типовые-задачи)
9. [Важные правила и ограничения](#важные-правила-и-ограничения)
10. [FAQ](#faq)

## Введение

SWIFT Processing - это модульная система для обработки банковских SWIFT сообщений стандарта ISO 20022. Система построена на декларативных JSON конфигурациях, которые описывают все аспекты: от UI до бизнес-логики.

### Основные принципы
- **Декларативность**: UI и логика описываются в JSON
- **Модульность**: каждый объект независим и самодостаточен
- **Расширяемость**: легко добавлять новые типы сообщений и операции
- **Двухуровневая БД**: PostgreSQL для системы + Oracle Colvir для банковских данных

## Быстрый старт

### Структура проекта
```
swift.objects/
├── ao/                         # Прикладные объекты
│   ├── swiftIncome.json       # Входящие сообщения
│   ├── swiftOutcome.json      # Исходящие сообщения
│   └── processManagement.json # Управление процессами
├── workplace/                  # Рабочие места
│   └── swift.manager.xml      # Конфигурация меню
└── .package.info              # Метаданные пакета
```

### Первые шаги

1. **Изучите существующий объект**
   ```bash
   cat swift.objects/ao/swiftIncome.json
   ```

2. **Найдите нужный паттерн**
   - Списки: секция `"lists"`
   - Формы: секция `"forms"`
   - Методы: секция `"methods"`

3. **Скопируйте и адаптируйте**
   - Никогда не создавайте с нуля
   - Всегда отталкивайтесь от существующего

## Архитектура системы

### Слои системы

```
┌─────────────────────────────────────┐
│         UI Layer (JSON)             │ ← Формы, списки, контролы
├─────────────────────────────────────┤
│      Business Logic (Python)        │ ← Методы, валидация
├─────────────────────────────────────┤
│         Data Layer                  │
│  ┌─────────────┬─────────────────┐ │
│  │ PostgreSQL  │  Oracle Colvir   │ │ ← SWIFT данные | Банк. данные
│  └─────────────┴─────────────────┘ │
└─────────────────────────────────────┘
```

### Поток обработки сообщения

```
Файл SWIFT → Импорт → Парсинг → Создание процесса → Обработка → Результат
     ↓          ↓         ↓            ↓                ↓           ↓
  XML/TXT   swift_input  Поля     process table    Operations   Outgoing
```

## Структура JSON объектов

### Минимальный объект
```json
{
    "lists": {},      // Табличные представления
    "forms": {},      // Формы и диалоги
    "methods": {},    // Серверная логика
    "references": {}, // Справочники
    "js": {},        // JavaScript функции
    "actions": {},    // Глобальные действия
    "filter": {}      // Глобальные фильтры
}
```

### Ключевые концепции

#### 1. Динамические выражения ($)
```json
{
    "visible$": "mem.showField === true",      // Условная видимость
    "disabled$": "!$listRow || mem.readonly",  // Условное отключение
    "title$": "`Платеж №${mem.number}`",       // Шаблонные строки
    "value$": "mem.amount * mem.rate"          // Вычисляемые значения
}
```

#### 2. Префиксы элементов формы
- Без префикса: обычное поле `"fieldName": {}`
- `@` - группа/секция: `"@section": {}`
- `|` - список/таблица: `"|items": {}`
- `.` - системные элементы: `".btnSave": {}`

#### 3. Контекстные переменные
- `mem` - память формы (данные)
- `context` - контекст выполнения
- `$listRow` - текущая строка списка
- `params` - параметры вызова
- `task` - текущая задача

## Работа с базами данных

### PostgreSQL (Системная БД)
```python
# Чтение данных
with initDbSession(database='default').cursor() as c:
    c.execute('SELECT * FROM swift_input WHERE id = %(id)s', {'id': id})
    data = fetchone(c)

# Вставка с конфликтом
SQL = '''
    INSERT INTO swift_out_fields (dep_id, id, content)
    VALUES (%(dep_id)s, %(id)s, %(content)s)
    ON CONFLICT (dep_id, id) DO UPDATE SET
        content = EXCLUDED.content
'''
```

### Oracle (Colvir CBS)
```python
# Только чтение!
with initDbSession(application='colvir_cbs').cursor() as c:
    c.execute('''
        SELECT J.ID, V.CODE as VAL_CODE
        FROM P_ORD J, T_VAL V
        WHERE V.ID = J.VAL_ID
    ''', params)
```

## UI компоненты

### Основные контролы
- `TextEdit` - текстовое поле
- `DateEdit` - выбор даты
- `SelectEdit` - выпадающий список
- `Checkbox` - флажок
- `Button` - кнопка
- `CurrencyField` - денежная сумма
- `ObjectReference` - ссылка на объект
- `ListTable` - таблица

### Паттерн формы редактирования
```json
{
    "title": "Редактирование",
    "className": "vertical",
    "$": {
        "@fields": {
            "className": "vertical",
            "$": {
                // Поля формы
            }
        },
        "@buttons": {
            "className": "horizontal",
            "style": {"justifyContent": "flex-end"},
            "$": {
                "btnCancel": {
                    "label": "Отмена",
                    "control": "Button",
                    "action": {"js": "frontend.closeTask()"}
                },
                "btnSave": {
                    "label": "Сохранить", 
                    "control": "Button",
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

## Управление процессами

### Компоненты
1. **Process Type** - типы сообщений (pacs.008, camt.053...)
2. **Process State** - состояния (LOADED, PROCESSED...)
3. **Process Operation** - операции (MARK_AS_PROCESSED...)
4. **Process** - экземпляры процессов

### Добавление новой операции

**ВАЖНО**: Операции выполняются через унифицированный метод `runOperations`! НЕ создавайте отдельные методы.

```sql
-- 1. Создать операцию
INSERT INTO process_operation (type_code, code, name_ru, to_state)
VALUES ('pacs.008', 'VALIDATE', 'Проверить', 'VALIDATED');

-- 2. Связать с состояниями  
INSERT INTO process_operation_states (operation_id, state_id)
SELECT o.id, s.id FROM process_operation o, process_state s
WHERE o.code = 'VALIDATE' AND s.code = 'LOADED';

-- 3. Если нужна специальная логика:
-- Для PL/SQL (Oracle):
UPDATE process_operation SET resource_url = 'DECLARE ... BEGIN ... END;'
WHERE code = 'VALIDATE';

-- Для Python:
UPDATE process_operation SET database = 'python', resource_url = 'validateMethod'
WHERE code = 'VALIDATE';
```

Операция вызывается через:
```javascript
backend.post('/aoa/execObjectMethod', {
    object: 'swiftIncome',
    method: 'runOperations',
    params: {process_id: id, operation_code: 'VALIDATE'}
})
```

## Типовые задачи

### 1. Добавить новое поле в форму
```json
// В секции "$" формы добавить:
"new_field": {
    "label": "Новое поле",
    "control": "TextEdit",
    "required": true,
    "placeholder": "Введите значение"
}
```

### 2. Добавить колонку в список
```json
// В "columns" списка добавить:
"new_column": {
    "title": "Новая колонка",
    "width": 150,
    "format": "currency"
}
```

### 3. Создать новый метод
```json
"methods": {
    "myMethod": {
        "script": {
            "py": """
from apng_core.db import fetchone

# Ваш код здесь
data = {'result': 'success'}
"""
        }
    }
}
```

## Важные правила и ограничения

### ❗ КРИТИЧЕСКИ ВАЖНО

1. **НЕ изменяйте названия стандартных полей**
   - Движок обрабатывает их специальным образом
   - Изменение приведет к неработоспособности

2. **НЕ создавайте таблицы в Oracle**
   - Oracle Colvir - только для чтения
   - Все новые таблицы - только в PostgreSQL

3. **ВСЕГДА следуйте существующим паттернам**
   - Не изобретайте новые подходы
   - Копируйте и адаптируйте существующее

4. **ИСПОЛЬЗУЙТЕ параметризованные запросы**
   ```python
   # ✅ Правильно
   c.execute('SELECT * FROM t WHERE id = %(id)s', {'id': value})
   
   # ❌ Неправильно
   c.execute(f'SELECT * FROM t WHERE id = {value}')
   ```

5. **ПРОВЕРЯЙТЕ типы БД в методах**
   ```python
   # PostgreSQL
   initDbSession(database='default')
   
   # Oracle
   initDbSession(application='colvir_cbs')
   ```

## FAQ

### Q: Как добавить новый тип SWIFT сообщения?
A: 
1. Добавьте запись в `process_type`
2. Создайте состояния в `process_state`
3. Создайте операции в `process_operation`
4. Обновите парсер для нового типа

### Q: Почему не работает мое поле после переименования?
A: Вы изменили стандартное поле. Движок ожидает конкретные имена. Верните оригинальное название.

### Q: Как отладить Python код в методах?
A: 
- Используйте `logging.getLogger()`
- Проверяйте логи сервера
- Используйте `raise Exception(debug_data)` для быстрой отладки

### Q: Можно ли использовать React компоненты?
A: Нет, система использует собственный рендерер. Используйте только документированные контролы.

### Q: Как сделать поле обязательным только при условии?
A: 
```json
{
    "required$": "mem.payment_type === 'international'"
}
```

### Q: Где хранятся файлы SWIFT сообщений?
A: Пути настраиваются в таблице `swift_settings`:
- `folder_in` - входящие
- `folder_out` - исходящие
- `folder_unprocessed` - необработанные

## Полезные ссылки

### Документация по компонентам
- [Архитектура системы](./SWIFT_PROCESSING_ARCHITECTURE.md)
- [Структура JSON объектов](./JSON_STRUCTURE_GUIDE.md)
- [Справочник зарезервированных слов](./RESERVED_WORDS_REFERENCE.md) ⚠️ **КРИТИЧЕСКИ ВАЖНО**
- [Работа с БД](./DATABASE_PATTERNS.md)
- [UI компоненты](./UI_COMPONENTS_GUIDE.md)
- [Управление процессами](./PROCESS_MANAGEMENT_GUIDE.md)
- [Примеры задач](./COMMON_TASKS_EXAMPLES.md)

## Контакты и поддержка

При возникновении вопросов:
1. Проверьте существующие примеры
2. Изучите документацию
3. Обратитесь к старшему разработчику

---

**Помните**: Лучше потратить время на изучение существующих паттернов, чем сломать систему креативными решениями!

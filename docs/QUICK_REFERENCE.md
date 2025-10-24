# Краткий справочник SWIFT Processing

## 🔴 Главные правила

1. **НИКОГДА** не меняйте зарезервированные слова
2. **ВСЕГДА** копируйте существующие паттерны
3. **Python в JSON** - одна строка с `\n`
4. **PostgreSQL** - наша БД, **Oracle** - только чтение
5. **forceUpdate()** после изменения `mem`

## 📝 Быстрые шаблоны

### Добавить колонку в список
```json
"new_column": {
    "title": "Название",
    "width": 150,
    "format": "currency"  // date, datetime, datetimesec, currency, number
}
```

### Добавить поле в форму
```json
"field_name": {
    "label": "Метка",
    "control": "TextEdit",  // См. список контролов ниже
    "required": true,
    "placeholder": "Подсказка",
    "style": {"width": "300px"}
}
```

### Добавить метод
```json
"methodName": {
    "script": {
        "py": "from apng_core.db import fetchall\n\nSQL = 'SELECT * FROM table'\n\nwith initDbSession(database='default').cursor() as c:\n    c.execute(SQL)\n    data = fetchall(c)"
    }
}
```

### Добавить кнопку в список
```json
{
    "title": "Действие",
    "icon": "send",
    "command": {
        "type": "js",
        "js": "backend.post('/aoa/execObjectMethod', {object: 'swiftIncome', method: 'process', params: {id: $listRow.id}})"
    },
    "visible$": "$listRow.state === 'new'"
}
```

## 🎛️ Контролы

| Контрол | Описание | Пример |
|---------|----------|--------|
| `TextEdit` | Текстовое поле | `"control": "TextEdit"` |
| `TextArea` | Многострочный текст | `"control": "TextArea", "controlProps": {"rows": 5}` |
| `DateEdit` | Дата | `"control": "DateEdit"` |
| `CurrencyField` | Сумма | `"control": "CurrencyField"` |
| `SelectList` | Список | `"control": "SelectList", "controlProps": {"list": [...]}` |
| `SelectEdit` | Список с поиском | `"control": "SelectEdit"` |
| `Checkbox` | Флажок | `"control": "Checkbox"` |
| `Button` | Кнопка | `"control": "Button"` |
| `ObjectReference` | Ссылка | `"control": "ObjectReference", "controlProps": {"object": "name"}` |
| `ListTable` | Таблица | `"control": "ListTable"` |
| `AceEditor` | Редактор кода | `"control": "AceEditor"` |
| `Chip` | Чип | `"control": "chip"` (в колонках) |

## 🔧 JavaScript функции

### Backend
```javascript
// Вызов метода
backend.post('/aoa/execObjectMethod', {
    object: 'objectName',
    method: 'methodName', 
    params: {param1: value1}
})

// С кешированием
backend.post(..., {useCache: true})
```

### Frontend
```javascript
frontend.closeTask()              // Закрыть задачу
frontend.showMessage('Текст')     // Показать сообщение
frontend.dialog({...})            // Открыть диалог
frontend.newTask({...})           // Новая задача
```

### Утилиты
```javascript
validate()                        // Проверить форму
forceUpdate()                     // Обновить UI
forceRefreshList()               // Обновить список
```

## 🗃️ Контекстные переменные

| Переменная | Где доступна | Описание |
|------------|--------------|----------|
| `mem` | Формы | Данные формы |
| `$listRow` | Списки | Текущая строка |
| `context` | Везде | Общий контекст |
| `params` | События | Параметры события |
| `task` | Формы | Текущая задача |
| `parameters` | Python | Входные параметры |
| `data` | Python | Результат (обязательно!) |

## 🔀 Динамические выражения ($)

```json
"visible$": "mem.showField"                    // Видимость
"disabled$": "!$listRow"                       // Отключение
"readOnly$": "!!mem.id"                        // Только чтение
"title$": "`Сумма: ${mem.amount}`"            // Шаблон строки
"value$": "mem.price * mem.quantity"           // Вычисление
"style$": "{color: mem.error ? 'red' : ''}"   // Стили
```

## 📊 SQL паттерны

### PostgreSQL
```python
# SELECT
with initDbSession(database='default').cursor() as c:
    c.execute('SELECT * FROM table WHERE id = %(id)s', {'id': id})
    data = fetchall(c)  # или fetchone(c)

# INSERT/UPDATE с конфликтом
SQL = '''
    INSERT INTO table (id, field) VALUES (%(id)s, %(field)s)
    ON CONFLICT (id) DO UPDATE SET field = EXCLUDED.field
'''
```

### Oracle (только чтение!)
```python
with initDbSession(application='colvir_cbs').cursor() as c:
    c.execute('SELECT * FROM P_ORD WHERE ID = :id', {'id': id})
```

## 🎨 Стандартные иконки

`refresh`, `add`, `edit`, `delete`, `save`, `send`, `check`, `undo`, `visibility`, `payment`, `close`

## 🚨 Частые ошибки

❌ **Неправильно:**
```json
"script": {
    "py": """
    from apng_core.db import fetchall
    SQL = 'SELECT * FROM table'
    """
}
```

✅ **Правильно:**
```json
"script": {
    "py": "from apng_core.db import fetchall\nSQL = 'SELECT * FROM table'"
}
```

❌ **Неправильно:**
```javascript
backend.post(...).then(forceUpdate())  // Вызывается сразу!
```

✅ **Правильно:**
```javascript
backend.post(...).then(() => forceUpdate())  // Функция
```

❌ **Неправильно:**
```python
c.execute(f"SELECT * FROM t WHERE id = {value}")  // SQL injection!
```

✅ **Правильно:**
```python
c.execute("SELECT * FROM t WHERE id = %(id)s", {'id': value})
```

## 📋 Чек-лист новой функции

- [ ] Нашел похожий паттерн в существующих объектах
- [ ] Скопировал и адаптировал (не создал с нуля!)
- [ ] Проверил зарезервированные слова
- [ ] Python в одну строку с `\n`
- [ ] Использовал параметризованные запросы
- [ ] Добавил `forceUpdate()` после изменения `mem`
- [ ] Проверил в какую БД идет запрос
- [ ] Протестировал

# Справочник зарезервированных слов

## ⚠️ КРИТИЧЕСКИ ВАЖНО

Зарезервированные слова - это ключи JSON, которые обрабатываются движком специальным образом. **НИКОГДА не изменяйте их!**

## Зарезервированные слова vs Поля БД

### Пример из списка (list)
```json
"columns": {                    // ← ЗАРЕЗЕРВИРОВАННОЕ
    "imported": {              // ← Поле БД (можно менять)
        "title": "Дата",       // ← ЗАРЕЗЕРВИРОВАННОЕ
        "width": 170,          // ← ЗАРЕЗЕРВИРОВАННОЕ
        "format": "datetime"   // ← ЗАРЕЗЕРВИРОВАННОЕ
    },
    "msg_type": {              // ← Поле БД
        "title": "Тип"         // ← ЗАРЕЗЕРВИРОВАННОЕ
    }
}
```

## Полный список зарезервированных слов

### Для списков (lists)

```json
{
    "columns": {},              // Определение колонок
    "id": "ID",                // Ключевое поле
    "getList": "methodName",   // Метод получения данных
    "getRowStyle": "",         // Стили строк
    "actions": [],             // Действия
    "filter": {},              // Фильтрация
    "events": {}               // События
}
```

#### В columns:
- `title` - заголовок колонки
- `width` - ширина в пикселях
- `flex` - гибкая ширина
- `control` - контрол отображения
- `format` - форматирование
- `fields` - составные поля
- `cellStyle` - стили ячейки
- `decode` - декодирование значений
- `readonly` - только чтение

#### В actions:
- `title` - название действия
- `icon` - иконка
- `mini` - маленькая кнопка
- `split` - кнопка с подменю
- `command` - команда
- `disabled$` - условное отключение
- `visible$` - условная видимость
- `confirm` - подтверждение

#### В command:
- `type` - тип команды (standard, task, js)
- `call` - вызываемая функция
- `params` - параметры
- `title$` - динамический заголовок

### Для форм (forms)

```json
{
    "title": "",               // Заголовок формы
    "title$": "",             // Динамический заголовок
    "className": "",          // CSS класс
    "style": {},              // Стили
    "$": {},                  // Элементы формы
    "actions": {}             // Действия формы
}
```

#### В элементах формы:
- `label` - метка поля
- `control` - тип контрола
- `controlProps` - свойства контрола
- `controlOpts` - опции контрола
- `required` - обязательное поле
- `placeholder` - подсказка
- `readOnly$` - динамический readonly
- `visible$` - динамическая видимость
- `disabled$` - динамическое отключение
- `style` - стили элемента
- `actions` - обработчики событий

### Для методов (methods)

```json
{
    "sql": {
        "sqlType": "",         // query, script
        "database": "",        // default, colvir_cbs
        "sql": "",            // SQL запрос
        "params": []          // Параметры
    },
    "script": {
        "py": ""              // Python код
    }
}
```

### Для справочников (references)

```json
{
    "form": {
        "style": {},
        "columns": [],
        "primaryKey": "",
        "titleField": "",
        "valueField": "",
        "displayField": "",
        "fastFilter": true,
        "filter": {},
        "method": ""
    }
}
```

## Специальные префиксы элементов

- **Без префикса** - обычное поле: `"fieldName": {}`
- **@** - группа элементов: `"@section": {}`
- **|** - список/таблица: `"|items": {}`
- **.** - системные элементы: `".btnSave": {}`

## Динамические выражения (суффикс $)

Любое свойство с суффиксом `$` вычисляется динамически:

```json
{
    "visible$": "mem.showField === true",
    "disabled$": "!$listRow",
    "title$": "`Сумма: ${mem.amount}`",
    "objectKey$": "{id: $listRow.id}"
}
```

## Типы контролов

### Текстовые
- `TextEdit` - однострочное поле
- `TextArea` - многострочное поле

### Числовые и даты
- `CurrencyField` - денежная сумма
- `DateEdit` - выбор даты

### Выбор значений
- `SelectEdit` - с поиском
- `SelectList` - простой список
- `Checkbox` - флажок
- `ObjectReference` - ссылка на объект

### Отображение
- `Chip` - чип статуса
- `ListTable` - таблица
- `AceEditor` - редактор кода

### Действия
- `Button` - кнопка
- `ActionPanel` - панель действий

## Форматы данных

### format для колонок
- `date` - дата
- `datetime` - дата и время
- `datetimesec` - дата, время, секунды
- `currency` - валюта
- `number` - число

### Типы команд (type)
- `standard` - стандартная (refresh, close)
- `task` - открытие задачи
- `js` - JavaScript код

## Контекстные переменные

### Доступны везде
- `mem` - память формы (данные)
- `context` - общий контекст
- `params` - параметры вызова

### В списках
- `$listRow` - текущая строка

### В формах
- `task` - текущая задача
- `dialog` - текущий диалог

### В методах Python
- `parameters` - входные параметры
- `data` - результат (обязательно!)

## Функции JavaScript

### Backend
```javascript
backend.post('/aoa/execObjectMethod', {
    object: 'objectName',
    method: 'methodName',
    params: {}
})
```

### Frontend
```javascript
frontend.closeTask()
frontend.showMessage('text')
frontend.dialog({})
frontend.newTask({})
```

### Утилиты
```javascript
validate()              // Валидация формы
forceUpdate()          // Обновление UI
forceRefreshList()     // Обновление списка
```

## Python в JSON

**ВАЖНО**: Python код в JSON хранится в одной строке с `\n` для переводов:

```json
"script": {
    "py": "from apng_core.db import fetchall\n\nSQL = '''SELECT * FROM table'''\n\nwith initDbSession(database='default').cursor() as c:\n    c.execute(SQL)\n    data = fetchall(c)"
}
```

### Доступные импорты
```python
from apng_core.db import fetchall, fetchone, initDbSession
from apng_core.exceptions import UserException
from apng_core.auth import getUser
from apng_core.aoa.services import filter as aoa
```

---

**Помните**: Если не уверены, является ли слово зарезервированным - проверьте в существующих объектах!

# UI Updates - Compact & Modern Design

## Что изменено:

### ✅ Компактный Header
- Убран заголовок "Process Manager"
- Кнопка сохранения - только иконка слева
- Переключатель день/ночь справа
- Минимальный padding (0.5)

### ✅ Левая панель - Tree с кнопками управления
**Новые кнопки:**
- ➕ Add type - добавить новый тип
- ↳ Add child - добавить дочерний тип
- 🗑️ Delete - удалить выбранный тип

**Компактный список:**
- Уменьшенные отступы (py: 0.5)
- Минимальная высота строки (32px)
- Компактные шрифты (body2 / caption)

### ✅ Средняя панель - Компактные таблицы

**Type Attributes:**
- Редактируемые поля (кроме Code)
- При изменении активируется кнопка Save
- Compact padding (1.5)

**States List:**
- Сокращенные заголовки (E/D/S вместо Edit/Delete/Start)
- Маленькие иконки цветов (16x16)
- Компактные чекбоксы (p: 0)
- Размер шрифта: 0.75rem

**Operations List:**
- Cancel показан как чип "C"
- Убрана колонка Name (RU) для экономии места
- Компактный шрифт

### ✅ Правая панель - Компактный редактор

**State Editor:**
- Subtitle вместо h6
- Все изменения сохраняются в store
- Активирует кнопку Save

**Operation Editor:**
- Те же улучшения
- Multiline поля для скриптов
- Все подключено к changes store

### ✅ Тема день/ночь
- Сохраняется в localStorage
- Переключатель в header справа
- Полная поддержка Material-UI темы

## Как работает сохранение:

1. Редактируете атрибуты типа → кнопка Save активна
2. Редактируете state → кнопка Save активна
3. Редактируете operation → кнопка Save активна
4. Жмете Save → все изменения уходят на backend одним запросом

## Активация кнопки Save:

Кнопка становится активной при изменении:
- Type attributes (name_en, name_ru, attributes_table)
- State properties (name, color, flags)
- Operation properties (name, icon, scripts)

## Компактность:

**Было:**
- Header padding: 2
- Panel padding: 2
- Font sizes: h6, h5, body1
- Large tables with full names

**Стало:**
- Header padding: 0.5
- Panel padding: 1
- Font sizes: subtitle2, body2, caption (0.75rem)
- Compact tables with abbreviations

## Открыть приложение:

```bash
http://localhost:3000
```

Попробуйте:
1. Выбрать тип (например pacs.008)
2. Изменить Name (English) в Type Attributes
3. Увидеть что кнопка Save стала активной (синяя)
4. Переключить день/ночь (иконка справа вверху)
5. Кликнуть на state → редактировать в правой панели


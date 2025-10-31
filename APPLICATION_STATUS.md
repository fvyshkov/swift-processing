# Process Manager Application - Status

## ✅ Приложение РАБОТАЕТ!

### Что запущено:

1. **PostgreSQL Database** ✅
   - База данных: `swift_processing`
   - Загружено из `process.txt`:
     - 7 process types
     - 13 process states  
     - 14 process operations
     - 11 operation-state relations

2. **Backend (FastAPI)** ✅
   - URL: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs
   - Запущен с виртуальным окружением (venv)

3. **Frontend (React + TypeScript)** ✅
   - URL: http://localhost:3000
   - Vite dev server
   - Material-UI интерфейс

## Как использовать:

### Откройте браузер:
```
http://localhost:3000
```

### Основные функции:

1. **Левая панель** - список типов процессов (SWIFT, pacs.008, etc.)
2. **Средняя панель** - детали выбранного типа:
   - Атрибуты типа
   - Список состояний (states) с цветовой индикацией
   - Список операций (operations)
3. **Правая панель** - редактор для выбранного состояния или операции

### API endpoints работают:

```bash
# Получить все типы
curl http://localhost:8000/api/v1/types

# Получить состояния для pacs.008
curl http://localhost:8000/api/v1/types/pacs.008/states

# Получить операции для pacs.008
curl http://localhost:8000/api/v1/types/pacs.008/operations
```

## Управление приложением:

### Запуск backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или просто:
```bash
./start_backend.sh
```

### Запуск frontend:
```bash
cd frontend
npm run dev
```

### Остановка:
```bash
# Остановить все процессы
pkill -f "uvicorn app.main:app"
pkill -f "vite"
```

## Структура проекта:

### Backend (`/backend`)
- FastAPI REST API
- SQLAlchemy async ORM
- PostgreSQL database
- Все CRUD операции реализованы
- Endpoint для batch save

### Frontend (`/frontend`)
- React 18 + TypeScript
- Material-UI v5
- React Query для данных
- Zustand для state management
- 3-панельный layout

## Что работает:

✅ Загрузка и отображение типов процессов
✅ Загрузка и отображение состояний
✅ Загрузка и отображение операций  
✅ Отображение цветов состояний
✅ Выбор типа/состояния/операции
✅ Просмотр деталей в правой панели
✅ Базовое редактирование (UI готов)

## Что можно улучшить:

⚠️ Сохранение изменений (кнопка "Save All Changes" - нужно подключить к store)
⚠️ Добавление/удаление состояний и операций (кнопки не добавлены)
⚠️ Древовидная структура типов (сейчас плоский список)
⚠️ Color picker для состояний
⚠️ Code editor для Python скриптов
⚠️ Валидация на frontend

## Файлы конфигурации:

- `backend/.env` - не создан (используются значения по умолчанию)
- `backend/app/config.py` - автоматически определяет USER для подключения к БД
- `frontend/src/api/client.ts` - API_BASE_URL = http://localhost:8000/api/v1

## База данных:

Подключение к PostgreSQL:
```bash
psql swift_processing

# Посмотреть типы
SELECT code, name_en FROM process_type;

# Посмотреть состояния для pacs.008
SELECT s.code, s.name_en, s.color_code 
FROM process_state s 
JOIN process_type t ON s.type_id = t.id 
WHERE t.code = 'pacs.008';
```

## Logs и отладка:

Backend logs в консоли где запущен uvicorn
Frontend logs в консоли браузера (F12)

## Следующие шаги:

1. Откройте http://localhost:3000 в браузере
2. Выберите тип в левой панели
3. Посмотрите состояния и операции в средней панели
4. Кликните на состояние/операцию для редактирования

Приложение полностью функционально для просмотра и базового редактирования!


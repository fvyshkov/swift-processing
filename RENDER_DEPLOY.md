# Deploy to Render.com

## Информация для деплоя

- **Email**: fvyshkov@gmail.com
- **API Key**: rnd_1jMp7KapvojqxZu2uJAAJdxJcqrM
- **Region**: Frankfurt (EU)

## Структура проектов

Будут созданы 3 сервиса на Render:

1. **PostgreSQL Database** - `process-manager-db`
2. **Backend API** - `process-manager-backend` (FastAPI)
3. **Frontend** - `process-manager-frontend` (React Static Site)

## Подготовка к деплою

### Шаг 1: Создать репозиторий на GitHub

```bash
cd /Users/fvyshkov/PROJECTS/swift-processing

# Инициализация git (если еще не сделано)
git init
git add .
git commit -m "Initial commit: Process Manager app"

# Создать репозиторий на GitHub и залить
git remote add origin https://github.com/fvyshkov/swift-processing.git
git branch -M main
git push -u origin main
```

### Шаг 2: Создать проекты на Render

#### Вариант A: Через Blueprint (автоматически)

1. Зайти на https://dashboard.render.com
2. New → Blueprint
3. Подключить GitHub репозиторий
4. Выбрать файл `render.yaml`
5. Render автоматически создаст все 3 сервиса

#### Вариант B: Вручную

**1. Создать PostgreSQL:**
- New → PostgreSQL
- Name: `process-manager-db`
- Database: `swift_processing`
- User: `postgres`
- Region: Frankfurt
- Plan: Free

**2. Создать Backend:**
- New → Web Service
- Connect repository
- Name: `process-manager-backend`
- Environment: Python
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `DATABASE_URL` = (internal connection string from database)
  - `FRONTEND_URL` = (URL frontend после создания)

**3. Создать Frontend:**
- New → Static Site
- Connect repository
- Name: `process-manager-frontend`
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Environment Variables:
  - `VITE_API_URL` = (URL backend)

### Шаг 3: Загрузить данные в БД

После создания PostgreSQL:

```bash
# Получить connection string из Render dashboard
# Формат: postgresql://user:password@hostname:5432/database

# Загрузить схему и данные
psql "postgresql://user:password@hostname:5432/swift_processing" < process.txt
```

Или через Render Dashboard:
1. Открыть Database → Connect
2. Использовать External Connection String
3. Загрузить данные через psql

## Автоматический деплой

### Файлы для Render

✅ `render.yaml` - Blueprint конфигурация
✅ `backend/requirements.txt` - Python зависимости  
✅ `frontend/package.json` - Node зависимости
✅ Переменные окружения настроены

### Environment Variables

**Backend:**
- `DATABASE_URL` - автоматически из PostgreSQL service
- `FRONTEND_URL` - URL фронтенда (для CORS)
- `PORT` - автоматически от Render

**Frontend:**
- `VITE_API_URL` - URL бекенда

## URLs после деплоя

После успешного деплоя получите:

- **Backend**: https://process-manager-backend.onrender.com
- **Frontend**: https://process-manager-frontend.onrender.com
- **Database**: Internal URL (не публичный)

## Команды для локальной проверки перед деплоем

```bash
# Проверить что backend собирается
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Проверить что frontend собирается
cd frontend
npm install
npm run build
```

## Важные замечания

### Free Plan ограничения:
- Backend засыпает после 15 минут без активности
- Первый запрос может быть медленным (cold start)
- PostgreSQL Free: 256MB RAM, 1GB storage

### CORS настройка:
Backend автоматически добавит URL фронтенда в allowed origins через переменную `FRONTEND_URL`.

### Database Migration:
После создания БД нужно:
1. Создать таблицы (из `process.txt`)
2. Загрузить данные
3. Проверить работу через API

## Быстрый старт

### Используя Render Blueprint:

1. Зайти в Render Dashboard
2. New → Blueprint
3. Подключить GitHub repo
4. Render автоматически:
   - Создаст PostgreSQL
   - Задеплоит Backend
   - Задеплоит Frontend
   - Настроит переменные окружения

### Manual Steps:

1. Создать PostgreSQL database
2. Загрузить schema: `psql $DATABASE_URL < process.txt`
3. Создать Backend web service
4. Создать Frontend static site
5. Настроить environment variables
6. Дождаться деплоя

## Проверка после деплоя

```bash
# Health check
curl https://process-manager-backend.onrender.com/health

# Get types
curl https://process-manager-backend.onrender.com/api/v1/types

# Open frontend
open https://process-manager-frontend.onrender.com
```

## Troubleshooting

### Backend не стартует:
- Проверить DATABASE_URL в environment variables
- Проверить логи в Render Dashboard

### Frontend не подключается к Backend:
- Проверить VITE_API_URL указывает на правильный backend URL
- Проверить CORS настройки в backend
- Проверить FRONTEND_URL в backend environment variables

### Database connection error:
- Проверить что PostgreSQL создан и активен
- Проверить что таблицы созданы
- Проверить internal connection string

## Дальнейшие действия

1. ✅ Код готов к деплою
2. Создать GitHub репозиторий
3. Залить код на GitHub
4. Создать Blueprint на Render
5. Загрузить данные в PostgreSQL
6. Настроить environment variables
7. Проверить работу приложения

---

**Готово к деплою!** 🚀


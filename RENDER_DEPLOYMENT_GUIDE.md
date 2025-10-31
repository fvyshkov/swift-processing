# Render Deployment Guide

## Информация для деплоя

- **Email**: fvyshkov@gmail.com
- **API Key**: rnd_1jMp7KapvojqxZu2uJAAJdxJcqrM
- **Region**: Frankfurt (EU)

## Что готово к деплою ✅

### Backend (FastAPI)
- ✅ REST API с полным CRUD
- ✅ PostgreSQL подключение
- ✅ CORS настроен для production
- ✅ Health check endpoint
- ✅ Environment variables support
- ✅ Dockerfile готов
- ✅ requirements.txt

### Frontend (React + TypeScript)
- ✅ Build готов (Vite)
- ✅ Environment variables через VITE_API_URL
- ✅ Production-ready конфигурация
- ✅ Все компоненты работают

### Database
- ✅ init_database.sql с полными данными
- ✅ Схема с foreign keys
- ✅ 7 types, 13 states, 14 operations

## План деплоя на Render

### Вариант 1: Автоматический (через Blueprint) - РЕКОМЕНДУЕТСЯ

1. **Создать GitHub репозиторий**
   ```bash
   cd /Users/fvyshkov/PROJECTS/swift-processing
   
   # Если еще не создан репозиторий на GitHub:
   # Создайте его на github.com/new
   
   git add .
   git commit -m "Process Manager - ready for deployment"
   git remote add origin https://github.com/fvyshkov/swift-processing.git
   git push -u origin main
   ```

2. **Deploy через Render Dashboard**
   - Зайти на https://dashboard.render.com (войти через fvyshkov@gmail.com)
   - New → Blueprint
   - Connect GitHub repository: `fvyshkov/swift-processing`
   - Выбрать файл `render.yaml`
   - Apply Blueprint
   
3. **Render автоматически создаст:**
   - PostgreSQL database `process-manager-db`
   - Backend service `process-manager-backend`
   - Frontend static site `process-manager-frontend`

4. **Загрузить данные в PostgreSQL:**
   ```bash
   # Получить External Connection String из Render Dashboard
   # Database → process-manager-db → Connections
   
   psql "postgresql://user:password@hostname/database" < init_database.sql
   ```

### Вариант 2: Ручное создание

#### Шаг 1: Создать PostgreSQL
1. New → PostgreSQL
2. Name: `process-manager-db`
3. Database: `swift_processing`
4. Region: Frankfurt
5. Plan: Free
6. Create Database

После создания:
```bash
# Получить External Connection String
psql "CONNECTION_STRING" < init_database.sql
```

#### Шаг 2: Создать Backend
1. New → Web Service
2. Connect GitHub repository
3. Settings:
   - Name: `process-manager-backend`
   - Root Directory: `.`
   - Environment: Python
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. Environment Variables:
   ```
   DATABASE_URL = [Internal Database URL from step 1]
   PYTHON_VERSION = 3.9.18
   ```

5. Advanced:
   - Health Check Path: `/health`

#### Шаг 3: Создать Frontend
1. New → Static Site
2. Connect GitHub repository
3. Settings:
   - Name: `process-manager-frontend`
   - Root Directory: `.`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
   
4. Environment Variables:
   ```
   VITE_API_URL = [Backend URL from step 2]
   ```

#### Шаг 4: Обновить Backend CORS
В Backend environment variables добавить:
```
FRONTEND_URL = [Frontend URL from step 3]
```

## После деплоя

### URLs будут такие:
- **Backend**: `https://process-manager-backend.onrender.com`
- **Frontend**: `https://process-manager-frontend.onrender.com`
- **Database**: Internal URL (не публичный)

### Проверка:
```bash
# Health check
curl https://process-manager-backend.onrender.com/health

# API docs
open https://process-manager-backend.onrender.com/docs

# Frontend
open https://process-manager-frontend.onrender.com
```

## Важные файлы для деплоя

- ✅ `render.yaml` - Blueprint конфигурация
- ✅ `init_database.sql` - Инициализация БД с данными
- ✅ `backend/requirements.txt` - Python зависимости
- ✅ `backend/Dockerfile` - Docker образ (опционально)
- ✅ `frontend/package.json` - Node зависимости
- ✅ `frontend/vite.config.ts` - Build конфигурация

## Структура репозитория

```
swift-processing/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── render.yaml           ← Blueprint
├── init_database.sql     ← DB initialization
└── README.md
```

## Особенности Render Free Plan

### Ограничения:
- Backend засыпает после 15 минут без активности
- Cold start ~30 секунд при первом запросе
- PostgreSQL: 256MB RAM, 1GB storage
- 90 дней хранения данных

### Что работает отлично:
- Автоматический деплой при push в GitHub
- HTTPS из коробки
- Логи в реальном времени
- Environment variables
- Автоматические backups БД

## Следующий шаг

Выберите вариант деплоя:

### ВАРИАНТ A: Автоматический Blueprint (5 минут)
1. Создать GitHub репозиторий
2. Push код на GitHub
3. New Blueprint на Render
4. Загрузить данные в БД
5. Готово!

### ВАРИАНТ B: Ручное создание (15 минут)
1. Создать PostgreSQL
2. Создать Backend
3. Создать Frontend
4. Настроить Environment Variables
5. Загрузить данные
6. Готово!

## Нужна помощь с деплоем?

Напишите какой вариант предпочитаете, и я помогу с конкретными шагами!

---

**Код полностью готов к production деплою!** 🚀


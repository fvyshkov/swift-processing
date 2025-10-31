# Process Manager - Deploy на Render (5 минут)

## ✅ Готово к деплою

- Репозиторий: https://github.com/fvyshkov/swift-processing
- Email: fvyshkov@gmail.com
- Существующая БД: `swift-standalone-db` (можем использовать её!)

## Быстрый деплой (3 шага)

### Шаг 1: Создать Backend (2 минуты)

1. Открыть: https://dashboard.render.com/create?type=web
2. **Connect repository**: `fvyshkov/swift-processing`
3. **Настройки:**
   ```
   Name: process-manager-api
   Region: Frankfurt
   Branch: main
   Root Directory: . (оставить пустым)
   Runtime: Python 3
   
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   
   Instance Type: Free
   ```

4. **Advanced → Environment Variables:**
   ```
   DATABASE_URL = [скопировать Internal Database URL из swift-standalone-db]
   PYTHON_VERSION = 3.9.18
   ```

5. **Advanced → Health Check Path:**
   ```
   /health
   ```

6. **Create Web Service**

### Шаг 2: Создать Frontend (2 минуты)

1. Открыть: https://dashboard.render.com/create?type=static
2. **Connect repository**: `fvyshkov/swift-processing`  
3. **Настройки:**
   ```
   Name: process-manager-frontend
   Branch: main
   Root Directory: . (оставить пустым)
   
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

4. **Environment Variables:**
   ```
   VITE_API_URL = [URL бэкенда из шага 1]
   Например: https://process-manager-api.onrender.com
   ```

5. **Create Static Site**

### Шаг 3: Инициализировать БД (1 минута)

Использовать существующую БД `swift-standalone-db`:

```bash
# Получить External Connection String из:
# https://dashboard.render.com/d/dpg-d3ii7nogjchc73ech7pg-a

# Загрузить схему и данные
cd /Users/fvyshkov/PROJECTS/swift-processing
psql "postgresql://swift_user:PASSWORD@HOST/swift_standalone" < init_database.sql
```

**ИЛИ создать отдельную БД в `swift-standalone-db`:**

```sql
-- Подключиться к существующей БД
psql "CONNECTION_STRING_FROM_RENDER"

-- Создать отдельную схему для process manager
CREATE SCHEMA IF NOT EXISTS process_manager;
SET search_path TO process_manager;

-- Выполнить init_database.sql
\i init_database.sql
```

### Шаг 4: Обновить CORS в Backend

После создания Frontend, добавить в Backend environment variables:
```
FRONTEND_URL = [URL фронтенда]
Например: https://process-manager-frontend.onrender.com
```

## 🎯 Готово!

После деплоя приложение будет доступно по адресу Frontend URL.

### URLs:
- **Backend API**: https://process-manager-api.onrender.com
- **API Docs**: https://process-manager-api.onrender.com/docs
- **Frontend**: https://process-manager-frontend.onrender.com

### Проверка:
```bash
# Health check
curl https://process-manager-api.onrender.com/health

# Get types
curl https://process-manager-api.onrender.com/api/v1/types
```

## Альтернатива: Использовать новую БД

Если хотите отдельную БД для Process Manager:

1. Удалить старую `swift-standalone-db` (если не нужна)
2. Создать новую с именем `process-manager-db`
3. Следовать шагам выше

## Проблемы?

### Backend не стартует:
- Проверить DATABASE_URL в env vars
- Проверить логи: `render logs -s process-manager-api`

### Frontend не может подключиться:
- Проверить VITE_API_URL правильный
- Проверить FRONTEND_URL в backend env vars
- Проверить CORS в логах backend

### База данных не подключается:
- Использовать **Internal Database URL** (не External!)
- Формат: `postgresql://user:password@hostname/database`

---

**Время деплоя**: ~5-7 минут (первый build)
**Cold start**: ~30 секунд после периода неактивности


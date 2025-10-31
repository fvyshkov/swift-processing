# Render Deploy - Ручные шаги (из-за ограничений API)

## Почему вручную?

Render API не поддерживает создание Free tier сервисов программно. Но это быстро через Dashboard!

## ✅ Что уже есть:

- Репозиторий: https://github.com/fvyshkov/swift-processing ✅
- PostgreSQL БД: `swift-standalone-db` ✅ (можем использовать)
- Render CLI: установлен и авторизован ✅
- Все файлы готовы ✅

## 🎯 План деплоя (3 сервиса, 5 минут)

### Option A: Использовать существующую БД

**Плюс**: Быстрее, не нужно создавать новую БД
**Минус**: Shared БД с другим проектом

### Option B: Создать новую БД

**Плюс**: Изолированная БД
**Минус**: Нужно удалить старую (Free plan = 1 БД)

---

## Деплой - Пошагово

### 1️⃣ Backend API (Python FastAPI)

**URL для создания**: https://dashboard.render.com/create?type=web

**Настройки:**
| Поле | Значение |
|------|---------|
| **Name** | `process-manager-api` |
| **Region** | Frankfurt |
| **Branch** | main |
| **Root Directory** | `.` (пустое) |
| **Runtime** | Python 3 |
| **Build Command** | `cd backend && pip install -r requirements.txt` |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

**Environment Variables:**
```
DATABASE_URL = [Internal URL из swift-standalone-db или новой БД]
PYTHON_VERSION = 3.9.18
```

**Advanced Settings:**
- Health Check Path: `/health`
- Auto-Deploy: Yes

**Создать** → Дождаться первого деплоя (~5 минут)

---

### 2️⃣ Frontend (React Static Site)

**URL для создания**: https://dashboard.render.com/create?type=static

**Настройки:**
| Поле | Значение |
|------|---------|
| **Name** | `process-manager-frontend` |
| **Branch** | main |
| **Root Directory** | `.` (пустое) |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

**Environment Variables:**
```
VITE_API_URL = https://process-manager-api.onrender.com
```
*(Замените на реальный URL после создания backend)*

**Создать** → Дождаться build (~3 минуты)

---

### 3️⃣ Инициализация БД

**Вариант A: В существующей БД**

```bash
# 1. Получить External Connection String
# Dashboard → swift-standalone-db → Connect → External Connection String

# 2. Загрузить данные
cd /Users/fvyshkov/PROJECTS/swift-processing
psql "postgresql://swift_user:PASSWORD@HOST/swift_standalone" < init_database.sql

# 3. Проверить
psql "postgresql://..." -c "SELECT COUNT(*) FROM process_type;"
```

**Вариант B: Создать новую БД**

1. Удалить `swift-standalone-db` (если не нужна)
2. New → PostgreSQL:
   - Name: `process-manager-db`
   - Database: `swift_processing`
   - User: `swift_user`
   - Region: Frankfurt
   - Version: 15
3. Загрузить `init_database.sql` как в варианте A

---

### 4️⃣ Обновить CORS

После создания Frontend, вернуться в Backend:

1. Environment Variables → Add
2. ```
   FRONTEND_URL = https://process-manager-frontend.onrender.com
   ```
3. Save → Backend перезапустится

---

## ✅ Проверка после деплоя

### 1. Backend Health
```bash
curl https://process-manager-api.onrender.com/health
# Должно вернуть: {"status":"ok"}
```

### 2. API работает
```bash
curl https://process-manager-api.onrender.com/api/v1/types
# Должен вернуть JSON с типами
```

### 3. Frontend загружается
Открыть в браузере:
```
https://process-manager-frontend.onrender.com
```

Должны увидеть:
- Дерево типов слева
- Компактный интерфейс
- Работающие CRUD операции

---

## 🐛 Troubleshooting

### Backend returns 500
**Причина**: Нет подключения к БД
**Решение**: 
- Проверить DATABASE_URL
- Использовать Internal URL (не External!)
- Проверить что таблицы созданы

### Frontend белый экран
**Причина**: Не может подключиться к API
**Решение**:
- Проверить VITE_API_URL без `/api/v1` на конце
- Проверить CORS в backend
- F12 → Console для ошибок

### CORS errors
**Причина**: Frontend URL не в allowed origins
**Решение**:
- Добавить FRONTEND_URL в backend env vars
- Перезапустить backend

---

## 📝 Checklist

- [ ] Backend создан на Render
- [ ] Frontend создан на Render  
- [ ] DATABASE_URL настроен в Backend
- [ ] VITE_API_URL настроен в Frontend
- [ ] FRONTEND_URL настроен в Backend
- [ ] init_database.sql загружен в БД
- [ ] Health check работает
- [ ] API возвращает данные
- [ ] Frontend открывается

---

## ⏱️ Время деплоя

- **Backend первый build**: ~5 минут
- **Frontend первый build**: ~3 минуты
- **Инициализация БД**: ~30 секунд
- **Total**: ~8-10 минут

## 💰 Costs

**Free tier включает:**
- 750 часов Web Services
- 100GB bandwidth
- PostgreSQL 256MB RAM, 1GB storage
- **Стоимость: $0/месяц** 🎉

---

## 🚀 Следующий шаг

Выберите вариант:

1. **Dashboard создание** (рекомендую) - следуйте шагам 1️⃣2️⃣3️⃣4️⃣ выше
2. **Или скажите и я помогу** - пошагово с проверками

**Готовы начать?**


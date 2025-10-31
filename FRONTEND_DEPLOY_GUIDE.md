# Frontend Deployment на Render

## Что нужно для фронтенда:

### 1. Создать Static Site на Render

**URL**: https://dashboard.render.com/create?type=static

**Настройки:**

| Параметр | Значение |
|----------|---------|
| **Name** | `process-manager-frontend` |
| **Repository** | `fvyshkov/swift-processing` |
| **Branch** | `main` |
| **Root Directory** | `.` (оставить пустым) |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

### 2. Environment Variables

**ОБЯЗАТЕЛЬНО добавить:**

```
VITE_API_URL = https://swift-processing.onrender.com
```

⚠️ **Важно**: URL БЕЗ `/api/v1` на конце!

### 3. После создания

Frontend автоматически:
- Установит npm пакеты
- Соберет production build
- Задеплоит на CDN
- Будет доступен по URL типа: `https://process-manager-frontend.onrender.com`

## 📦 Что включено в build:

✅ React 18 + TypeScript
✅ Material-UI components
✅ Code editor с подсветкой
✅ Color picker
✅ Все компоненты работают
✅ Dark/Light theme
✅ Оптимизированный production build

## ⏱️ Время деплоя:

- **Первый build**: ~3-5 минут
- **Последующие**: ~2-3 минуты
- **Size**: ~500KB gzipped

## 🔧 Troubleshooting

### Build fails:

**Проблема**: `npm install` ошибка
**Решение**: Проверить что `frontend/package.json` есть в репо

**Проблема**: `vite build` ошибка  
**Решение**: Проверить TypeScript ошибки локально

### Frontend белый экран:

**Проблема**: Не может подключиться к API
**Решение**:
1. Проверить что VITE_API_URL правильный
2. Проверить CORS в backend
3. F12 → Console для ошибок

### CORS errors:

**Проблема**: Backend блокирует запросы
**Решение**: Добавить в Backend env vars:
```
FRONTEND_URL = https://process-manager-frontend.onrender.com
```

## 🎯 Checklist для Frontend:

- [ ] Static Site создан на Render
- [ ] Repository подключен
- [ ] Build Command правильный
- [ ] Publish Directory: `frontend/dist`
- [ ] VITE_API_URL настроен
- [ ] Build прошел успешно
- [ ] Frontend открывается
- [ ] API запросы работают

## 💡 После деплоя Frontend:

### Обновить Backend CORS:

1. Зайти в Backend service settings
2. Environment → Add Variable:
   ```
   FRONTEND_URL = https://process-manager-frontend.onrender.com
   ```
3. Save → Backend перезапустится

### Проверить работу:

```bash
# Открыть frontend
open https://process-manager-frontend.onrender.com

# Проверить что API работает
# F12 → Network → должны быть запросы к swift-processing.onrender.com
```

## 📋 Структура для фронтенда:

```
frontend/
├── src/
│   ├── components/     ✅ Все компоненты готовы
│   ├── hooks/          ✅ React Query hooks
│   ├── store/          ✅ Zustand stores
│   ├── api/            ✅ API client с env vars
│   ├── types/          ✅ TypeScript types
│   └── App.tsx         ✅ Main app
├── package.json        ✅ Dependencies
├── vite.config.ts      ✅ Build config
└── index.html          ✅ Entry point
```

Всё готово! 🚀


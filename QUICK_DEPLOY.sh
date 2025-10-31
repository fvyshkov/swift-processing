#!/bin/bash

echo "🚀 Process Manager - Quick Deploy Script"
echo ""
echo "Этот скрипт поможет задеплоить приложение на Render"
echo ""

# Get database connection string
echo "📊 Шаг 1: Получите Connection String из Render Dashboard"
echo "   https://dashboard.render.com/d/dpg-d3ii7nogjchc73ech7pg-a"
echo ""
read -p "Вставьте External Connection String: " DB_URL

if [ -z "$DB_URL" ]; then
    echo "❌ Connection string не указан!"
    exit 1
fi

echo ""
echo "📦 Шаг 2: Загружаем данные в БД..."
psql "$DB_URL" < init_database.sql

if [ $? -eq 0 ]; then
    echo "✅ База данных инициализирована!"
else
    echo "❌ Ошибка загрузки данных"
    exit 1
fi

echo ""
echo "✅ Готово!"
echo ""
echo "Теперь создайте сервисы через Render Dashboard:"
echo "1. Backend: https://dashboard.render.com/create?type=web"
echo "2. Frontend: https://dashboard.render.com/create?type=static"
echo ""
echo "Подробности в DEPLOY_STEPS.md"

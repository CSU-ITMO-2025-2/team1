#!/bin/bash
# Скрипт для полного сброса базы данных (удаление и пересоздание)
# ВНИМАНИЕ: Все данные будут удалены!
# Использование: ./scripts/reset_db.sh

set -e

echo "⚠️  ВНИМАНИЕ: Все данные в базе будут удалены!"
read -p "Вы уверены? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Операция отменена"
    exit 0
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден"
    exit 1
fi

# Загрузка переменных окружения
export $(cat .env | grep -v '^#' | xargs)

echo "🗑️  Удаление базы данных $POSTGRES_DB..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c \
    "DROP DATABASE IF EXISTS $POSTGRES_DB"

echo "🗄️  Создание базы данных $POSTGRES_DB..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c \
    "CREATE DATABASE $POSTGRES_DB"

echo "🔄 Применение миграций..."
alembic upgrade head

echo "✨ База данных успешно пересоздана!"


#!/bin/bash
# Скрипт инициализации базы данных для hr-assist
# Использование: ./scripts/init_db.sh

set -e

echo "🚀 Инициализация базы данных для hr-assist..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создайте его на основе .env.example"
    exit 1
fi

# Загрузка переменных окружения
export $(cat .env | grep -v '^#' | xargs)

echo "📦 Проверка подключения к PostgreSQL..."

# Ожидание готовности PostgreSQL
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c '\q' 2>/dev/null; then
        echo "✅ PostgreSQL готов к работе"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Ожидание PostgreSQL... попытка $attempt/$max_attempts"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Не удалось подключиться к PostgreSQL"
    exit 1
fi

# Создание базы данных если её нет
echo "🗄️  Создание базы данных $POSTGRES_DB..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c \
    "CREATE DATABASE $POSTGRES_DB"

echo "✅ База данных $POSTGRES_DB готова"

# Применение миграций
echo "🔄 Применение миграций Alembic..."
alembic upgrade head

echo "✨ База данных успешно инициализирована!"
echo ""
echo "📊 Информация о таблицах:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c '\dt'


#!/bin/bash
set -e  # Останавливаем скрипт при ошибке

echo "Применяем миграции Alembic..."
sleep 1
alembic upgrade head

echo "Запускаем Celery..."
exec "$@"
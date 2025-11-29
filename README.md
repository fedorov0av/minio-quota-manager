# Minio Size Control

## Сервис для очистки бакетов Minio

### Настройка

- Переименовать **example.env** в **.env**;
- Заполните переменные (см. таблицу ниже):

#### Основные настройки

Название | Тип | Описание | Пример значения
--------|-----|----------|---------------
`MINIO_URL` | `string` | URL MinIO | `"wsi-minio"` (prod), `"localhost"
`MINIO_ACCESS_KEY` | `string` | Access Key | `"changethis"`
`MINIO_SECRET_KEY` | `string` | Secret Key | `"changethis"`
`MINIO_API_PORT` | `number` | Порт MinIO API | `9000`
`PERCENT_DELETE_FILES` | `number` | Процент объектов в бакете для удаления. | `10`
`CLEAN_PERCENT` | `number` | Максимальный процент свободного пространства в бакете от квоты. | `10`
`CERT_CHECK` | `boolean` | Включить/выключить проверку сертификата при подключению к MinIO | `true`
`SECURE` | `boolean` | Включить/выключить защищенное подключение к MinIO | `true`
`TASK_DIR_TIME_MINUTES` | `number` | Период сканирования (мин.) для запуска задания на сканирование бакетов и директорий | `5`
`TASK_CLEAN_TIME_MINUTES` | `number` | Период сканирования (мин.) для запуска задания на очистку бакетов | `5`
`LOG_FILE` | `string` | Файл для журналирования событий | `"logs/celery.log"`

## Базы данных

Название | Тип | Описание | Пример значения
--------|-----|----------|---------------
`POSTGRES_SERVER` | `string` | URL PostgreSQL | `"msc-db"` (prod), `"localhost"` (dev)
`POSTGRES_PORT` | `number` | Порт PostgreSQL | `5432`
`POSTGRES_DB` | `string` | Имя БД | `"msc"`
`POSTGRES_USER` | `string` | Пользователь БД | `"postgres"`
`POSTGRES_PASSWORD` | `string` | Пароль БД | `"changethis"`
`REDIS_URL` | `string` | URL Redis | `"msc-redis"` (prod), `"localhost"` (dev)
`REDIS_PORT` | `number` | Порт Redis | `6379`


#### Внимание!

Минимальное рекомендуемое значение для **TASK_CLEAN_TIME_MINUTES**: **10** (минут). Так как, сортировка объектов по дате выполняется клиентской частью сервиса (не поддерживается MinIO нативно), что требует полного сканирования и обработки списка объектов. Частые выполнения этой операции создают значительную нагрузку.

Сервис работает только с бакетами, имеющими установленную квоту. Бакеты без квот не участвуют в процессе очистки.

### Запуск

#### 1. Docker compose:

Для запуска выполните команду:

```bash
docker compose up
```

Для остановки выполните команду:

```bash
docker compose down
```

#### 2. Локальный запуск:

Установите зависимости (для установки зависимостей понадобиться пакетный менеджер [uv](https://astral.sh/blog/uv-unified-python-packaging)):

```bash
uv sync
```

Для работы с базой данных необходимо применить миграцию **Alembic** из директории **backend/**:

```bash
alembic upgrade head
```

Запуск сервиса:

```bash
celery -A app.celery worker --loglevel=INFO -B --logfile=logs/celery.log --concurrency 1
```

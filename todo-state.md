# TODO STATE — marketplace-backend

## Последняя выполненная задача
Фаза 3 — S3 / MinIO (2026-03-26) ✓
- app/s3.py: boto3 клиент, ensure_bucket_exists, upload_file, get_public_url
- app/placeholder.py: генерация PNG без внешних зависимостей
- app/main.py: lifespan вызывает ensure_bucket_exists при старте

## Следующая задача
Фаза 4: Seed-скрипт — 100+ товаров, атрибуты, offers, загрузка placeholder PNG в MinIO

## Контекст
- стек: Python 3.12, FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, MinIO (boto3), JWT
- принятые решения:
  - Base из database.py
  - Alembic async через asyncio.run
  - stock хранится в Product, не в Offer
  - price_currency default = "RUB"
  - boto3 синхронный, вызовы через run_in_executor
  - ensure_bucket_exists — страховка при старте (minio-init делает то же в compose)
  - placeholder PNG генерируется без Pillow (чистый stdlib)
  - get_public_url строит URL локально без запроса к MinIO
- Dockerfile подключим к infra позже
- текущие проблемы: нет

## Лог сессий
- [2026-03-26] Фаза 1 — структура проекта, 1 итерация, проблем не было
- [2026-03-26] Фаза 2 — модели + alembic + migrate сервис, миграция прошла успешно
- [2026-03-26] Фаза 3 — s3.py + placeholder.py + lifespan, 1 итерация

# TODO STATE — marketplace-backend

## Последняя выполненная задача
Фаза 4 — Seed-скрипт (2026-03-26) — ожидает проверки
- app/seed.py: 10 продавцов, 120 товаров (4 категории × 30), атрибуты, offers, загрузка PNG в MinIO
- seed сервис добавлен в docker-compose (ручной запуск)
- защита от повторного запуска: проверяет COUNT(*) в sellers

## Следующая задача
Запустить seed: docker compose run --rm seed
Затем — Фаза 5: Публичное API

## Контекст
- стек: Python 3.12, FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, MinIO (boto3), JWT
- принятые решения:
  - Base из database.py
  - Alembic async через asyncio.run
  - stock хранится в Product, не в Offer
  - price_currency default = "RUB"
  - boto3 синхронный, вызовы через run_in_executor
  - placeholder PNG генерируется без Pillow (stdlib)
  - seed — только ручной запуск, не в автостарте compose
  - seed идемпотентен: повторный запуск ничего не делает (проверяет sellers)
- текущие проблемы: нет

## Лог сессий
- [2026-03-26] Фаза 1 — структура проекта, 1 итерация, проблем не было
- [2026-03-26] Фаза 2 — модели + alembic + migrate сервис, миграция прошла успешно
- [2026-03-26] Фаза 3 — s3.py + placeholder.py + lifespan, проверено: /health 200, MinIO ок
- [2026-03-26] Фаза 4 — seed.py + seed сервис в compose, ожидает проверки

# TODO STATE — marketplace-backend

## Последняя выполненная задача
Фаза 6 — Админское API (2026-03-26) ✓
- POST /v1/admin/auth/login → токен
- GET /v1/admin/products с токеном → 200, без токена → 401
- CRUD products, sellers, offers, image upload — реализованы

## Следующая задача
Фаза 7: Тесты и качество

## Контекст
- стек: Python 3.12, FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, MinIO (boto3), JWT
- принятые решения:
  - stock в Product, не в Offer
  - пагинация: offset/limit + has_more (без total)
  - has_more: limit+1 trick
  - nearest_delivery_date: correlated subquery
  - offers_sort в Python
  - image/thumbnail URL строится в роутере
  - boto3 через run_in_executor
  - make_thumbnail: PNG decode + nearest-neighbor; fallback → серая плашка
  - require_admin: HTTPBearer + jose.jwt.decode на роутере целиком
  - auth роутер подключён отдельно (без require_admin на /login)
  - PUT: partial update через model_dump(exclude_unset=True)
  - DELETE → 204, POST create → 201
- текущие проблемы: нет

## Лог сессий
- [2026-03-26] Фаза 1 — структура проекта, 1 итерация, проблем не было
- [2026-03-26] Фаза 2 — модели + alembic + migrate сервис, миграция прошла успешно
- [2026-03-26] Фаза 3 — s3.py + placeholder.py + lifespan, /health 200, MinIO ок
- [2026-03-26] Фаза 4 — seed.py, 120 товаров / 739 offers / изображения в MinIO ок
- [2026-03-26] Фаза 5 — публичное API, /products и /products/{id} проверены
- [2026-03-26] Фаза 6 — админское API, login/auth/CRUD проверены

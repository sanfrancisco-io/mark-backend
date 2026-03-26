# TODO STATE — marketplace-backend

## Последняя выполненная задача
Фаза 5 — Публичное API (2026-03-26) — ожидает проверки
- app/schemas.py: SellerShort, OfferOut, AttributeOut, ProductListItem, ProductListResponse, ProductDetail
- app/routers/public.py: GET /products (offset/limit + has_more), GET /products/{id} (offers_sort)
- app/main.py: подключён public_router с prefix /v1/public

## Следующая задача
Проверить в браузере: GET /v1/public/products, /v1/public/products/1
Затем — Фаза 6: Админское API

## Контекст
- стек: Python 3.12, FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, MinIO (boto3), JWT
- принятые решения:
  - stock хранится в Product, не в Offer
  - пагинация: offset/limit + has_more (без total) — infinite scroll на фронте
  - has_more: запрашиваем limit+1, если пришло больше limit → has_more=True
  - nearest_delivery_date: correlated subquery MIN(offers.delivery_date)
  - offers_sort: сортировка в Python после загрузки (не в SQL)
  - image/thumbnail URL строится через get_public_url(key), None если key=None
  - offers загружаются через selectinload + joinedload(seller)
- текущие проблемы: нет

## Лог сессий
- [2026-03-26] Фаза 1 — структура проекта, 1 итерация, проблем не было
- [2026-03-26] Фаза 2 — модели + alembic + migrate сервис, миграция прошла успешно
- [2026-03-26] Фаза 3 — s3.py + placeholder.py + lifespan, /health 200, MinIO ок
- [2026-03-26] Фаза 4 — seed.py, 120 товаров / 739 offers / изображения в MinIO ок
- [2026-03-26] Фаза 5 — публичное API, ожидает проверки

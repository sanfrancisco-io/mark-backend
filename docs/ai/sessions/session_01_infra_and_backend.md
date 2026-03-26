# Session 01 — Infra & Backend: Фазы 1–5

**Дата:** 2026-03-26
**Модель:** claude-sonnet-4-6
**Охват:** Фазы 1–5 marketplace-backend

---

## Фаза 1 — Настройка проекта

**Что делали:**
Создали структуру проекта с нуля: папки `app/`, `app/routers/`, `migrations/`, `tests/`, `docs/ai/sessions/`. Написали `requirements.txt`, `.env.example`, `app/database.py`, `app/main.py` (минимальный FastAPI app с CORS и `/health`), `Dockerfile`.

**Итераций:** 1

**Проблемы:** нет

**Решения:**
- `Base` (DeclarativeBase) живёт в `database.py`, а не в отдельном `base.py` — меньше файлов, модели импортируют оттуда
- `async_sessionmaker` + `AsyncSession` вместо устаревшего `sessionmaker`
- CORS настроен сразу под `localhost:3000` (будущий фронт)
- Dockerfile как placeholder — подключение к infra отложено до финала

---

## Фаза 2 — Модели и миграции

**Что делали:**
Написали `app/models.py` (4 модели), настроили Alembic с async-поддержкой, написали первую миграцию вручную, добавили сервис `migrate` в `docker-compose.yml`. Миграция применена успешно.

**Итераций:** 1 (модели скорректированы в процессе обсуждения перед написанием кода)

**Проблемы:** нет

**Решения и почему:**
- **stock в Product, не в Offer** — остаток это свойство товара, а не конкретного предложения продавца
- **price в Offer** — каждый продавец предлагает свою цену; `price_amount` (Numeric 12,2) + `price_currency` (Text) и в Product, и в Offer
- **rating в Seller** — Numeric(2,1), значения 0.0–9.9
- **updated_at** — `server_default=func.now()` + `onupdate=func.now()` на уровне SQLAlchemy
- **Alembic async** — `env.py` использует `asyncio.run` + `create_async_engine` с asyncpg URL напрямую; DATABASE_URL берётся из env var, не из `alembic.ini`
- **Миграция написана вручную** — `alembic revision --autogenerate` требует живой БД, а на этапе написания кода она недоступна
- **Сервис migrate в compose** — `restart: "no"`, `depends_on: postgres: condition: service_healthy`; применяется через `docker compose run --rm migrate`

---

## Фаза 3 — S3 / MinIO

**Что делали:**
Написали `app/s3.py` (клиент MinIO), `app/placeholder.py` (генератор PNG), обновили `app/main.py` на `lifespan` с вызовом `ensure_bucket_exists`.

**Итераций:** 1

**Проблемы:** нет

**Решения и почему:**
- **boto3 синхронный + run_in_executor** — boto3 не поддерживает async нативно; оборачиваем через `asyncio.get_event_loop().run_in_executor` чтобы не блокировать event loop FastAPI
- **ensure_bucket_exists при старте** — страховка на случай если `minio-init` (compose) не отработал или backend запускается без docker compose; сначала `head_bucket`, создаём только если нет
- **get_public_url без сетевого запроса** — строим URL локально: `{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{key}`; быстро и без зависимости от MinIO при сериализации
- **placeholder PNG без Pillow** — генерируем минимальный валидный PNG через stdlib (`struct`, `zlib`); не добавляем тяжёлую зависимость ради seed-данных
- **lifespan вместо on_event** — `@app.on_event("startup")` deprecated в FastAPI, используем `@asynccontextmanager lifespan`

---

## Фаза 4 — Seed-скрипт

**Что делали:**
Написали `app/seed.py`: 10 продавцов, 120 товаров по 4 категориям (электроника, одежда, спорт, дом и быт), атрибуты специфичные для категории, 2–10 offers на товар, загрузка placeholder PNG в MinIO. Добавили сервис `seed` в `docker-compose.yml`.

**Итераций:** 1

**Результат проверки:** 120 товаров, 739 offers, изображения доступны (GET `product_0000.png` → 200 OK)

**Проблемы:** нет

**Решения и почему:**
- **Идемпотентность** — `COUNT(*) FROM sellers` при старте; повторный запуск ничего не делает; важно чтобы случайный `docker compose run --rm seed` не задублировал данные
- **Только ручной запуск** — seed не в автостарте compose; должен запускаться один раз намеренно
- **Категории с разными атрибутами** — у электроники "Гарантия"/"Интерфейс", у одежды "Размер"/"Сезон", у спорта "Вес"; реалистичнее чем одинаковый набор для всех
- **Цвет плашки по категории** — steel blue/orchid/sea green/peru; быстро визуально различать категории в MinIO и в браузере
- **Диапазоны цен по категории** — электроника 1500–80000, одежда 500–15000 и т.д.; цены правдоподобные
- **offer.price = product.price ± 20%** — продавцы конкурируют в разумном диапазоне от базовой цены товара

---

## Фаза 5 — Публичное API

**Что делали:**
Написали `app/schemas.py` (6 Pydantic-схем), `app/routers/public.py` (два эндпоинта), подключили роутер в `main.py`.

**Итераций:** 1 (схема ответа списка уточнена в обсуждении: убрали `total`, добавили `has_more`)

**Проблемы:** нет

**Решения и почему:**
- **has_more вместо total** — фронт использует infinite scroll, `total` не нужен; реализация: запрашиваем `limit + 1` строк, если вернулось больше `limit` → `has_more=True`, отдаём первые `limit`
- **nearest_delivery_date через correlated subquery** — `MIN(offers.delivery_date)` прямо в SELECT одним запросом, без отдельного запроса или Python-агрегации
- **offers_sort в Python, не в SQL** — offers уже загружены через `selectinload`; сортировка в Python дешевле чем переписывать запрос под каждый вариант; кол-во offers на товар небольшое
- **selectinload + joinedload(seller)** — `selectinload(Product.offers).joinedload(Offer.seller)` даёт два запроса вместо N+1; joinedload для seller внутри уже загруженных offers
- **Literal["price", "delivery_date"]** — FastAPI автоматически валидирует параметр и отдаёт 422 при неверном значении; не нужен ручной if/raise
- **image/thumbnail URL в роутере, не в схеме** — `get_public_url(key) if key else None` вызывается при построении ответа; схемы остаются чистыми Pydantic-моделями без зависимости от s3.py

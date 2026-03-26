# TODO — marketplace-backend

## Стек и решения
- Python 3.12
- FastAPI
- SQLAlchemy 2.x async + asyncpg
- Alembic (миграции)
- MinIO через boto3
- Принятые решения: (заполни после первой сессии)

## Структура проекта
```
marketplace-backend/
  app/
    models.py       ← Product, Seller, Offer, ProductAttribute
    database.py     ← async engine + AsyncSession
    s3.py           ← клиент MinIO
    seed.py         ← тестовые данные
    routers/
      public.py     ← /v1/public/*
      admin.py      ← /v1/admin/*
      auth.py       ← /v1/admin/auth/login
    main.py         ← FastAPI app, CORS, роуты
  migrations/
    versions/
  tests/
    test_smoke.py
  docs/ai/
    AI_WORKFLOW.md
    sessions/
  Dockerfile
  requirements.txt
  .env.example
```

## Переменные окружения (.env.example)
```
DATABASE_URL=postgresql+asyncpg://marketplace:secret@postgres:5432/marketplace
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=products
MINIO_PUBLIC_URL=http://localhost:9000
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
JWT_SECRET=changeme
```

---

## Фаза 1 — Настройка проекта ✓

- [x] Создать структуру: app/, migrations/, tests/, docs/ai/
- [x] Настроить requirements.txt (fastapi, sqlalchemy, asyncpg, alembic, boto3, python-jose, python-multipart)
- [x] Создать app/database.py — async engine + AsyncSession
- [x] Создать .env.example со всеми переменными
- [x] Создать Dockerfile для backend

## Фаза 2 — Модели и миграции ✓

- [x] Создать app/models.py — классы Product, ProductAttribute, Seller, Offer
- [x] Инициализировать Alembic (alembic init migrations)
- [x] Написать первую миграцию: создать все 4 таблицы
- [x] Применить миграцию: alembic upgrade head (через docker-compose migrate)
- [x] Проверить: подключиться к postgres, увидеть таблицы

## Фаза 3 — S3 / MinIO ✓

- [x] Создать app/s3.py — клиент MinIO через boto3
- [x] Настроить публичный bucket при старте приложения
- [x] Реализовать функции: upload_file, get_public_url
- [ ] Добавить в seed загрузку placeholder-изображений в MinIO (Фаза 4)
- [ ] Проверить: загруженный файл доступен по URL в браузере (Фаза 4)

## Фаза 4 — Seed-скрипт

- [ ] Создать app/seed.py — генерация тестовых данных
- [ ] 100+ товаров с разными названиями, ценами, остатками
- [ ] 2-6 атрибутов на товар (Цвет, Размер, Материал и т.д.)
- [ ] 2-10 offers на товар с разными продавцами
- [ ] Даты доставки — текущая неделя (today + 0..6 дней)
- [ ] Запустить seed, проверить данные в базе

## Фаза 5 — Публичное API

- [ ] GET /v1/public/products — список с offset/limit пагинацией
- [ ] Вычислять nearest_delivery_date = min(offers.delivery_date)
- [ ] GET /v1/public/products/{id} — атрибуты + offers
- [ ] Параметр ?offers_sort=price|delivery_date
- [ ] Настроить CORS (origins: http://localhost:3000)
- [ ] Проверить в браузере: localhost:8000/v1/public/products

## Фаза 6 — Админское API

- [ ] POST /v1/admin/auth/login — возвращает JWT bearer-токен
- [ ] Middleware: проверка токена для всех /v1/admin/* роутов
- [ ] CRUD /v1/admin/products (list, create, get, update, delete)
- [ ] POST /v1/admin/products/{id}/image — загрузка multipart/form-data в MinIO
- [ ] GET+POST /v1/admin/sellers
- [ ] CRUD /v1/admin/products/{id}/offers + PUT/DELETE /v1/admin/offers/{id}

## Фаза 7 — Тесты и качество

- [ ] Smoke-тест: GET /v1/public/products → 200
- [ ] Smoke-тест: GET /v1/public/products/{id} → 200 и 404
- [ ] Smoke-тест: POST /v1/admin/auth/login → верный пароль 200, неверный 401
- [ ] Проверить все HTTP статусы: 400, 401, 404, 422
- [ ] Запустить pytest — все тесты зелёные

## Фаза 8 — AI документация

- [ ] Создать docs/ai/AI_WORKFLOW.md — инструменты, итерации, решения
- [ ] Сохранять каждую сессию в docs/ai/sessions/session_XX_name.md
- [ ] Создать docs/ai/PROMPTS.md — ключевые промпты (опционально)

---

## Лог сессий
- (заполняй после каждой сессии)
- [дата] Фаза X — что сделали, сколько итераций, что сломалось

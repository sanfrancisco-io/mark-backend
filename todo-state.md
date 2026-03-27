# TODO STATE — marketplace-backend

## Последняя выполненная задача
Фаза 7 + Фаза 8 — Тесты и AI документация (2026-03-26) ✓
- 26 тестов: 10 публичных, 6 auth, 9 admin + conftest
- Исправлен asyncpg NullPool + dependency_overrides
- docs/ai/sessions/session_02_tests.md — лог с разбором проблем
- docs/ai/AI_WORKFLOW.md и session_01 — написаны ранее

## Следующая задача
Все фазы выполнены. Backend готов.

## Контекст
- стек: Python 3.12, FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, MinIO (boto3), JWT
- принятые решения:
  - stock в Product, не в Offer
  - пагинация: offset/limit + has_more (без total)
  - offers_sort в Python после загрузки
  - image/thumbnail URL строится в роутере через get_public_url
  - boto3 через run_in_executor
  - make_thumbnail: PNG decode + nearest-neighbor (stdlib), fallback → серая плашка
  - require_admin: HTTPBearer + jose.jwt.decode на роутере целиком
  - auth роутер отдельно от admin (без require_admin на /login)
  - PUT: partial update через model_dump(exclude_unset=True)
  - DELETE → 204, POST create → 201
  - тесты: NullPool + app.dependency_overrides[get_db] для изоляции
  - pytestmark = pytest.mark.asyncio на уровне модуля (работает в strict и auto)
  - @pytest_asyncio.fixture для async-фикстур в conftest
- текущие проблемы: нет

## Лог сессий
- [2026-03-26] Фаза 1 — структура проекта, 1 итерация
- [2026-03-26] Фаза 2 — модели + alembic + migrate, миграция прошла
- [2026-03-26] Фаза 3 — s3.py + placeholder.py + lifespan
- [2026-03-26] Фаза 4 — seed.py, 120 товаров / 739 offers / MinIO ок
- [2026-03-26] Фаза 5 — публичное API, проверено
- [2026-03-26] Фаза 6 — админское API, login/auth/CRUD проверены
- [2026-03-26] Фаза 7 — 26 тестов, 3 итерации (asyncio → NullPool), 26 passed
- [2026-03-26] Фаза 8 — AI_WORKFLOW.md, session_01, session_02

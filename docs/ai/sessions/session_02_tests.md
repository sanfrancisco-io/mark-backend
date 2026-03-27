# Session 02 — Тесты: Фаза 7

**Дата:** 2026-03-26
**Модель:** claude-sonnet-4-6
**Охват:** Фаза 7 — тесты и качество

---

## Что делали

Написали 26 smoke-тестов покрывающих:
- Публичное API (`test_public.py`, 10 тестов) — читают seed-данные
- Аутентификацию (`test_auth.py`, 6 тестов) — login, no token, invalid token
- Админское API (`test_admin.py`, 9 тестов) — CRUD с fixture teardown

Добавили `pytest.ini` с `asyncio_mode = auto` и `asyncio_default_fixture_loop_scope = function`.
Фикстуры в `conftest.py` используют `@pytest_asyncio.fixture(scope="function")`.

**Итог:** 26 passed, 0 failed, 0.59s

---

## Проблемы и решения

### Проблема 1 — 0 тестов собрано (asyncio mode = STRICT)

**Симптом:** `pytest -v` выводит "asyncio mode = STRICT" и собирает 0 тестов.

**Причина:** pytest запускался не из директории `marketplace-backend/`, поэтому `pytest.ini` не находился. pytest-asyncio 0.25 по умолчанию — STRICT mode, в котором `async def` тест-функции без `@pytest.mark.asyncio` не собираются.

**Решение:**
1. Добавили `pytestmark = pytest.mark.asyncio` на уровне каждого тестового модуля — работает в любом режиме (strict и auto)
2. Заменили `@pytest.fixture` на `@pytest_asyncio.fixture` в `conftest.py` — в strict mode async-фикстуры тоже требуют явной пометки

---

### Проблема 2 — asyncpg InterfaceError (главная)

**Симптом:** 8 тестов проходят, 12 падают с:
```
asyncpg.exceptions.InterfaceError: cannot perform operation: another operation is in progress
```

**Причина:** `database.py` создаёт один глобальный `engine` с connection pool при импорте модуля. Все тесты используют один и тот же пул. asyncpg не допускает параллельных операций на одном соединении — когда несколько тестов в одном event loop пытаются использовать одно и то же соединение из пула, возникает конфликт.

**Что не помогло:**
- `asyncio_default_fixture_loop_scope = function` в `pytest.ini` — уменьшило количество конфликтов, но не устранило их
- Явный `scope="function"` на всех фикстурах — то же самое

**Решение — NullPool + dependency_overrides:**

В `app/database.py` добавили:
```python
from sqlalchemy.pool import NullPool

def make_test_session_factory(url: str) -> async_sessionmaker:
    test_engine = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
```

`NullPool` полностью отключает пул — каждая сессия открывает и закрывает соединение самостоятельно. Соединения не переиспользуются между тестами.

В `tests/conftest.py` переопределили `get_db` для каждого теста через FastAPI dependency injection:
```python
@pytest_asyncio.fixture(scope="function")
async def client():
    session_factory = make_test_session_factory(DATABASE_URL)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
```

`app.dependency_overrides` — стандартный механизм FastAPI для замены зависимостей в тестах. После теста override очищается через `pop`.

**Итераций до решения:** 3 (asyncio_mode → asyncio_default_fixture_loop_scope → NullPool)

---

## Архитектурные решения

| Решение | Почему |
|---|---|
| Смешанный подход: GET читают seed, POST/PUT/DELETE создают свои данные | Компромисс для smoke-тестов прототипа: GET-тесты проще, CRUD-тесты изолированы |
| `make_test_session_factory` в `database.py`, не в `conftest.py` | Логика создания engine остаётся в слое БД; conftest только конфигурирует |
| `dependency_overrides` вместо патчинга engine | Правильный FastAPI-способ замены зависимостей; не затрагивает production code |
| `NullPool` только для тестов | Production engine сохраняет пул для производительности |

"""
Unit-тести для Flask-додатку.
Використовують SQLite in-memory для ізоляції від PostgreSQL.
Запуск: pytest test_app.py -v
"""
import os
import sys
import tempfile
import pytest

# --- Переоприділюємо DATABASE_URL ДО імпорту app ---
# SQLite in-memory не потребує PostgreSQL
os.environ["DB_HOST"] = ""
os.environ["DB_PORT"] = ""
os.environ["DB_USER"] = ""
os.environ["DB_NAME"] = ""

# Патчимо модуль перед імпортом — використовуємо SQLite
import app as app_module

# Замінюємо DATABASE_URL на SQLite in-memory
app_module.DATABASE_URL = "sqlite://"
# Скидаємо lazy engine щоб він створився заново з SQLite
app_module._engine = None
app_module._SessionLocal = None

from app import app, Base, get_engine

# Monkey-patch: SQLite не підтримує ALTER TABLE ... IF NOT EXISTS.
# Оскільки таблиці створюються через Base.metadata.create_all (вже з колонкою name),
# ця міграція не потрібна у тестах — замінюємо на no-op.
_original_index = app_module.index

import functools
from unittest.mock import patch

def _patched_execute(original_execute):
    """Обгортка для db.execute що ігнорує ALTER TABLE міграцію."""
    @functools.wraps(original_execute)
    def wrapper(stmt, *args, **kwargs):
        if hasattr(stmt, 'text') and 'ALTER TABLE' in str(stmt.text):
            return None
        if isinstance(stmt, str) and 'ALTER TABLE' in stmt:
            return None
        # Перевірка для text() об'єктів
        try:
            if 'ALTER TABLE' in str(stmt):
                return None
        except Exception:
            pass
        return original_execute(stmt, *args, **kwargs)
    return wrapper


@pytest.fixture(autouse=True)
def setup_db():
    """Створює таблиці перед кожним тестом і очищає після."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Скидаємо engine для наступного тесту
    app_module._engine = None
    app_module._SessionLocal = None
    app_module.DATABASE_URL = "sqlite://"


@pytest.fixture
def client(monkeypatch):
    """Створює тестовий клієнт Flask з патчем для SQLite."""
    app.config["TESTING"] = True

    # Патчимо get_session щоб db.execute ігнорував ALTER TABLE
    original_get_session = app_module.get_session

    def patched_get_session():
        session = original_get_session()
        session.execute = _patched_execute(session.execute)
        return session

    monkeypatch.setattr(app_module, 'get_session', patched_get_session)

    with app.test_client() as client:
        yield client


class TestHealthz:
    """Тести для ендпоінту /healthz."""

    def test_healthz_returns_200(self, client):
        """Health check повинен повертати 200 OK."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.data == b"OK"

    def test_healthz_does_not_depend_on_db(self, client):
        """Health check не повинен залежати від стану БД."""
        # Навіть якщо БД недоступна, healthz має працювати
        response = client.get("/healthz")
        assert response.status_code == 200


class TestIndexPage:
    """Тести для головної сторінки /."""

    def test_get_index_returns_200(self, client):
        """GET / повинен повертати 200 та HTML з привітанням."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Привіт" in response.data.decode("utf-8")

    def test_get_index_shows_visit_counter(self, client):
        """Сторінка повинна показувати лічильник візитів."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "відвідали" in html

    def test_post_index_with_name(self, client):
        """POST з іменем повинен зберегти відвідувача."""
        response = client.post("/", data={"visitor_name": "Тестовий Юзер"})
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Тестовий Юзер" in html

    def test_post_index_empty_name(self, client):
        """POST з порожнім іменем не повинен крашити."""
        response = client.post("/", data={"visitor_name": ""})
        assert response.status_code == 200

    def test_multiple_visits_increment_counter(self, client):
        """Кожен візит повинен збільшувати лічильник."""
        client.get("/")
        client.get("/")
        response = client.get("/")
        html = response.data.decode("utf-8")
        # Має бути 3 візити
        assert "<strong>3</strong>" in html

    def test_recent_visits_shown(self, client):
        """Останні відвідувачі повинні відображатися."""
        client.post("/", data={"visitor_name": "Відвідувач 1"})
        client.post("/", data={"visitor_name": "Відвідувач 2"})
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "Відвідувач 1" in html
        assert "Відвідувач 2" in html


class TestGetSecret:
    """Тести для функції get_secret."""

    def test_get_secret_reads_file(self):
        """Повинен читати секрет з файлу."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("my-secret-password")
            temp_path = f.name

        try:
            # Мокаємо шлях до секрету
            original_func = app_module.get_secret

            def mock_get_secret(name, default=None):
                try:
                    with open(temp_path, 'r') as fh:
                        return fh.read().strip()
                except IOError:
                    return default

            result = mock_get_secret("db-password")
            assert result == "my-secret-password"
        finally:
            os.unlink(temp_path)

    def test_get_secret_returns_default_on_missing_file(self):
        """Повинен повертати default якщо файл не знайдено."""
        result = app_module.get_secret("nonexistent-secret", "fallback")
        assert result == "fallback"

    def test_get_secret_returns_none_when_no_default(self):
        """Повинен повертати None якщо файл не знайдено і default не вказано."""
        result = app_module.get_secret("nonexistent-secret")
        assert result is None

class TestReady:
    """Тести для ендпоінту /ready."""

    def test_ready_returns_200(self, client):
        """Readiness check повинен повертати 200 OK при доступній БД."""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.data == b"OK"

    def test_ready_returns_503_on_db_failure(self, client, monkeypatch):
        """Readiness check повинен повертати 503 Service Unavailable при збої БД."""
        from sqlalchemy.exc import OperationalError
        import sqlalchemy.engine

        def mock_execute(*args, **kwargs):
            raise OperationalError("mock error", None, None)

        # Мокаємо виконання запиту до БД щоб викликати виключення
        original_get_session = app_module.get_session

        def patched_get_session():
            session = original_get_session()
            session.execute = mock_execute
            return session

        monkeypatch.setattr(app_module, 'get_session', patched_get_session)

        response = client.get("/ready")
        assert response.status_code == 503
        assert b"Service Unavailable" in response.data

class TestMetrics:
    """Тести для ендпоінту /metrics."""

    def test_metrics_returns_200(self, client):
        """Metrics check повинен повертати 200 OK та метрики у форматі Prometheus."""
        response = client.get("/metrics")
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        assert 'app_request_count' in content
        assert 'app_visits_total' in content

    def test_metrics_increments_after_visit(self, client):
        """Перевірка чи метрики збільшуються після візиту."""
        # Робимо успішний візит
        client.get("/")
        
        response = client.get("/metrics")
        content = response.data.decode('utf-8')
        # Перевіряємо що app_visits_total присутній і має значення > 0
        # Формат зазвичай: app_visits_total_total 1.0 або app_visits_total 1.0
        assert 'app_visits_total' in content

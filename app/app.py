import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, request

# --- Функція для читання секрету з файлу ---
def get_secret(secret_name, default_value=None):
    """Читає секрет з файлу, змонтованого CSI драйвером."""
    secret_path = f"/secrets/{secret_name}"
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except IOError:
        print(f"Warning: Secret file not found at {secret_path}. Using default value.")
        return default_value

# --- Налаштування бази даних ---
DB_USER = os.environ.get("DB_USER", "app_user")
# Читаємо пароль з файлу, а не зі змінної оточення
DB_PASS = get_secret("db-password", "default_password")
DB_NAME = os.environ.get("DB_NAME", "app_db")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")  # Підключення через Cloud SQL Proxy
DB_PORT = os.environ.get("DB_PORT", "5432")

# Рядок підключення для PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Lazy ініціалізація БД ---
# engine та SessionLocal створюються при першому звернені, а не при старті Gunicorn.
# Це виключає краш Gunicorn якщо cloud-sql-proxy ще не готовий.
_engine = None
_SessionLocal = None
Base = declarative_base()

def get_engine():
    """Повертає (або lazy-створює) SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine

def get_session():
    """Повертає (або lazy-створює) SQLAlchemy session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()

# --- Модель SQLAlchemy ---
class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, index=True)

# --- Ініціалізація Flask ---
app = Flask(__name__)

# --- Логіка додатку ---
@app.route('/')
def index():
    """
    При кожному візиті:
    1. Реєструє візит у базі даних.
    2. Підраховує загальну кількість візитів.
    3. Повертає вітальне повідомлення з лічильником.
    """
    db = get_session()
    try:
        # Створюємо таблиці якщо їх ще немає (перший запит)
        Base.metadata.create_all(bind=get_engine())

        # Отримання IP-адреси. Враховуємо, що додаток за проксі (GKE Ingress).
        if request.headers.getlist("X-Forwarded-For"):
            ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_addr = request.remote_addr

        # Створення нового запису про візит
        new_visit = Visit(ip_address=ip_addr)
        db.add(new_visit)
        db.commit()

        # Підрахунок загальної кількості візитів
        total_visits = db.query(func.count(Visit.id)).scalar()

        return f"<h1>Hello! This site has been visited {total_visits} times.</h1>"

    except Exception as e:
        # У випадку помилки підключення до БД, повертаємо HTTP 503
        db.rollback()
        print(f"Database error: {e}")
        return f"<h1>Service temporarily unavailable.</h1><p>Database error: {e}</p>", 503
    finally:
        db.close()

@app.route('/healthz')
def healthz():
    """
    Ендпоінт для перевірки стану (Health Check).
    Завжди повертає 200 OK — додаток живий якщо gunicorn запущений.
    Перевірка БД тут НЕ виконується щоб health check не залежав від стану БД.
    """
    return "OK", 200

if __name__ == '__main__':
    # Запускаємо додаток (для локальної розробки)
    app.run(host='0.0.0.0', port=8080)

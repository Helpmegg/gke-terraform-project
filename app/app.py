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
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1") # Підключення через Cloud SQL Proxy
DB_PORT = os.environ.get("DB_PORT", "5432")

# Рядок підключення для PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    db = SessionLocal()
    try:
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
        # У випадку помилки підключення до БД, повертаємо повідомлення про помилку
        db.rollback()
        return f"<h1>Error connecting to the database:</h1><p>{e}</p>", 500
    finally:
        db.close()

@app.route('/healthz')
def healthz():
    """Ендпоінт для перевірки стану (Health Check)."""
    return "OK", 200

def create_tables():
    """Створює таблиці в базі даних, якщо їх ще немає."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == '__main__':
    # Створюємо таблиці при першому запуску
    create_tables()
    # Запускаємо додаток (для локальної розробки)
    app.run(host='0.0.0.0', port=8080)

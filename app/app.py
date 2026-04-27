import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, request, render_template_string

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
    name = Column(String(255), nullable=True)

# --- Ініціалізація Flask ---
app = Flask(__name__)

# --- Логіка додатку ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вітаємо на сайті</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 600px;
            padding: 2rem;
            box-sizing: border-box;
        }
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
            animation: fadeIn 0.8s ease-out;
            box-sizing: border-box;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-weight: 800;
            font-size: 2.5rem;
            margin-top: 0;
            margin-bottom: 0.5rem;
            background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .counter {
            font-size: 1.2rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 2rem;
        }
        input[type="text"] {
            width: 100%;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--glass-border);
            background: rgba(0, 0, 0, 0.2);
            color: var(--text-primary);
            font-size: 1rem;
            font-family: inherit;
            box-sizing: border-box;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
        }
        button {
            width: 100%;
            padding: 1rem;
            border-radius: 12px;
            border: none;
            background: var(--accent);
            color: #0f172a;
            font-weight: 600;
            font-size: 1rem;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        button:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
        }
        .visitor-list {
            text-align: left;
            margin-top: 2rem;
        }
        .visitor-list h3 {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }
        .visitor-item {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--glass-border);
        }
        .visitor-name {
            font-weight: 600;
        }
        .visitor-meta {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        .anon {
            font-style: italic;
            color: var(--text-secondary);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-panel">
            <h1>Привіт! 👋</h1>
            <div class="counter">Цей сайт відвідали <strong>{{ total_visits }}</strong> разів.</div>
            
            <div class="form-group">
                <form method="POST">
                    <input type="text" name="visitor_name" placeholder="Введіть ваше ім'я..." required>
                    <button type="submit">Залишити слід</button>
                </form>
            </div>

            {% if recent_visits %}
            <div class="visitor-list">
                <h3>Останні відвідувачі:</h3>
                {% for visit in recent_visits %}
                <div class="visitor-item">
                    <div class="visitor-name">
                        {% if visit.name %}{{ visit.name }}{% else %}<span class="anon">Анонім</span>{% endif %}
                    </div>
                    <div class="visitor-meta">
                        {{ visit.ip_address }} &bull; {{ visit.timestamp.strftime('%H:%M, %d.%m.%Y') }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    При кожному візиті:
    1. Реєструє візит у базі даних (з іменем або без).
    2. Підраховує загальну кількість візитів.
    3. Повертає вітальне повідомлення з формою та лічильником.
    """
    db = get_session()
    try:
        # Створюємо таблиці якщо їх ще немає (перший запит)
        Base.metadata.create_all(bind=get_engine())
        
        # Міграція: додаємо колонку name, якщо її не існує
        db.execute(text("ALTER TABLE visits ADD COLUMN IF NOT EXISTS name VARCHAR(255);"))
        db.commit()

        # Отримання IP-адреси. Враховуємо, що додаток за проксі (GKE Ingress).
        if request.headers.getlist("X-Forwarded-For"):
            ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_addr = request.remote_addr

        # Отримання імені користувача з форми
        user_name = None
        if request.method == 'POST':
            user_name = request.form.get('visitor_name', '').strip()
            if not user_name:
                user_name = None

        # Створення нового запису про візит
        new_visit = Visit(ip_address=ip_addr, name=user_name)
        db.add(new_visit)
        db.commit()

        # Підрахунок загальної кількості візитів
        total_visits = db.query(func.count(Visit.id)).scalar()
        
        # Отримання 5 останніх візитів для відображення
        recent_visits = db.query(Visit).order_by(Visit.timestamp.desc()).limit(5).all()

        return render_template_string(HTML_TEMPLATE, total_visits=total_visits, recent_visits=recent_visits)

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

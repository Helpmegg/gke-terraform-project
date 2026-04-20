# --- Етап 1: Збірка (Builder) ---
FROM python:3.11-slim as builder

WORKDIR /app

# Встановлюємо системні залежності для компіляції (за потреби)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# --- Етап 2: Фінальний образ (Final) ---
FROM python:3.11-slim

WORKDIR /app

# Встановлюємо runtime залежності
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY app.py .

ENV PATH="/opt/venv/bin:$PATH"

# Створення непривілейованого користувача для безпеки (Best Practice)
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -s /bin/sh -m appuser
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]

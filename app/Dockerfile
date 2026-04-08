# --- Етап 1: Збірка (Builder) ---
FROM python:3.11-alpine as builder

WORKDIR /app

# Встановлюємо системні залежності для компіляції (за потреби)
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# --- Етап 2: Фінальний образ (Final) ---
FROM python:3.11-alpine

WORKDIR /app

# Встановлюємо runtime залежності
RUN apk add --no-cache libpq

COPY --from=builder /opt/venv /opt/venv
COPY app.py .

ENV PATH="/opt/venv/bin:$PATH"

# Створення непривілейованого користувача для безпеки (Best Practice)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]

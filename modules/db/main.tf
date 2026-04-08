resource "random_id" "suffix" {
  byte_length = 4
}

# 1. Увімкнення Secret Manager API
resource "google_project_service" "secret_manager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# 2. Генерація випадкового пароля
resource "random_password" "db_password" {
  length  = 16
  special = false # Щоб уникнути проблем в URL підключення
}

# 3. Створення "Сейфа" (Secret)
resource "google_secret_manager_secret" "db_pass" {
  secret_id = "db-password-${random_id.suffix.hex}"
  project   = var.project_id
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager]
}

# 4. Покласти пароль у "Сейф" (Secret Version)
resource "google_secret_manager_secret_version" "db_pass_val" {
  secret      = google_secret_manager_secret.db_pass.id
  secret_data = random_password.db_password.result
}

# 5. Cloud SQL Інстанс (PostgreSQL)
resource "google_sql_database_instance" "main" {
  name             = "gke-pet-db-${random_id.suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  deletion_protection = false # Тільки для Pet Project!

  settings {
    tier = "db-f1-micro" # Найдешевший варіант

    ip_configuration {
      ipv4_enabled    = false       # Вимикаємо публічний IP (Безпека!)
      private_network = var.vpc_id  # Тільки приватний доступ з VPC
    }
  }
}

# 6. Створення бази та користувача
resource "google_sql_database" "database" {
  name     = "app_db"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

resource "google_sql_user" "users" {
  name     = "app_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
  project  = var.project_id
}

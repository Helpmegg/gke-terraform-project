resource "google_sql_database_instance" "postgres" {
  name             = "main-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region


  depends_on = [var.db_network_dependency]

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = var.network_id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled = true
    }
  }
}


resource "google_sql_database" "database" {
  name     = "myapp_db"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "users" {
  name     = "app_user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}
output "instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  value       = google_sql_database_instance.main.connection_name
}

output "db_name" {
  description = "The name of the database."
  value       = google_sql_database.database.name
}

output "db_user" {
  description = "The name of the database user."
  value       = google_sql_user.users.name
}

output "db_password_secret_id" {
  description = "The ID of the Secret Manager secret containing the DB password."
  value       = google_secret_manager_secret.db_pass.secret_id
}

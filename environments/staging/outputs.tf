output "db_instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  value       = module.db.instance_connection_name
}

output "db_password_secret_id" {
  description = "The ID of the Secret Manager secret containing the DB password."
  value       = module.db.db_password_secret_id
}

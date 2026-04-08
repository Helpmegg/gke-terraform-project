variable "project_id" {}
variable "region" {}

variable "network_name" {}
variable "subnet_name" {}

variable "pods_range_name" {}
variable "services_range_name" {}

variable "service_account_email" {}

variable "db_instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  type        = string
  default     = ""
}

variable "db_name" {
  description = "The name of the database."
  type        = string
  default     = ""
}

variable "db_user" {
  description = "The database user."
  type        = string
  default     = ""
}

variable "db_password_secret_id" {
  description = "The ID of the secret containing the database password."
  type        = string
  default     = ""
}

variable "project_id" {}
variable "region" {}

variable "network_name" {}
variable "subnet_name" {}

variable "pods_range_name" {}
variable "services_range_name" {}

variable "service_account_email" {}

variable "cluster_name" {
  description = "Ім'я GKE кластера"
  type        = string
  default     = "gke-pet-cluster"
}

variable "use_spot_instances" {
  description = "Чи використовувати Spot інстанси для workload нод"
  type        = bool
  default     = true
}

variable "autoscaling_min_nodes" {
  description = "Мінімальна кількість нод для Cluster Autoscaler"
  type        = number
  default     = 1
}

variable "autoscaling_max_nodes" {
  description = "Максимальна кількість нод для Cluster Autoscaler"
  type        = number
  default     = 3
}

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

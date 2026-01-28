variable "project_id" {
  description = "gke-tf-denis-2026"
  type        = string
}

variable "region" {
  description = "Region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  type        = string
  sensitive   = true
}
# modules/database/variables.tf

variable "project_id" {
  description = "ID вашого проекту Google Cloud"
  type        = string
}

variable "region" {
  description = "Регіон для бази даних (наприклад, europe-west1)"
  type        = string
}

variable "vpc_id" {
  description = "ID мережі VPC (береться з модуля VPC)"
  type        = string
}

variable "db_tier" {
  description = "Тип машини Cloud SQL (наприклад, db-f1-micro, db-custom-1-3840)"
  type        = string
  default     = "db-f1-micro"
}

variable "deletion_protection" {
  description = "Захист від видалення (true для production)"
  type        = bool
  default     = false
}
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
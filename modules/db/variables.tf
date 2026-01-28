variable "region" { type = string }
variable "network_id" { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}
# Ця змінна потрібна, щоб БД не почала створюватися раніше, ніж налаштується Peering
variable "db_network_dependency" { type = any }
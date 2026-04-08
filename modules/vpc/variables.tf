# modules/vpc/variables.tf

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "network_name" {
  description = "The name of the VPC network"
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR range for the primary subnet (Nodes)"
  type        = string
}

variable "pods_cidr" {
  description = "CIDR range for Pods (secondary range)"
  type        = string
}

variable "services_cidr" {
  description = "CIDR range for Services (secondary range)"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

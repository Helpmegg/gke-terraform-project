
output "network_name" {
  description = "The name of the VPC being created"
  value       = google_compute_network.main.name
}

#
output "network_id" {
  description = "The ID of the VPC being created"
  value       = google_compute_network.main.id
}


output "network_self_link" {
  description = "The URI of the VPC being created"
  value       = google_compute_network.main.self_link
}


output "subnet_name" {
  description = "The name of the subnet being created"
  value       = google_compute_subnetwork.private.name
}

output "subnet_region" {
  description = "The region where the subnet is created"
  value       = google_compute_subnetwork.private.region
}
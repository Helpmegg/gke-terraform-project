output "network_self_link" {
  value = google_compute_network.main.self_link
}

output "subnet_self_link" {
  value = google_compute_subnetwork.private.self_link
}


output "network_id" {
  value       = google_compute_network.main.id
  description = "ID VPC"
}

output "peering_completed" {
  value       = google_service_networking_connection.default.id
  description = "Peering complete"
}
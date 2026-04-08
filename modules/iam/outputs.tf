output "sa_email" {
  value = google_service_account.gke_sa.email
}

output "sa_id" {
  value = google_service_account.gke_sa.name
}

resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "guestbook-repo"
  description   = "Docker repository for Guestbook app"
  format        = "DOCKER"
}

output "repo_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.my_repo.repository_id}"
}
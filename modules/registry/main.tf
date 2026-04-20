resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "my-repo"
  description   = "Docker repository"
  format        = "DOCKER"
}

output "repo_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.my_repo.repository_id}"
}
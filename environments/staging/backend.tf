terraform {
  backend "gcs" {
    bucket = "gke-petproject-2026-497418"
    prefix = "terraform/staging"
  }
}

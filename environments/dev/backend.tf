terraform {
  backend "gcs" {
    bucket = "gke-tf-denis-2026"
    prefix = "terraform/state"
  }
}
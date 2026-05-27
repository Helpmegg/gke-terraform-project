provider "google" {
  project = "gke-petproject-2026-497418" # Вставте скопійований ID
  region  = "europe-west1"               # Ваша бажана локація
}

provider "google-beta" {
  project = "gke-petproject-2026-497418"
  region  = "europe-west1"
}
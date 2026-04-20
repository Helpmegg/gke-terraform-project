provider "google" {
  project = "gke-petproject-2026"  # Вставте скопійований ID
  region  = "europe-west1"        # Ваша бажана локація
}

provider "google-beta" {
  project = "gke-petproject-2026"
  region  = "europe-west1"
}
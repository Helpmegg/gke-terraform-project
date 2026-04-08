# Тимчасовий ресурс для тестування
resource "google_container_cluster" "primary_test" {
  project  = "gke-petproject-2026" # Замінено var.project_id
  name     = "gke-pet-cluster-test"
  location = "us-central1" # Замінено var.region

  initial_node_count       = 1
  remove_default_node_pool = true
  deletion_protection      = false # <--- Аргумент, що викликає помилку

  network    = "projects/gke-petproject-2026/global/networks/gke-vpc" # Потрібно вказати повний шлях
  subnetwork = "projects/gke-petproject-2026/regions/us-central1/subnetworks/gke-subnet" # Потрібно вказати повний шлях

  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods-range"
    services_secondary_range_name = "gke-services-range"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "gke-petproject-2026.svc.id.goog"
  }

  addons_config {
    gcp_secretmanager_csi_driver_config { # <--- Блок, що викликає помилку
      enabled = true
    }
  }
}

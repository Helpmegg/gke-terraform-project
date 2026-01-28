
resource "google_container_cluster" "primary" {
  name     = "gke-production-cluster"
  location = var.region


  remove_default_node_pool = true
  initial_node_count       = 1

  network    = var.network
  subnetwork = var.subnetwork


  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {
    cluster_secondary_range_name  = "k8s-pod-range"
    services_secondary_range_name = "k8s-service-range"
  }
}


resource "google_container_node_pool" "system" {
  name       = "system-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 1

  node_config {
    machine_type    = "e2-medium"
    service_account = google_service_account.gke_nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb    = 30
    disk_type    = "pd-standard"
  }
}


resource "google_container_node_pool" "workload" {
  name       = "workload-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 1

  node_config {
    spot            = true
    machine_type    = "e2-small"
    service_account = google_service_account.gke_nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb = 30
    disk_type    = "pd-standard"
  }
}

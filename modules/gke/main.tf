# 1. Сам Кластер (Control Plane)
resource "google_container_cluster" "primary" {
  name     = "gke-pet-cluster"
  location = var.region

  initial_node_count       = 1
  remove_default_node_pool = true
  deletion_protection      = false

  network    = var.network_name
  subnetwork = var.subnet_name

  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.0.0.0/8"
      display_name = "VPC CIDR"
    }
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "GitHub Actions"
    }
  }


  # Вмикаємо Cloud Operations Suite (Logging & Monitoring)
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }

  # Увімкнення Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Дозволяє використання CSI драйверу для управління безпечним монтуванням секретів
  secret_manager_config {
    enabled = true
  }
}

resource "google_container_node_pool" "workload_nodes" {
  name       = "workload-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    spot         = true
    machine_type = "e2-medium"
    disk_size_gb = 30
    disk_type    = "pd-standard"

    service_account = var.service_account_email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    # Додаємо taint, щоб системні поди не шедулилися сюди за замовчуванням (опціонально)
    taint {
      key    = "workload"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }
}

resource "google_container_node_pool" "system_nodes" {
  name       = "system-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    spot         = false # Системні поди краще не на спотах для стабільності
    machine_type = "e2-medium"
    disk_type    = "pd-standard"
    disk_size_gb = 30

    service_account = var.service_account_email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

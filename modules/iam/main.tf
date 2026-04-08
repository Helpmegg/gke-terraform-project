# 1. Створення VPC
resource "google_compute_network" "main" {
  name                    = var.network_name
  auto_create_subnetworks = false #
}

# 2. Створення підмережі (Subnet)
resource "google_compute_subnetwork" "private" {
  name          = "${var.network_name}-private-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id


  private_ip_google_access = true

  #
  secondary_ip_range {
    range_name    = "k8s-pods-range"
    ip_cidr_range = var.pods_cidr
  }
  secondary_ip_range {
    range_name    = "k8s-services-range"
    ip_cidr_range = var.services_cidr
  }
}


resource "google_compute_router" "router" {
  name    = "${var.network_name}-router"
  region  = var.region
  network = google_compute_network.main.id
}


resource "google_compute_router_nat" "nat" {
  name                               = "${var.network_name}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
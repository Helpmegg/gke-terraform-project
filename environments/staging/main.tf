
module "vpc" {
  source = "../../modules/vpc"

  project_id    = var.project_id
  network_name  = "staging-vpc"
  region        = "europe-west1"
  subnet_cidr   = "10.10.0.0/24"
  pods_cidr     = "10.11.0.0/20"
  services_cidr = "10.12.0.0/24"
}

module "iam" {
  source     = "../../modules/iam"
  project_id = var.project_id
}

module "db" {
  source = "../../modules/db"

  project_id          = var.project_id
  vpc_id              = module.vpc.network_id
  region              = "europe-west1"
  db_tier             = "db-f1-micro"
  deletion_protection = false

  depends_on = [module.vpc]
}

module "gke" {
  source = "../../modules/gke"

  project_id   = var.project_id
  region       = "europe-west1-b"
  cluster_name = "gke-staging-cluster"

  network_name = module.vpc.network_name
  subnet_name  = module.vpc.subnet_name

  pods_range_name     = "k8s-pods-range"
  services_range_name = "k8s-services-range"

  service_account_email = module.iam.sa_email

  # Autoscaling — аналогічно dev
  use_spot_instances    = true
  autoscaling_min_nodes = 1
  autoscaling_max_nodes = 3

  db_instance_connection_name = module.db.instance_connection_name
  db_name                     = module.db.db_name
  db_user                     = module.db.db_user
  db_password_secret_id       = module.db.db_password_secret_id
}

module "registry" {
  source     = "../../modules/registry"
  project_id = var.project_id
  region     = "europe-west1"
}

# Workload Identity binding
resource "google_service_account_iam_binding" "workload_identity_binding" {
  service_account_id = module.iam.sa_id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/web-app-ksa]"
  ]

  depends_on = [module.gke]
}

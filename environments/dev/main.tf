module "vpc" {
  source = "../../modules/vpc"
  region = "us-central1"
}

module "gke" {
  source     = "../../modules/gke"
  project_id = var.project_id
  region     = var.region


  network    = module.vpc.network_self_link
  subnetwork = module.vpc.subnet_self_link
}

module "db" {
  source                = "../../modules/db"
  region                = var.region
  network_id            = module.vpc.network_id
  db_password           = var.db_password
  db_network_dependency = module.vpc.peering_completed
}
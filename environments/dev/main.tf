
module "vpc" {
  source = "../../modules/vpc"

  project_id    = "gke-petproject-2026"
  network_name  = "main-vpc"
  region        = "europe-west1"
  subnet_cidr   = "10.0.0.0/28"
  pods_cidr     = "10.1.0.0/20"
  services_cidr = "10.2.0.0/24"
}

module "iam" {
  source     = "../../modules/iam"
  project_id = "gke-petproject-2026"
}

module "db" {
  source = "../../modules/db"

  project_id = "gke-petproject-2026"
  vpc_id     = module.vpc.network_id
  region     = "europe-west1"
}

module "gke" {
  source = "../../modules/gke"

  project_id = "gke-petproject-2026"
  region     = "europe-west1-b"

  network_name = module.vpc.network_name
  subnet_name  = module.vpc.subnet_name

  pods_range_name     = "k8s-pods-range"
  services_range_name = "k8s-services-range"

  service_account_email = module.iam.sa_email

  db_instance_connection_name = module.db.instance_connection_name
  db_name                     = module.db.db_name
  db_user                     = module.db.db_user
  db_password_secret_id       = module.db.db_password_secret_id
}

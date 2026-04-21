# modules/gke/firewall.tf
#
# Firewall для Health Checks Google Cloud Load Balancer.
# Необхідно для GCE Ingress у приватному GKE-кластері.
#
# ПРИМІТКА: Аналогічне правило є у modules/vpc/main.tf, але воно
# покриває лише порт 8080 та NodePort діапазон. Цей ресурс є частиною
# модуля GKE і явно прив'язаний до кластера через project_id.

resource "google_compute_firewall" "allow_gclb_health_checks" {
  project     = var.project_id
  name        = "gke-pet-cluster-allow-gclb-hc"
  description = "Allow Google LB health checks to reach GKE nodes (required for GCE Ingress)"
  network     = var.network_name

  direction = "INGRESS"
  priority  = 950 # Вищий пріоритет ніж дефолтне правило у VPC (1000)

  # Офіційні діапазони IP Google Cloud Load Balancer health checkers
  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16",
  ]

  # Теги нод — відповідають tags у node_config в main.tf
  target_tags = ["gke-node"]

  allow {
    protocol = "tcp"
    # 8080 — порт додатку (app container)
    # 30000-32767 — діапазон NodePort, який використовує GCE Ingress
    ports = ["8080", "30000-32767"]
  }
}

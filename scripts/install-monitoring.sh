#!/usr/bin/env bash
# =============================================================================
# install-monitoring.sh
# Встановлення kube-prometheus-stack (Prometheus + Grafana + Node Exporter)
# у namespace monitoring за допомогою Helm.
#
# Передумови:
#   - kubectl налаштовано та підключено до кластера gke-pet-cluster
#   - Helm 3.x встановлено
#
# Використання:
#   ./scripts/install-monitoring.sh
# =============================================================================
set -euo pipefail

NAMESPACE="monitoring"
RELEASE_NAME="prometheus"
CHART="prometheus-community/kube-prometheus-stack"
TIMEOUT="10m"

echo "==> Додаємо репозиторій Helm prometheus-community..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Створюємо namespace '${NAMESPACE}' (якщо не існує)..."
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

echo "==> Встановлюємо / оновлюємо ${RELEASE_NAME} у namespace ${NAMESPACE}..."
helm upgrade --install "${RELEASE_NAME}" "${CHART}" \
  --namespace "${NAMESPACE}" \
  --set alertmanager.enabled=false \
  --set grafana.service.type=ClusterIP \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --wait \
  --timeout "${TIMEOUT}"

echo ""
echo "==> Встановлення завершено."
echo ""
echo "Доступ до Grafana UI (через port-forward):"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-grafana 3000:80"
echo "  Відкрити: http://localhost:3000"
echo "  Логін: admin / prom-operator"
echo ""
echo "Доступ до Prometheus UI:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "  Відкрити: http://localhost:9090"

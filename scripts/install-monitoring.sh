#!/bin/bash
# install-monitoring.sh
# Цей скрипт встановлює Prometheus та Grafana у ваш GKE кластер використовуючи Helm

set -e

echo "================================================="
echo " Встановлення Prometheus та Grafana через Helm "
echo "================================================="

# Перевірка наявності helm
if ! command -v helm &> /dev/null; then
    echo "Помилка: helm не знайдено. Будь ласка, встановіть Helm."
    exit 1
fi

# Перевірка підключення до Kubernetes (через kubectl)
if ! kubectl cluster-info &> /dev/null; then
    echo "Помилка: Немає підключення до Kubernetes кластеру."
    echo "Спершу виконайте: gcloud container clusters get-credentials gke-pet-cluster --zone europe-west1-b"
    exit 1
fi

echo "[1/4] Додавання helm-репозиторію prometheus-community..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "[2/4] Створення namespace 'monitoring'..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

echo "[3/4] Встановлення kube-prometheus-stack..."
# Встановлюємо kube-prometheus-stack з кастомними параметрами, якщо потрібно
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set alertmanager.enabled=false \
  --set grafana.service.type=ClusterIP \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --wait \
  --timeout 10m

echo "[4/4] Встановлення завершено!"
echo "================================================="
echo "Щоб отримати доступ до Grafana, відкрийте прокидання портів:"
echo "kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
echo ""
echo "Після цього відкрийте в браузері: http://localhost:3000"
echo "Логін за замовчуванням: admin"
echo "Пароль: prom-operator"
echo "================================================="

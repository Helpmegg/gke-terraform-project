terraform {
  backend "gcs" {
    bucket = "gke-petproject-2026"
    prefix = "terraform/state"
    # Для блокування стану (state locking) потрібно розкоментувати/налаштувати:
    # Google Cloud Storage за замовчуванням підтримує state locking, додаткові налаштування DynamoDB (як у AWS) не потрібні,
    # але варто впевнитися, що у бакеті увімкнено Object Versioning (це робиться на рівні створення бакета, не в самому backend.tf)
  }
}

locals {
  apis       = toset(["run.googleapis.com", "iam.googleapis.com", "secretmanager.googleapis.com", "monitoring.googleapis.com"])
  normal_env = merge(var.env, { APP_ENV = var.environment, THREADS = tostring(var.concurrency) })
}
# この構成を削除しても共有プロジェクトのAPIを無効化しません。
resource "google_project_service" "api" {
  for_each           = local.apis
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = var.runtime_account_id
  display_name = "Cloud Run runtime (${var.environment})"
  depends_on   = [google_project_service.api]
}
# secret_envに指定したSecretだけに読み取り権限を付けます。
resource "google_secret_manager_secret_iam_member" "runtime" {
  for_each  = toset([for s in values(var.secret_env) : s.secret_id])
  project   = var.project_id
  secret_id = each.key
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}
resource "google_cloud_run_v2_service" "app" {
  project              = var.project_id
  name                 = var.service_name
  location             = var.region
  deletion_protection  = var.deletion_protection
  ingress              = var.ingress
  invoker_iam_disabled = false
  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
  scaling {
    min_instance_count = var.min_instances
    max_instance_count = var.max_instances
  }
  template {
    service_account                  = google_service_account.runtime.email
    timeout                          = "${var.timeout_seconds}s"
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"
    max_instance_request_concurrency = var.concurrency
    session_affinity                 = false
    containers {
      image = var.image
      ports { container_port = 8080 }
      resources {
        limits            = { cpu = var.cpu, memory = var.memory }
        cpu_idle          = true # リクエストベース課金
        startup_cpu_boost = var.startup_cpu_boost
      }
      dynamic "env" {
        for_each = local.normal_env
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = var.secret_env
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_id
              version = env.value.version
            }
          }
        }
      }
      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 2
        period_seconds        = 5
        failure_threshold     = 12
        http_get { path = "/" }
      }
      # liveness probeは本例では使いません（課金方式との互換性を別途確認）。
    }
    dynamic "vpc_access" {
      for_each = var.vpc == null ? [] : [var.vpc]
      content {
        egress = vpc_access.value.egress
        network_interfaces {
          network    = vpc_access.value.network
          subnetwork = vpc_access.value.subnetwork
        }
      }
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  lifecycle {
    prevent_destroy = true # 解除にはこの定数をfalseへ変更します。
  }
  depends_on = [google_project_service.api, google_secret_manager_secret_iam_member.runtime]
}
# member型を使用して、他チームの同じロールのメンバーを一括上書きしません。
resource "google_cloud_run_v2_service_iam_member" "invoker" {
  for_each = var.invoker_members
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = each.key
}

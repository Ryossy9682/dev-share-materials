resource "google_monitoring_alert_policy" "errors" {
  count                 = var.enable_alert ? 1 : 0
  project               = var.project_id
  display_name          = "${var.service_name}: sustained HTTP 5xx"
  combiner              = "OR"
  enabled               = true
  notification_channels = var.notification_channels
  conditions {
    display_name = "HTTP 5xx responses for 5 minutes"
    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\" AND resource.labels.service_name = \"${var.service_name}\" AND metric.labels.response_code_class = \"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
      trigger { count = 1 }
    }
  }
  documentation {
    content   = "Cloud Runのログ、直近の変更、外部APIの権限・応答を確認します。"
    mime_type = "text/markdown"
  }
  depends_on = [google_project_service.api]
}

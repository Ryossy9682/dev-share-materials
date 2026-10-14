output "service_url" {
  description = "認証付きで確認するサービスURL"
  value       = google_cloud_run_v2_service.app.uri
}
output "runtime_service_account" {
  value = google_service_account.runtime.email
}

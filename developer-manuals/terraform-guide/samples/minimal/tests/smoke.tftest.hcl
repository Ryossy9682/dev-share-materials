mock_provider "google" {}
run "private_service_configuration" {
  command = plan
  variables {
    project_id              = "sample-project"
    image                   = "asia-northeast1-docker.pkg.dev/sample-project/apps/hello@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    runtime_service_account = "runtime@sample-project.iam.gserviceaccount.com"
  }
  assert {
    condition     = google_cloud_run_v2_service.app.invoker_iam_disabled == false
    error_message = "Cloud RunのIAM認証を無効化しないこと。"
  }
}

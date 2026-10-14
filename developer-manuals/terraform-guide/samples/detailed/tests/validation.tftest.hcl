mock_provider "google" {}
run "reject_public_invoker" {
  command = plan
  variables {
    project_id      = "sample-project"
    image           = "asia-northeast1-docker.pkg.dev/sample-project/apps/hello@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    invoker_members = ["allUsers"]
  }
  expect_failures = [var.invoker_members]
}
run "reject_invalid_scaling" {
  command = plan
  variables {
    project_id    = "sample-project"
    image         = "asia-northeast1-docker.pkg.dev/sample-project/apps/hello@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    min_instances = 5
    max_instances = 2
  }
  expect_failures = [var.max_instances]
}

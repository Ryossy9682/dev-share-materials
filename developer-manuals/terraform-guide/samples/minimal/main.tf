terraform {
  required_version = ">= 1.9.0, < 2.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.10.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region  = var.region
}

# 学習用：API、SA、イメージは事前に用意します。
variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "asia-northeast1"
}
variable "service_name" {
  type    = string
  default = "tf-hello-minimal"
}
variable "image" { type = string }
variable "runtime_service_account" { type = string }

resource "google_cloud_run_v2_service" "app" {
  name                 = var.service_name
  location             = var.region
  deletion_protection  = false
  ingress              = "INGRESS_TRAFFIC_ALL"
  invoker_iam_disabled = false
  template {
    service_account = var.runtime_service_account
    containers {
      image = var.image
    }
  }
}
output "service_url" { value = google_cloud_run_v2_service.app.uri }

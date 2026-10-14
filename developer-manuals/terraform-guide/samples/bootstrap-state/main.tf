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
variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "asia-northeast1"
}
variable "bucket_name" { type = string }
resource "google_storage_bucket" "state" {
  project                     = var.project_id
  name                        = var.bucket_name
  location                    = "ASIA-NORTHEAST1"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  lifecycle { prevent_destroy = true }
}
output "bucket_name" { value = google_storage_bucket.state.name }

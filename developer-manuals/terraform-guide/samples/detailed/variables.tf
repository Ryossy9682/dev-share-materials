variable "project_id" {
  description = "配置する既存Google CloudプロジェクトのID"
  type        = string
}
variable "region" {
  description = "Cloud RunとVPCサブネットのリージョン"
  type        = string
  default     = "asia-northeast1"
}
variable "service_name" {
  description = "最小構成とは別名にします。"
  type        = string
  default     = "tf-hello-detailed"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,47}[a-z0-9]$", var.service_name))
    error_message = "サービス名は2～49文字の小文字・数字・ハイフンで指定します。"
  }
}
variable "runtime_account_id" {
  description = "作成する専用実行用SAのID"
  type        = string
  default     = "tf-hello-runtime"
}
variable "image" {
  description = "既存イメージ。詳細構成はsha256ダイジェストで固定します。"
  type        = string
  validation {
    condition     = can(regex("@sha256:[a-f0-9]{64}$", var.image))
    error_message = "imageは@sha256:と64桁のダイジェストで固定してください。"
  }
}
variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environmentはdev/stg/prodです。"
  }
}
variable "cpu" {
  type    = string
  default = "1"
  validation {
    condition     = contains(["1", "2"], var.cpu)
    error_message = "この例のcpuは1か2です。"
  }
}
variable "memory" {
  type    = string
  default = "512Mi"
  validation {
    condition     = contains(["512Mi", "1Gi", "2Gi", "4Gi"], var.memory)
    error_message = "この例は512Mi/1Gi/2Gi/4Giに限定しています。"
  }
}
variable "concurrency" {
  type    = number
  default = 8
  validation {
    condition     = var.concurrency >= 1 && var.concurrency <= 80 && floor(var.concurrency) == var.concurrency
    error_message = "この例のconcurrencyは1～80の整数です。"
  }
}
variable "min_instances" {
  type    = number
  default = 0
  validation {
    condition     = var.min_instances >= 0 && floor(var.min_instances) == var.min_instances
    error_message = "min_instancesは0以上の整数です。"
  }
}
variable "max_instances" {
  type    = number
  default = 3
  validation {
    condition     = var.max_instances >= 1 && var.max_instances <= 100 && var.max_instances >= var.min_instances && floor(var.max_instances) == var.max_instances
    error_message = "max_instancesは1～100、かつmin_instances以上の整数です。"
  }
}
variable "timeout_seconds" {
  type    = number
  default = 60
  validation {
    condition     = var.timeout_seconds >= 1 && var.timeout_seconds <= 3600 && floor(var.timeout_seconds) == var.timeout_seconds
    error_message = "timeout_secondsは1～3600の整数です。"
  }
}
variable "startup_cpu_boost" {
  type    = bool
  default = false
}
variable "deletion_protection" {
  description = "falseをapplyしてからでないと削除できません。prevent_destroyも別に解除が必要です。"
  type        = bool
  default     = true
}
variable "ingress" {
  type    = string
  default = "INGRESS_TRAFFIC_ALL"
  validation {
    condition     = contains(["INGRESS_TRAFFIC_ALL", "INGRESS_TRAFFIC_INTERNAL_ONLY", "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"], var.ingress)
    error_message = "Cloud RunがサポートするIngress列挙値を指定します。"
  }
}
variable "invoker_members" {
  description = "サービスを呼べるuser/group/serviceAccount。allUsersは指定不可。"
  type        = set(string)
  default     = []
  validation {
    condition     = alltrue([for member in var.invoker_members : can(regex("^(user|group|serviceAccount):[^ ]+@[^ ]+$", member))])
    error_message = "user: / group: / serviceAccount: のメール主体だけ指定します。"
  }
}
variable "env" {
  description = "機密でない環境変数。値はstateにも保存されます。"
  type        = map(string)
  default     = {}
  validation {
    condition     = !contains(keys(var.env), "APP_ENV") && !contains(keys(var.env), "THREADS")
    error_message = "APP_ENVとTHREADSはサンプルが管理する予約キーです。"
  }
}
variable "secret_env" {
  description = "同一プロジェクトの既存Secret IDと固定バージョン。機密の値自体は指定しません。"
  type        = map(object({ secret_id = string, version = string }))
  default     = {}
  validation {
    condition     = alltrue([for name, s in var.secret_env : can(regex("^[1-9][0-9]*$", s.version)) && !contains(concat(keys(var.env), ["APP_ENV", "THREADS"]), name)])
    error_message = "Secretバージョンは正の整数文字列、環境変数名は通常のenvや予約キーと重複不可です。"
  }
}
variable "vpc" {
  description = "既存VPCを使う場合だけ指定。サブネットはCloud Runと同リージョン。"
  type        = object({ network = string, subnetwork = string, egress = string })
  default     = null
  validation {
    condition     = var.vpc == null ? true : contains(["PRIVATE_RANGES_ONLY", "ALL_TRAFFIC"], var.vpc.egress)
    error_message = "VPC egressはPRIVATE_RANGES_ONLYかALL_TRAFFICです。"
  }
}
variable "enable_alert" {
  description = "5xxが継続する場合の監視ポリシーを作成するか"
  type        = bool
  default     = false
}
variable "notification_channels" {
  description = "既存Monitoring通知チャネルの完全なID。空なら通知先はありません。"
  type        = list(string)
  default     = []
}

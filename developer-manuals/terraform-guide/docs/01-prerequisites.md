# Google Cloudの事前準備

Terraform CLI、Google Cloud CLIを用意し、既存の開発プロジェクトと課金を確認します。以下はPowerShellです。YOUR_PROJECT_IDをプロジェクトIDへ置き換えます。

```powershell
$projectId = "YOUR_PROJECT_ID"
gcloud auth login
gcloud auth application-default login
gcloud auth application-default set-quota-project $projectId
```

gcloudのログインとTerraform providerが使うADCは別です。ローカルにサービスアカウントの鍵JSONを置くことを前提にしていません。CIではWorkload Identity Federation等を検討します。

設定担当者が、使用するAPIを有効化します。詳細構成はRun・IAM・Secret Manager・MonitoringのAPIをTerraformで管理しますが、Terraform実行の前提となるService Usage等は有効化しておきます。既存のAPI管理主体がある場合は、その主体へ統一します。

```powershell
gcloud services enable serviceusage.googleapis.com cloudresourcemanager.googleapis.com `
  run.googleapis.com iam.googleapis.com artifactregistry.googleapis.com `
  cloudbuild.googleapis.com storage.googleapis.com --project $projectId
```

必要な権限は次の操作単位で担当者と確認します。一律にOwnerを付ける手順ではありません。

| 主体 | 必要な操作 |
|---|---|
| Terraform実行者 | Cloud Runの作成・更新、実行SAへのactAs、必要なAPIの有効化 |
| 詳細構成の設定担当者 | SA作成、対象サービスのIAM設定、既存SecretのIAM設定、監視ポリシー作成 |
| stateを扱う実行者 | stateバケット内のオブジェクト操作。GCS backend公式手順ではStorage Object Adminを確認 |
| イメージビルド用SA | Cloud Buildの利用、対象Artifact Registryへの書込、使用するログ・ソースへの権限 |
| Cloud Runのサービスエージェント | 対象イメージへの読取。別プロジェクトのイメージでは明示設定も必要 |
| 関数の実行用SA | 必要な業務API・データへのアクセス。あいさつ処理は業務権限不要 |

コンテナを用意する場合、同一プロジェクト・リージョンにArtifact RegistryのDockerリポジトリ`apps`を作ります。既存の場合は作成コマンドを省略します。

```powershell
gcloud artifacts repositories create apps --repository-format=docker `
  --location=asia-northeast1 --project $projectId
$image = "asia-northeast1-docker.pkg.dev/$projectId/apps/hello"
gcloud builds submit .\samples\app --tag "$($image):manual-v1" --project $projectId
$digest = gcloud artifacts docker images describe "$($image):manual-v1" `
  --project $projectId --format="value(image_summary.digest)"
Write-Output "$image@$digest"
```

出力された`@sha256:...`付きURLをtfvarsのimageへ設定します。最小構成は実行用SAも事前に用意します。詳細構成は専用SAを作成します。イメージのビルド・保管には別途費用が発生し得ます。

出典：

- https://docs.cloud.google.com/docs/terraform/authentication
- https://developer.hashicorp.com/terraform/language/backend/gcs
- https://docs.cloud.google.com/run/docs/deploying
- https://docs.cloud.google.com/build/docs/building/build-containers

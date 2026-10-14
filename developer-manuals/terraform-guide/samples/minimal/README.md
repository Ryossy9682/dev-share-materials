# 最小構成版

`main.tf`だけに基本設定をまとめています。既存プロジェクト、Run API、実行用SA、既存コンテナイメージが必要です。CPU・メモリ・スケーリング等の多くはAPI/providerの既定値に委ねるため、コスト最適化の完成形ではありません。IAM認証は有効で、公開呼び出し権限は作りません。

このフォルダーで以下を実行します。

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
# terraform.tfvarsを実際の値に編集
terraform init
terraform fmt -check
terraform validate
terraform test
terraform plan -out="change.tfplan"
terraform show "change.tfplan"
terraform apply "change.tfplan"
terraform output -raw service_url
```

`terraform apply`は実リソースを作成・更新します。保存済みplanを指定するapplyでは改めて確認されないため、showで確認したplanを適用します。planとstateは機密を含み得るファイルです。

呼び出し権限は設定担当者が付与します。最小構成はIAMメンバーをTerraformで管理しません。

```powershell
gcloud run services add-iam-policy-binding tf-hello-minimal `
  --project YOUR_PROJECT_ID --region asia-northeast1 `
  --member="user:YOUR_EMAIL" --role="roles/run.invoker"
$url = terraform output -raw service_url
$token = gcloud auth print-identity-token
Invoke-RestMethod "$url/?name=Developer" -Headers @{Authorization="Bearer $token"}
```

学習後に削除する場合は`terraform plan -destroy -out="destroy.tfplan"`、`terraform show "destroy.tfplan"`で範囲を確認してから`terraform apply "destroy.tfplan"`を実行します。実行用SAやイメージはこのstateの管理外なので残ります。

出典： https://developer.hashicorp.com/terraform/cli/commands/plan

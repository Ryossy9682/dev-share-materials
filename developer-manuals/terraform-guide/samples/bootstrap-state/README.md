# stateバケットを先に用意する

バケットがすでにある場合は作成不要です。この補助構成はローカルstateで、東京リージョンのバケットを作成します。世界で一意なbucket_nameへ変更してください。

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan -out="bootstrap.tfplan"
terraform show "bootstrap.tfplan"
terraform apply "bootstrap.tfplan"
```

バケットはオブジェクトのバージョニング、均一なアクセス制御、公開アクセス防止、削除保護を設定します。実行者には作成権限、state利用者には対象バケットへのオブジェクト操作権限が必要です。

このフォルダーのローカルstateも安全に保持します。チーム利用へ移す場合、同じバケットの別prefixへbootstrap自身のstateを移行できます。管理するstateと保存先は削除依存があるため、運用基盤として分けて扱います。

出典： https://developer.hashicorp.com/terraform/language/backend/gcs

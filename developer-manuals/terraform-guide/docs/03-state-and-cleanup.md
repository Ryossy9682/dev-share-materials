# state移行と削除

stateは設定と実リソースの対応表です。同じリソースを複数stateで管理しません。最小版と詳細版は別サービスとして作成する例で、移行によって自動的に引き継がれる構成ではありません。

既存サービスを管理する場合、構成を実物に合わせてからimportし、planで予期しない削除・置換・公開化がないことを確認します。importはコードと実設定を完全に一致させる処理ではありません。

```hcl
import {
  to = google_cloud_run_v2_service.app
  id = "projects/PROJECT_ID/locations/asia-northeast1/services/SERVICE_NAME"
}
```

上記は説明例です。既存のCloud Run functionsや別Terraform管理下のサービスへそのまま適用しないでください。管理方式・state所有者・依存SA・トリガーを確認した専用の移行設計が必要です。

ローカルstateをGCSへ移す場合、作業を停止し、stateの安全なバックアップを取得してからbackendを追加し、`terraform init -migrate-state -backend-config="backend.dev.hcl"`を実行します。`-reconfigure`はstateを移行するコマンドではありません。GCSではbucket+prefixを環境ごとに分けます。

詳細版を意図して削除する場合の順序：

1. 対象プロジェクト・サービス・stateを確認します。
2. `main.tf`の`prevent_destroy = true`を`false`へ変更します。
3. tfvarsの`deletion_protection = false`をplanし、通常のapplyで反映します。
4. `terraform plan -destroy -out="destroy.tfplan"`を作成し、`terraform show "destroy.tfplan"`で削除範囲を確認します。
5. 意図した範囲であることを確認して`terraform apply "destroy.tfplan"`を実行します。

詳細版の専用SAと追加IAM・監視も削除対象です。Secret本体、VPC、通知チャネル、イメージ、stateバケットは管理外なので残ります。APIリソースは`disable_on_destroy=false`のためAPI自体は無効化されません。`prevent_destroy`はコードのブロックを消せば保護が残る保証はなく、IAMや運用上の制御の代替にはなりません。

stateにロックが残った場合、実行中の処理がないこととロック所有者を確認します。`force-unlock`を最初の対処にはしません。

出典：

- https://developer.hashicorp.com/terraform/language/state
- https://developer.hashicorp.com/terraform/language/import
- https://developer.hashicorp.com/terraform/language/backend/gcs
- https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle

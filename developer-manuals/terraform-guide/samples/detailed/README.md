# 詳細設定版

最小版と同じ関数イメージを、異なるサービス名・専用実行SAで配置します。GCS backendを使用し、stateバケットを先に作成する必要があります。backendのbucketとprefixはTerraform変数ではなくinit時の設定です。

```powershell
Copy-Item backend.dev.hcl.example backend.dev.hcl
Copy-Item terraform.tfvars.example terraform.tfvars
# bucket・prefixとtfvarsを実際の値へ編集
terraform init -backend-config="backend.dev.hcl"
terraform fmt -check
terraform validate
terraform test
terraform plan -out="change.tfplan"
terraform show "change.tfplan"
terraform apply "change.tfplan"
```

設定の役割：`versions.tf`＝バージョン/provider、`backend.tf`＝state保存先、`variables.tf`＝入力と検証、`main.tf`＝実リソース、`monitoring.tf`＝任意の監視、`outputs.tf`＝確認用URL等です。同じフォルダーの全`.tf`がまとめて評価され、ファイル名の順で作成されるわけではありません。

詳細版はデフォルトで削除保護が有効です。削除は`docs/03-state-and-cleanup.md`を読み、Terraformのprevent_destroyとproviderのdeletion_protectionを別々に解除して行います。

Secretの値はTerraformから作成しません。事前登録した同一プロジェクトのSecret IDと数字のバージョンだけ指定します。`secret_env`が空ならSecretの読み取り権限は作りません。VPCと通知チャネルも既存のものを指定する任意機能で、初期値では利用しません。

`enable_alert=true`で5xx応答率（件/秒）が0超の状態が5分継続した場合の監視ポリシーを作ります。既定の通知チャネルは空のため、通知が必要なら既存チャネルIDを設定します。これはエラー割合の監視ではありません。

`env`の値はstateに入ります。パスワードを通常のenvへ入れないでください。サンプルのあいさつ関数はAPI_TOKEN等の業務設定を使いません。Secret/VPCは設定方法の例です。

各環境はディレクトリ・サービス名・SA名・backend prefixを分けます。workspaceの切替だけで本番誤適用を防げると判断しないでください。詳細版の管理対象に対するgcloud/コンソール変更は、次のplanで差分になる場合があります。

出典： https://developer.hashicorp.com/terraform/language/backend/gcs

# 検証結果と適用前チェック

確認日：2026-10-14

実行環境はLinux、Terraform CLI 1.13.5です。Google provider 7.10.0を公式レジストリから取得し、署名と依存ロックファイルを確認しました。最小構成・詳細構成・stateバケット補助構成の`terraform fmt -check`が成功し、HCLの構文を読み取れることを確認しています。

最小構成と詳細構成で`terraform validate`と`terraform test`を試みましたが、この実行環境ではprovider起動時のUnixソケット作成が`operation not permitted`となるため、完了していません。テストが成功したという実績ではありません。設定項目は対象バージョンの公式providerドキュメントと照合しています。

Google Cloudへの実plan・apply・削除、GCSロック・IAM・Secret・VPC・監視の実動作、Dockerイメージのビルドは未実施です。コンテナに使うHTTP関数は、前のサンプルでFunctions Framework経由の5テストとローカルHTTP呼び出しを確認したものです。

利用環境で行うチェック：

1. 各構成で`terraform init`と`terraform validate`を成功させます。
2. minimal/detailedの`terraform test`を成功させます。付属テストはmock providerで実リソースを作成しない構成です。
3. 開発プロジェクトの実planをレビューし、権限・既存リソース・削除/置換を確認します。
4. apply後にIAM付きHTTP呼び出し、ログ、state、再planを確認します。
5. 任意のSecret/VPC/監視機能を有効にした構成でも確認します。

出典：

- https://developer.hashicorp.com/terraform/cli/commands/validate
- https://developer.hashicorp.com/terraform/language/tests/mocking
- https://registry.terraform.io/providers/hashicorp/google/7.10.0/docs/resources/cloud_run_v2_service

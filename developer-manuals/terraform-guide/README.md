# Terraform開発マニュアル・サンプル

`02-terraform-developer-guide.html`をブラウザーで開き、最小構成→詳細構成の順で学習します。各設定は独立したルートモジュールです。同じサービスを二つのstateから管理しないでください。

| フォルダー | 内容 |
|---|---|
| `samples/minimal/` | 最小構成。1つのmain.tfにprovider・変数・Cloud Run・出力を集約 |
| `samples/detailed/` | 詳細構成。API、SA、IAM、資源、課金、Secret参照、VPC、監視、削除保護、GCS backend |
| `samples/bootstrap-state/` | 詳細構成のstateバケットを事前作成する補助手順 |
| `samples/app/` | 前のマニュアルと同じHTTP関数をコンテナ化するDockerfile |
| `docs/` | 設定の比較、事前準備、state移行、削除、検証結果 |

対象はGoogle CloudのCloud Runサービスです。関数のソースを直接Terraformでビルドせず、Functions Frameworkの関数コンテナを先に用意して配置します。既存Cloud Run functionsへそのまま適用する移行手順ではありません。

実行環境：Terraform 1.9以上2.0未満。サンプルのGoogle providerは7.10系に固定し、検証した選択バージョンを各フォルダーの`.terraform.lock.hcl`に記録しています。これらは最新版の推奨を意味しません。更新時は差分・互換性を検証してください。

公式情報： https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build

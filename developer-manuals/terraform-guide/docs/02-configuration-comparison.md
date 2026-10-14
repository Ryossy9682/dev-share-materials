# 最小構成と詳細構成の比較

| 観点 | minimal | detailed |
|---|---|---|
| ファイル構成 | main.tfに集約 | 観点別に分割 |
| state | ローカル | GCS。事前にバケットを用意 |
| API | 事前有効化 | 4 APIを管理。削除時の無効化なし |
| 実行用SA | 既存SA | 専用SAを作成 |
| IAM認証 | 有効 | 有効 |
| 呼び出し権限 | 別途付与 | 指定したuser/group/SAだけmemberで追加 |
| CPU・メモリ | 多くの項目を既定値へ委ねる | 1 CPU/512Miを基準に変数化 |
| 同時実行 | 既定値 | 8、THREADSも連動 |
| インスタンス数 | 既定値 | サービス全体で最小0・最大3 |
| 課金 | 明示設定なし | cpu_idle=trueのリクエストベース |
| 起動ブースト | 明示設定なし | 既定false。比較して変更 |
| ヘルスチェック | 既定 | HTTP startup probe。業務では専用path検討 |
| Ingress | ALL。IAM認証とは別 | 3種類から指定可能。初期値ALL |
| Secret | なし | 任意。既存Secretの数字バージョン参照 |
| VPC | なし | 任意。既存ネットワークへのDirect VPC egress |
| 監視 | なし | 任意。5xx継続のポリシーと既存通知チャネル |
| 削除保護 | 学習用にfalse | deletion_protectionとprevent_destroy |
| イメージ | 任意の既存参照 | ダイジェスト固定を入力検証 |
| トラフィック | 既定 | 最新リビジョン100%を明示 |

詳細版は万能な本番テンプレートではありません。業務のSLO、データ接続先、組織ポリシーに合わせて調整します。VPCのALL_TRAFFIC、Cloud NAT、最小インスタンス、Secret、ログ、stateの過去バージョン保持等は費用にも影響します。

出典： https://registry.terraform.io/providers/hashicorp/google/7.10.0/docs/resources/cloud_run_v2_service

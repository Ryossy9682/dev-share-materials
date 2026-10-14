# CI/CD sample repository

上位フォルダのHTMLとdocs/SETUP.mdを確認してください。MIN/MAX workflowはvariantsから一方だけコピーします。

# GitHub Actions CI/CD: MIN / MAX

このフォルダのHTMLで14章の解説、図解、設定全文を確認してください。
MAXは本教材の充実構成でありGitHubの絶対上限ではありません。

## 導入

1. sample-repository の内容を対象GitHubリポジトリのルートに置く。
2. variants/min または variants/max の `.github/workflows/dbt-ci-cd.yml` を対象の同じパスへコピー。一方だけを選ぶ。
3. MAXでは `.github/dependabot.yml` もコピーする。
4. mainのPR必須・CI必須・workflow変更レビューを設定する。MAX必須チェックはQuality gate。
5. GitHub Settings > Environments にproduction（MAXはstagingも）を作りmain限定を設定。
6. productionで承認者・自己承認禁止を設定。公開/非公開とプランにより利用可否が変わる。YAMLだけでは承認は有効にならない。
7. Environment variables とGoogle Cloud WIF / IAMを設定。
8. MAXの統合検証を先に実施。MINは検証用の出力先でクラウドの動作を確認する。
9. mainからworkflow_dispatchのdeploy=trueを実行。本番コマンドはtag:baseだけ、seedとfull refreshなし。

## 環境変数

- `GCP_PROJECT_ID` (staging／production): BigQueryジョブのproject ID。環境ごとに別project推奨
- `BIGQUERY_LOCATION` (両環境): 例：asia-northeast1。rawと出力のlocationを合わせる
- `GCP_WIF_PROVIDER` (両環境): projects/数値/locations/global/workloadIdentityPools/…/providers/…
- `GCP_SERVICE_ACCOUNT` (両環境): 環境ごとに専用のSAメール
- `DBT_PROD_DATASET` (production): 出力先。例analytics_prod。事前作成
- `DBT_RAW_PROJECT_ID` (production): raw_orders／raw_customers／raw_eventsのproject
- `DBT_RAW_DATASET` (production): raw source dataset。事前ロード

## BigQueryと認証

- Workload Identity Federationを使用し、対象のrepository_id/owner_id、main、environmentを制限する。
- production SA: jobUserを実行project、dataViewerをraw dataset、dataEditorを出力datasetに設定。
- staging SA: 検証専用projectへ隔離しdataset作成・削除とクエリ実行を許可する。
- raw_orders / raw_customers / raw_eventsは架空教材スキーマ。実用前にモデルとsource設定を適合させる。
- production出力datasetとraw datasetは事前に用意。同じlocationを使う。
- authの一時ファイルgha-creds-*.jsonをコミット/成果物保存しない。

## ローカル検証

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-offline.txt
cp profiles/profiles.yml.example profiles/profiles.yml
dbt --no-send-anonymous-usage-stats --no-partial-parse parse --project-dir projects/patterns --profiles-dir profiles --vars '{enable_patterns: true, enable_snapshots: true}'
python scripts/check_demo_offline.py
python ci/test_guards.py
```

## 運用上の境界

- MAXのscheduleは毎日UTC16:15/JST01:15。起動時刻は厳密保証なし。本番自動反映なし。不要ならschedule削除。
- MAXはmainでBigQuery統合検証を実行するためクラウド料金が発生する。
- MERGE期待値469は削除未伝播を再現する教材用。正しい本番売上は349。
- cleanupは対象runのCI datasetのみ。強制停止ではcleanupが走らない場合があり、テーブルTTLはdataset自体を消さない。
- concurrencyは実行中の本番を中断しないが、既定のpendingは新しいpendingへ置換され得る。
- dbt build全体はトランザクションではない。本番の部分反映とデータ復旧は別設計。
- Actions SHA固定、依存lockは更新して再検証する。lockはhash未固定。
- アプリの段階配信、Terraform plan/apply、通知、自動rollback、Slim CI等は拡張案であり今回のYAMLには未実装。

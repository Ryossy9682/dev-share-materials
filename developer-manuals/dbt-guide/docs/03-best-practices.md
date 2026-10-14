# 設計・品質・運用の基準

| 観点 | 基準と終了条件 |
|---|---|
| 粒度 | 「注文IDごと」「日付ごと」等を1行の意味として定義。キーの重複テストを置く |
| 金額 | 通貨、税、割引、返金、丸め、売上計上時点を業務側と定義。NUMERIC等を検討 |
| Source | 取り込み済みテーブルを定義。元データの取り込み処理と混同しない |
| Staging | 改名、型、基本計算、状態正規化。集計・多表結合は必要性で別工程へ |
| 無意味な層 | 完全ミラーViewを必須にしない。モデル分割に役割があるか確認 |
| ref/source | 依存を明示し、環境名をSQLへ直接固定しない |
| Join | キーの一意性、欠損、1対多による増殖を確認。Distinctで隠さない |
| Incremental | 更新・遅延・削除・空パーティション・再実行・full-refreshを設計 |
| Data tests | unique/not_null/relationships/accepted_valuesに加え業務整合を確認 |
| Unit tests | 境界、丸め、状態変換を少量fixtureで検証 |
| Freshness | 最終更新時刻とロード時刻を区別。取り込み停止の監視は別コマンド・閾値で定義 |
| Contract | 重要な公開モデルの列名・型を固定。正しい金額や非NULLまで保証するものではない |
| 公開 | 全DAGの更新が1トランザクションとは限らない。テスト後の公開切替を必要に応じて設計 |
| 個人情報 | Gitのseedへ実データを入れない。アクセス権・マスキング・ログ・成果物も確認 |
| 環境 | 個人・CI・本番のdatasetと権限を分離。custom schemaの既定挙動も確認 |
| 実行 | 同じIncremental/Snapshotを同時に更新しない。取り込み完了後に実行する |
| ドキュメント | 定義、責任者、更新頻度、利用先（Exposure等）を残す |
| 費用 | build・テスト・Snapshot・BI照会・保存・外部実行基盤を合算して比較 |

運用例：取り込み完了 → Source freshness → dbt build → 公開条件確認 → BI利用 → 費用・鮮度・件数監視。dbt Core単体のCLIに定期実行サーバーや通知先が自動で付くわけではありません。Cloud Run jobs、外部オーケストレーター、dbt platformなどで実行管理を用意します。

出典：

- https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview
- https://docs.getdbt.com/docs/build/data-tests
- https://docs.getdbt.com/docs/build/unit-tests
- https://docs.getdbt.com/reference/resource-configs/contract
- https://docs.getdbt.com/docs/deploy/source-freshness

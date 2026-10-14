# 工程と遷移

| 順 | スキル | 入力 | 出力・終了条件 |
|---|---|---|---|
| 初回準備 | gdw-requirements | 依頼・Git状態 | feature.xxx確定・最新developから分岐・branch.md・案件ルート |
| 0 | gdw-bootstrap | 導入先環境 | environment.md・実行可否 |
| 1 | gdw-requirements | 依頼・既存枠 | requirements.mdの草案・一問一答 |
| 2 | gdw-investigate | 草案・対象コード | investigation.md・影響一覧 |
| 3 | gdw-estimate | 調査・草案 | estimates.md（C/B/A） |
| 4 | gdw-requirements | 調査・見積もり | 要件と受入条件の人の承認 |
| 5 | gdw-design | 承認要件・コード | design.md・test-cases.md・traceability.md |
| 6 | gdw-review-design | 固定した設計一式 | 独立レビューPASS |
| 7 | gdw-implement | 合格設計 | 実装・変更記録 |
| 8 | gdw-review-implementation | 実装・要件・設計 | 独立レビューPASS |
| 9 | gdw-tests | テストケース・実装 | UT/結合テストコード・実行ログ |
| 10 | gdw-review-tests | ケース・コード・計測結果 | 独立レビュー・網羅性・UT100% |
| 11 | gdw-verify | テスト合格・動作環境 | verification.md・主要ユースケース証跡 |
| 12 | gdw-deliver | 全証跡・差分 | コミット・PR・release.md草案。マージしない |
| 13 | gdw-release | 全検証・デプロイ計画 | 本番承認待ち→承認後デプロイ・確認 |

各工程への移動は入力の存在・現行版一致・前工程PASSを確認してから行います。設計レビューPASS後は追加の業務承認を要求せず実装へ進みます。ただしGemini・OS・組織のツール承認は迂回しません。

差し戻し：要件不足→requirements、実現性/契約/設計不足→design、実装誤り→implement、テスト不足/誤り→tests、環境障害→bootstrapまたはverify。戻り先で影響する後続成果物をSTALEにし、順に再確認します。新しいユースケースは既存要件の不足ケースか新要件かを区別し、新要件なら承認を取り直します。

3回停止の扱いはreview.md。init後の再開はgate.jsonのstage/completedとランタイムstatusから始め、既に承認された事項を繰り返し質問しません。同時に状態を更新する担当は1名に限定します。

各工程の固定入力・正本出力は各SKILL.mdの「固定の案件入力と出力」を参照。作成済みの工程MDは同じファイルへ加筆更新し、[保存・受け渡し](artifacts.md)に従う。

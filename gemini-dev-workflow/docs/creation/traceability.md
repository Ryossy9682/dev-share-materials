# 配布要件の追跡

| 要件 | 成果物 | 検証・状態 |
|---|---|---|
| REQ-01/02 | README、GEMINI.md、compatibility、全SKILL.md | 公式照合・静的検査・独立レビューPASS。実機は未検証 |
| REQ-03 | requirementsスキル、requirements/approvalひな型 | 独立レビュー・一問一答シナリオ確認 |
| REQ-04 | investigate/estimate、estimation、estimatesひな型 | C/B/A・時間・依存・未確定待ちを独立確認 |
| REQ-05/06 | design/review-design/implement/review-implementation | 入出力・要件対応・差し戻しを独立確認 |
| REQ-07 | tests/review-tests、coverage、ケース/対象ひな型 | 条件の独立確認。配布Python実装はUT行/分岐100% |
| REQ-08 | review、issues、handoff、任意reviewer | 3回・独立性・不在時待機の文書確認 |
| REQ-09 | verify、verification | 配布導入の結合3件。実アプリ動作は導入先で実施 |
| REQ-10/11 | contract/release、deliver/releaseスキル | 直接/間接禁止、push経由デプロイ、承認範囲を独立確認 |
| REQ-12 | workflow、state/resume/traceability | 段階読込・鮮度・失効・再開の独立確認 |
| REQ-13 | scripts、tests | UT19・結合3・競合時書込0・改行保持 |
| REQ-14 | README、docs/creation、Git bundle/ZIP | パッケージ検証結果は同梱PACKAGING-CHECKS.json |

## 追加要件の確認

| 要件 | 対応 | 検証 |
|---|---|---|
| REQ-12更新 | /tmp案件ルート・index/state | 静的検証・独立レビュー |
| REQ-15 | branching.md・requirements初回 | 一時Git remoteによる実コマンド検証 |
| REQ-16 | 全スキル固定入出力・artifacts | 初回/再開/独立担当の差分レビューPASS |
| REQ-17 | 同名正本と更新履歴 | 全テンプレートと各工程手順を確認 |
| REQ-18 | pr-artifacts・deliver・pr-reportひな型 | 順序・相対リンク・ハッシュ循環の独立確認 |

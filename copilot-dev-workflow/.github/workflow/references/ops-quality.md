# 品質基準の変更検出

check担当が基準Gitコミットと現在のテスト・CI・カバレッジ設定を比較する。追加/削除/変更をすべて拾い、正当な改善でも理由と人の承認を記録する。基準はbranch.mdのbase SHA。CIでは保護されたbase SHAを環境から指定し、PR側ops.jsonだけを信用しない。

```sh
python .github/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --repo /absolute/project --base BASE_SHA quality
```

既定対象はtests配下、ファイル名にtestを含むもの、snap、.github/workflows、pyproject.toml/pytest.ini/.coveragerc/tox.ini/setup.cfg/package.json/主要lock/jest.config.js/vitest.config.ts/coverage-scope.md/quality-policy.json。導入先固有の設定はops init --extraに全相対パスを追加する。意味を完全自動判定するものではないため、設定が別ファイルへ移された場合も対象を見直す。

変更時はquality.mdにdiff_hashと一覧を出して停止する。人が変更内容を確認した原文を保存し、templates/quality-approval.jsonをevidence/quality-approval.jsonに具体化する。再実行時は--inputで同ファイルを指定する。ops gateは自動で同ファイルを読む。承認後に変更するとハッシュ不一致で停止する。

CI用のquality-check.yml.exampleは導入先の環境に合わせ、保護base SHA・工程資料の取得・必須チェック名を設定して採用する。共有証跡やトークンはPRの任意コードへ渡さない。基準や検査スクリプトも変更できる主体に対する耐改ざんは、GitHubの権限・CODEOWNERS・必須チェックで補う。正当な承認があってもUT行分岐100%や独立レビューの条件は緩めない。

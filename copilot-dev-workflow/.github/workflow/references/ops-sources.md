# 参照資料の固定と更新

調査担当がMCP等で取得した原本を案件fetch/へ保存する。コードからNotion資格情報を取得しない。全必須URLをproject/profile.jsonのnotion_sourcesへ登録し、templates/source-observations.jsonの形でevidence/source-observations.jsonへ記録する。取得日時はUnix秒、更新日時は提供元の値、hashは取得ファイルのSHA256。子ページを含め、必要なページを全件列挙する。

```sh
python .github/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --input /tmp/REPO/feature.xxx/evidence/source-observations.json pin-sources
python .github/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --input /tmp/REPO/feature.xxx/evidence/source-observations.json sources
```

sources.lock.jsonとsources/以下に内容を固定し、gate.jsonの調査工程の固定入力とnotion一覧へ登録する。既存のimpactで調査以降を再確認対象にする。案件再開時は再取得し、内容・更新時刻・URL一覧を比較する。ops gateはprojectの必須URLと一致することも検査する。資料なしの場合だけ空配列を明示する。

変更検出時は自動で基準を更新しない。templates/source-change.jsonに新observations（実内容hash込み）と、人のapproval（旧lockハッシュ・新observations全体のハッシュ・理由・原文のパスとハッシュ）を記録する。新observationsのハッシュはランタイムencoded形式（sort_keys=true/indent=2/末尾改行）で計算する。

```sh
python .github/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --input /tmp/REPO/feature.xxx/source-change.json repin-sources
```

旧lockはevidenceへ退避、新本文は内容ハッシュ付き別名で保存する。全取得内容検証後に反映する。失敗時は旧lockとgateを戻す。成功後は調査・設計・後続の独立レビューをやり直す。取得時刻を書き換えるだけで再取得済みにしない。

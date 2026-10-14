# 環境診断

check担当で実施。Python/Git/CLI、21担当の明示model、担当検出、個人設定の上書き、Notion参照URL、/tmp書込みを照合する。CLIの有効版は実際に--versionで取得する。

templates/host-observations.jsonを案件のevidence/host-observations.jsonへコピーし、実ホストの担当選択・モデル表示・有効設定・資料取得ログから埋める。modelsは全21担当について実際のmodelと対応定義のSHA256を記載する。ハッシュは定義ファイルのバイト列に対して計算する。nullや未確認を推測で埋めない。logは案件内相対パス、log_hashはログのSHA256、observed_atは実取得時のUnix秒。モデル欄をコピーしただけでは観測にならない。

```sh
python .gemini/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --repo /absolute/project --input /tmp/REPO/feature.xxx/evidence/host-observations.json doctor
```

観測は24時間で失効する。モデル定義やCLI版変更も再診断。Notion未使用時だけnotion_urlsを空配列にする。必須URLはprofile.jsonのnotion_sourcesへ登録する。結果はdoctor.mdとevidence/doctor.json。チェック失敗はexit 2。ホスト証跡の本人性はこのスクリプトで保証しない。実機試験の未実行をdoctorの合格で代替しない。

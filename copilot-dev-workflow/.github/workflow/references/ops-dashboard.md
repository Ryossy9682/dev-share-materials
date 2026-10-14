# 進捗の表示

status担当で生成する。dashboard.htmlは表示用であり、承認や工程進行はできない。

```sh
python .github/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx dashboard
```

現在工程・完了工程・最後の運用ゲート結果・停止理由・次操作・issues.md・estimates.md・metrics.jsonを1ページに表示する。コード変更後の検査結果はSTALE表示。最後の結果は検査日時とともに表示し、最新検査と誤認しない。表示のためにCLIを起動したり工程状態を変更したりしない。

metrics.jsonはtemplates/metrics.jsonを使用し、各工程のestimate_hours/actual_hoursを記録する。未計測はnull。単位は1時間、比較の並びはC→B→A。人の稼働時間とAIの経過時間を混ぜない。実測値はタイマー/作業記録を根拠に更新する。

文字列はHTMLエスケープされる。外部JavaScriptや外部通信は使わない。案件資料を含むため、PR添付時は共有対象を確認する。

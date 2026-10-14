# 導入・更新・復元

新規導入はmaintenance.pyを使用する。既定は比較計画のみ。--apply時には既存ディレクトリのtargetと、新規かつtarget外のbackup絶対パスが必要。

```sh
python .gemini/workflow/runtime/maintenance.py install --source /absolute/new-distribution --target /absolute/project
python .gemini/workflow/runtime/maintenance.py install --source /absolute/new-distribution --target /absolute/project --backup /absolute/backups/install-001 --apply
python .gemini/workflow/runtime/maintenance.py update --source /absolute/new-distribution --target /absolute/project
python .gemini/workflow/runtime/maintenance.py update --source /absolute/new-distribution --target /absolute/project --backup /absolute/backups/update-001 --apply
```

導入時の正本は.gemini/workflow-install.json。管理ファイルの基準バイト列・配布内容ハッシュを保持する。3者比較でローカルのみの変更は保持し、同じファイルが配布側でも変わったら全適用を停止する。モデル設定・可変領域も勝手に上書きしない。指示ファイルの管理ブロック外は保持する。

旧版導入済みで台帳がない場合は、同じ旧版の配布をsourceに指定してadoptする。旧版のinstallerで配置された管理ブロック、または旧配布と完全一致する未マーカー指示を基準登録できる。独自追記と分離できない場合は競合として手動比較する。更新先の新版を旧版と偽ってadoptしない。

```sh
python .gemini/workflow/runtime/maintenance.py adopt --source /absolute/old-distribution --target /absolute/project --backup /absolute/backups/adopt-001 --apply
python .gemini/workflow/runtime/maintenance.py restore --target /absolute/project --backup /absolute/backups/update-001
python .gemini/workflow/runtime/maintenance.py restore --target /absolute/project --backup /absolute/backups/update-001 --apply
```

適用前にbackup/journal.jsonへ全変更のbefore/afterを保存する。書込エラー時は復元を試みる。強制終了・復元失敗時は台帳を保持し、同backupを使ってrestoreする。適用後に利用者が変更したファイルは自動復元しない。競合解消後に再計画する。同じtargetへの同時更新は禁止。結果とbackupパスを案件update.mdへ追記する。

従来scripts/install.pyは互換用途に残すが、以後の更新運用にはmaintenanceを使う。バックアップは/tmpの工程MDとは別に、消えない保存先を選ぶ。

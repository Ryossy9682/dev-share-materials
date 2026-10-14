# 実ホストによる動作試験

配布更新・モデル変更・CLI更新時に実施。実行は軽量担当、独立評価はcheck担当。認証・有料利用は導入環境に従う。ネットワークや権限を自動拡大しない。

```sh
python .gemini/workflow/runtime/evaluate.py prepare --root /tmp/gdw-evaluation-001 --source /absolute/gemini-dev-workflow
python .gemini/workflow/runtime/evaluate.py run --root /tmp/gdw-evaluation-001 --scenario questions
python .gemini/workflow/runtime/evaluate.py run --root /tmp/gdw-evaluation-001 --scenario questions --live
```

prepareは新規ルートにだけ、小さなPython課題・develop・ローカルbare remote・ワークフローを作成する。出力されたREADME.mdに従い初期設定を完了してから試験を始める。本番remoteへ接続しない。

試験順はquestions → design-rework → implementation → tests → resume。評価者が実際に質問へ回答し、承認と意図的な設計レビュー指摘を案件MDに保存する。1回のrunは1シナリオ。追加の対話はCLIで行い、ログを保存する。独立セッションでの再開を含める。試験を繰り返す場合は新しい評価ルートを使う。

各試験は終了コード・タイムアウト・要求モデル・定義ハッシュ・ホストログ・ソースハッシュ・その時点のコードと案件資料ZIPを保存する。対象ZIPとログを読む独立評価者は、templates/evaluation-review.jsonを埋める。全シナリオのdecision=PASS、具体的なreason、実モデルのホスト観測、対象記録ハッシュが必要。試験用モックで得た結果を実機結果として登録しない。

```sh
python .gemini/workflow/runtime/evaluate.py assess --root /tmp/gdw-evaluation-001 --review /tmp/gdw-evaluation-001/review.json
```

準備だけ=PREPARED、未実行/独立評価待ち=UNVERIFIED、実行失敗=FAIL、前提不足=BLOCKED、全実行と全独立評価合格=PASS。runのUNVERIFIED/FAILとBLOCKEDはexit 2。prepareのexit 0は試験合格ではない。CLI未導入の環境では実機試験未検証と明記する。

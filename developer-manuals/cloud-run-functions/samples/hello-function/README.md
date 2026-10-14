# HTTP関数サンプル

マニュアルv1.1と同じ`hello`関数です。Python 3.13、Windows PowerShell、Google Cloud CLIを前提にしています。クラウドへの配置は手動で実行します。BigQueryへの読込・書込は実装していません。

## ローカルで試す

PowerShellでこのフォルダーを開き、実行します。

```powershell
.\scripts\setup.ps1
.\scripts\test.ps1
.\scripts\start.ps1
```

別のターミナルから呼びます。サーバーはCtrl+Cで停止します。

```powershell
Invoke-RestMethod "http://127.0.0.1:8080/?name=Developer"
curl.exe -i -X POST "http://127.0.0.1:8080/"
```

正常時は`200`と`{"message":"Hello, Developer!"}`、POSTは`405`です。スクリプトの実行が会社のポリシーで禁止されている場合、マニュアルの個別コマンドを使用し、実行ポリシーは変更しないでください。

## クラウドへ配置する

開発用プロジェクトで課金とArtifact Registry・Cloud Build・Cloud Run・LoggingのAPIを有効化し、デプロイ・ビルド・実行用SAの権限をマニュアルに従って準備します。

```powershell
Copy-Item deploy.config.example.json deploy.config.json
```

`deploy.config.json`の`projectId`と`runtimeServiceAccount`を実際の値に変更し、配置先を確認します。実行用SAは作成済みである必要があります。

```powershell
gcloud auth login
.\scripts\deploy.ps1
```

デプロイは認証必須・リクエストベース課金で行います。スクリプトはAPIの有効化やIAM権限付与を行いません。呼び出す開発者には、対象サービスに対する`roles/run.invoker`を設定担当者が付与します。その後、次で確認します。

```powershell
.\scripts\invoke-cloud.ps1
```

`--project`を指定するためgcloudの既定プロジェクトを変更しません。デプロイのCPU・メモリ・同時実行等は設定ファイルで管理します。`concurrency`を増やす場合、実行スレッド数とスレッド安全性も確認してください。設定例は最安値を保証するものではありません。

## 応答時間を測る

ローカルサーバーを起動した状態で、次を実行します。

```powershell
.\.venv\Scripts\python.exe .\scripts\measure.py --count 10
```

クラウドの場合は実際のサービスURLを指定します。

```powershell
.\.venv\Scripts\python.exe .\scripts\measure.py `
  --url "https://YOUR_SERVICE_URL/?name=Developer" --cloud-auth --count 10
```

指定URLは`name=Developer`のGETで成功するサンプル用です。CSVは`results/latency.csv`へ保存します。同じ出力ファイルは上書きするため、比較では`--output results/config-a.csv`などで分けます。最大1,000件の逐次呼び出しで、並行負荷試験ではありません。クラウド呼び出しには費用が発生する可能性があります。

計測値は通信を含むクライアント側応答時間です。課金対象時間ではありません。少数件のp95は参考値で、初回の呼び出しがコールドスタートだったかもこのスクリプトでは判定しません。Cloud Monitoring、Cloud Billing、外部API費用を別途確認し、`cost-comparison.template.csv`へ比較結果を記入します。このあいさつサンプルでは、重複を除いた業務処理件数は計測できません。

## 構成と公式参照

- `main.py`：マニュアルと同じHTTP関数。
- `requirements.txt`：Functions Frameworkのバージョン指定。
- `scripts/`：セットアップ、起動、テスト、配置、呼び出し、逐次計測。
- `tests/`：HTTPステータス、JSON、空白、日本語、50/51文字の境界テスト。
- `.gcloudignore`：テスト・設定・仮想環境等をアップロード対象から除外。
- `cost-comparison.template.csv`：コスト比較の記録用ひな形。

出典：

- https://github.com/GoogleCloudPlatform/functions-framework-python
- https://docs.cloud.google.com/run/docs/deploy-functions
- https://docs.cloud.google.com/run/docs/authenticating/developers
- https://docs.cloud.google.com/run/docs/tips/services-cost-optimization
- https://docs.cloud.google.com/run/docs/about-concurrency
- https://cloud.google.com/run/pricing

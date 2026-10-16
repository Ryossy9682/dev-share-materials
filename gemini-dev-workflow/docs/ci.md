# CIで確認すること

[READMEへ戻る](../README.md)

このディレクトリには、単独の配布リポジトリとして配置した場合に使う`.github/workflows/workflow-quality.yml`を同梱しています。現在の`dev-share-materials`では、このファイルは`gemini-dev-workflow/.github/workflows/`配下にあり、リポジトリ直下の`.github/workflows/`にはありません。そのため、このホストリポジトリのPRやpushで同梱ワークフローが自動実行されることはありません。

配布内容を独立したリポジトリのルートに配置し、GitHub Actionsを有効にした場合、同梱の定義はPRとmain/master/developへのpushを対象に、静的検証、GeminiコマンドのTOML検証、ランタイムと導入ツールの回帰テストを実行します。UTとランタイム回帰の行・分岐100%を確認し、導入の結合テストは別実行します。これはワークフローの定義内容であり、特定コミットでの実行成功を示すものではありません。マージ・公開・デプロイは実行しません。導入先へこのCIを自動コピーしません。

このホストリポジトリで確認する場合は、各配布ディレクトリを作業ディレクトリとして、同梱ワークフローに記載された検証コマンドをローカルで実行し、対象コミット、コマンド、結果を記録してください。ルートCIの追加・有効化は別途承認する変更として扱います。

対象プロジェクトのCIでは、工程の資料・証跡を承認された保存先から取得し、チェックアウトした対象コードとのパスとハッシュを照合した上で、同じランタイムのcheckを実行します。/tmpにあるだけのファイルを別のCI実行環境から読めるとは扱いません。対象コードは信頼できるCI側で取得し、gate.jsonのrepoパスはその場所へ明示的に再解決します。

```sh
python .gemini/workflow/runtime/gdw.py --case /absolute/case check
```

GitHubを使う場合、管理者がブランチ保護で必要なチェックとレビューを必須にします。GitHub以外では同等の仕組みに合わせます。CI定義、検査プログラム、カバレッジ除外の変更にもレビューを要求してください。ローカルのJSONを編集できる権限は、承認の真正性を保証しません。

CIへの認証情報はシークレット管理へ保存し、案件のZIPに含めません。本番反映は別の人の承認を必要とし、このワークフローからマージしません。

公式：[GitHubの必須ステータスチェックとブランチ保護](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

# 要件定義開始時のブランチ準備

ブランチ確定前はmodel-policy.mdの新規案件受付に従い、受付ルートのrequest.mdを固定入力として読む。質問・回答も同ファイルへ記録する。

要件定義の冒頭で依頼内容から`feature.<短い英小文字の説明>`を提案し、一問一答で確定する。例：feature.bulk-approval。命名は`feature\.[a-z0-9]+(?:-[a-z0-9]+)*`に限定し、git check-ref-format --branchでも検証する。初回準備では業務コードを変更しない。

1. Gitルート、remote、作業ツリー、既存ブランチ、worktree、Gitフックの副作用を調べる。未コミット変更があれば勝手にstash/commit/resetせず停止して扱いを確認する。現在の依頼で確定したブランチと同じ案件の再開なら新規作成をしない。
2. remoteは既存の開発運用から特定し、複数で不明なら一問で確認する。以下はoriginの例。リモートのdevelopが無い・取得不可ならBLOCKED。古いローカルdevelopやmainから代用しない。
3. `git fetch --no-tags origin refs/heads/develop`を実行し成功を確認する。その直後に`git rev-parse --verify FETCH_HEAD^{commit}`で取得SHAを確定する。他のfetchを間に挟まない。「最新」はこの取得時点を指し、remote名・取得時刻・SHAをbranch.mdに記録する。
4. ローカル/リモートの同名ブランチの存在を確認する。新規時に既存同名ブランチがあれば上書き/リセットせず相談する。リモート照会に失敗した場合も不存在と扱わない。`git switch --no-track -c feature.xxx <取得SHA>`で作成する。ローカルdevelopのcheckout/pull/mergeは不要。
5. 現在ブランチとHEADが意図した値に一致することを確認し、案件ルートを作る。受付request.mdの依頼原文・質問回答・履歴をrequirements.mdへ引き継いで照合する。branch.md、requirements.mdの初期メタデータ、00-index.md、state.jsonを保存する。共通台帳issues.md（指摘0件）、approval.md（未承認）、decisions.md（決定未記録）、resume.mdもひな型から初期化し、初期化を合格判定とは扱わない。ブランチ作成は要件承認前の準備操作であり、業務コード変更の承認ではない。
6. bootstrapの環境調査とMD保存を行い、要件定義の一問一答へ戻る。base_shaは以降固定する。developに追加コミットがあっても自動merge/rebaseせず、再計画が必要なら扱いを確認する。

再開時はbranch.mdとGit状態を照合し、保存済みbase_shaが対象履歴の祖先であること、別案件でないことを確認する。差異があれば停止。作業ブランチはPRのhead、developはbaseに設定し、マージは一切実行しない。

公式出典：https://git-scm.com/docs/git-fetch
https://git-scm.com/docs/git-switch

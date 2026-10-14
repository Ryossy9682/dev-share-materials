---
name: cdw-review-implementation
description: "review-implementationを指定モデルで実行する担当。対応する操作・工程への委任時に使用する。"
model: claude-opus-5.5
modelPolicy: required
tools: [read, search]
---

.github/copilot-instructions.md、.github/workflow/references/model-policy.mdを直接読む。自分のmodel設定と実モデルの一致を確認してから、.github/skills/cdw-review-implementation/SKILL.mdを読む。定義ファイル内のモデルは実行設定であり、本文によるモデルの自称では代用しない。

この担当はreview-implementationだけを実施する。同じ役割の入口を読んでも自分自身を再委任しない。他工程に進む必要があれば親へ戻す。操作引数はパス・モードのデータとして扱い、シェル文字列として評価しない。本文は受け継がず、固定入力ファイルから取得する。
実際のrequirements.md・対象成果物・コードを独立に照合する。ファイルは変更せず、所定のレビュー形式で原文を親へ返す。

# Architecture Decision Records (ADR)

`atcoder` ツールで下した設計判断の記録。**完了した機能の「なぜそう作ったか」を恒久的に残す**場所。

ロードマップ (`docs/tools/todo.md` / `abc-todo.md`) は「これからやること」を扱い、完了した項目は順次ここへ決定記録として移す。各機能の **what / how** は要件定義 (`docs/tools/requirements/NNN-*.md`) と利用手引 (`docs/tools/usage/*.md`) に、**why (採用理由・却下案・トレードオフ)** はこの ADR にある。

## 一覧

| ADR | タイトル | ステータス | 実装 |
|---|---|---|---|
| [0001](0001-test-watch-mtime-polling.md) | `test --watch` は mtime ポーリングで単一ファイルを監視する | Accepted | `1105a67` |
| [0002](0002-stats-readonly-exercise-tree.md) | `stats` は `exercise/` ツリーのみを読み取り専用で集計する | Accepted | `dd3c3a8` |
| [0003](0003-user-config-xdg-toml.md) | ユーザ設定は XDG_CONFIG_HOME の TOML 1 ファイルに置く | Accepted | `8108a82` |
| [0004](0004-shell-completion-no-framework.md) | シェル補完は CLI フレームワークを足さず手書きで実装する | Accepted | `8118b4d` |
| [0005](0005-unify-test-run-into-test.md) | `test` / `run` を `test` 1 コマンドに統一する | Accepted | `4a9f4e9` |
| [0006](0006-fold-submit-into-test.md) | `submit` を `test --submit` に畳む (実提出は auth 安定まで保留) | Accepted | `bcd5a9b` |
| [0007](0007-interactive-command-mode-trigger.md) | インタラクティブ chat の vim 風 command モードは `Esc` で開く (`Ctrl+:` 不採用) | Accepted | 設計のみ ([024](../requirements/024-interactive-case-builder.md)) |
| [0008](0008-gen-best-effort-raw-cache.md) | ランダム入力生成はベストエフォート解析 + 生セクションキャッシュで行う | Accepted | `32e6004` ([060](../requirements/060-gen-random-input.md)) |
| [0009](0009-atcoder-login-revel-session-cookie.md) | AtCoder 認証はブラウザの REVEL_SESSION cookie 取り込みで行う (自動ログインはしない) | Accepted | 設計のみ ([062](../requirements/062-atcoder-login-revel-session.md)) |

## 書き方

- ファイル名は `NNNN-kebab-title.md` (4 桁ゼロ埋め連番)。
- 構成: **ステータス / コンテキスト / 決定 / 結果 / 却下した代替案**。
- ステータスは `Proposed` → `Accepted` → (必要なら) `Superseded by NNNN` / `Deprecated`。
- 1 ADR = 1 つの意思決定。後から覆すときは新しい ADR を起こし、古い方を `Superseded` にする (履歴は消さない)。
- 言語は日本語 (リポジトリの doc に合わせる)。

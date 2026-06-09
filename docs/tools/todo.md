# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

> このファイルは**これからやること**だけを残す。完了した項目は決定記録 (ADR) に移している:
> 採用理由・却下案・トレードオフは [`docs/tools/decisions/`](decisions/) を、機能の使い方は `docs/tools/atcoder-*-usage.md` を、仕様は `docs/tools/requirements/NNN-*.md` を参照。
>
> 完了済み (ADR 化済み): I. `test --watch` ([ADR 0001](decisions/0001-test-watch-mtime-polling.md)) / J. `stats` ([ADR 0002](decisions/0002-stats-readonly-exercise-tree.md)) / ユーザ設定ファイル ([ADR 0003](decisions/0003-user-config-xdg-toml.md)) / `completion` ([ADR 0004](decisions/0004-shell-completion-no-framework.md))。
>
> 完了済み (要件のみ): `stats --graph` 草表示 (contribution graph)。レベルはローカルのレター重み (`a`=1…`g`=7) で算出し、オフライン・読み取り専用を維持 ([要件 011](requirements/011-stats-graph.md))。

## H. エディタ・テンプレート連携

### 解きたい問題

- 練習でも本番でも、新規問題ファイルを開いた直後はいつも同じ boilerplate (`import sys; input=sys.stdin.readline`、`from collections import defaultdict` 等) を書くことになり、書き始めまでの摩擦が大きい。
- 練習用の `atcoder new` は当日 dir を mkdir するだけで、ファイルは生成していない。

### 決めること

- テンプレートの所在
  - 候補 1: リポジトリ内 `templates/python.py` (git で履歴管理、共有しやすい)
  - 候補 2: `$XDG_CONFIG_HOME/atcoder-daily-training/templates/python.py` (個人設定として分離)
  - 第一候補は **リポジトリ内**。1 人のリポジトリなので個人設定と区別する利得は薄い。
- テンプレート選択方法
  - 候補: `atcoder new --task d --template default` のように名前指定。デフォルトは "default"。
  - 言語ごとに複数テンプレート (`python_basic.py`, `python_io_fast.py` 等) を持てるようにする。
- 既存ファイルとの衝突
  - 既にファイルがある場合は上書きしない (確認プロンプトもしくは `--force` で上書き)。
- どのコマンドから生成されるか
  - `atcoder new --task d`: 当日 dir に `<task>.py` を生成 (現状は dir のみ作成)
  - ABC 本番対応 (`abc-todo.md` の B) の `contest prepare` でも内部的にこのテンプレート生成を呼ぶ
- テンプレート内の変数展開 (`{{task}}`, `{{contest}}`, `{{date}}` 等を埋め込むか、純粋なテキストか)
- テンプレートの形式 (Go の `text/template` 等を使うか、単純文字列か)

### 影響範囲

- 新規 `templates/` ディレクトリ
- 新規 `internal/template/` パッケージ
- `cmd/atcoder/new.go` の拡張
- ABC ロードマップの B (contest prepare) と接続

### 関連項目

- `abc-todo.md` の B (コンテストメタの取り扱い): contest prepare の中で全タスクのスケルトンを一括生成する。テンプレート機構をそこから呼べるようにしておく。

## K. 提出ジャッジ状況の確認 (`atcoder status`?) ⚠ 認証必須 (調査済み・保留)

### 解きたい問題

- `atcoder submit` は提出ページをブラウザで開くだけで、提出後の verdict (`WJ` → `AC`/`WA`/`TLE`/`RE`/`CE`) はブラウザに切り替えて自分で確認している。「今出したファイルの今のジャッジ結果」をターミナルから確認できると往復が消える。

### 調査結論 (2026-06-09): 実用版は**認証 (ログインセッション) が不可避**

実現可能性を着手前に調べた結果、「直前に提出したファイルのリアルタイム verdict」を満たすには AtCoder へのログインが必須と判明したため、設計には進まずここに保留する。

- **公式の提出/ジャッジ状況 API は存在しない。** 取得手段は公開ページのスクレイピングか非公式 API のみ。
- **コンテスト開催中の自分の提出は非公開** (本人のみ閲覧可)。自分の提出一覧 `/contests/<contest>/submissions/me` は**ログイン必須**。リアルタイムに verdict を取るにはセッション cookie (`REVEL_SESSION`) + CSRF トークンが要る (`online-judge-tools` / `atcoder-cli` と同方式)。
- **認証なしで取れるのは「コンテスト終了後の公開提出」だけ**で要件を満たさない:
  - 終了後は個別提出 `/contests/<c>/submissions/<id>` や全提出 `?f.User=<user>` が公開されスクレイプ可能。ただし (1) コンテスト中は不可 (2) submission ID を別途知る必要がある。
  - kenkoooo の AtCoder Problems API (`https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user=<user>&from_second=<unix>`, 認証不要) も使えるが、**バッチクロールで遅延** (即時性なし)・**コンテスト中の提出は含まない**。
- **現状方針との衝突**: `cmd/atcoder/submit.go` は「実際の提出は認証が必要なためブラウザ側に委ねる」と明記し、認証情報を一切持たない設計。本機能を実用レベルで作ると **repo 初の認証情報ハンドリング**になる。ここがこの TODO を保留にする最大の理由。

### 認証を入れて進める場合に決めること (将来検討)

- ログイン方法: `atcoder login` サブコマンドを追加し、ユーザ名/パスワード → `/login` の CSRF フロー → `REVEL_SESSION` cookie を取得。
- 認証情報・cookie の保存場所: `$XDG_CONFIG_HOME/atcoder-daily-training/session` 等。平文 cookie の扱い・パーミッション・`.gitignore` 対象化。
- ステータス取得経路: `/contests/<contest>/submissions/me` を認証付き GET → 提出テーブルをパースして最新 (またはタスク指定) の verdict を表示。`WJ`/`Judging (n/m)` の途中状態を polling して `--watch` 的に確定まで待つか。
- 利用規約・rate limit: 短間隔 polling は負荷になるため最小間隔を設ける (既存 fetch と同様 User-Agent 明示)。
- `submit` との連携: `atcoder submit` 後に submission ID を控え、そのまま `status` で結果を追える導線。

### 認証なしで妥協する代替案 (要件は下がる)

- **post-contest 限定の確認のみ提供**: 終了済みコンテストについて kenkoooo API か公開提出ページから直近の verdict を表示。コンテスト中・即時確認は非対応と明記する。練習 (`exercise/`) 用途には部分的に有効。

### 影響範囲 (認証版を作る場合)

- 新規 `cmd/atcoder/login.go`, `cmd/atcoder/status.go`
- 新規 `internal/atcoderauth/` (ログイン・cookie 永続化・認証付き HTTP クライアント)
- `internal/testexec/fetch.go` 相当のパース層に提出テーブル抽出を追加
- `cmd/atcoder/main.go` (dispatch + usage)
- `.gitignore` (session ファイル除外)

### 関連項目

- `cmd/atcoder/submit.go` (認証を避けブラウザ委譲している現状の設計判断)。
- `abc-todo.md` の本番対応 (E: 本番モード判定) と接続しうる: 本番中の verdict 確認はそこと相性が良い。

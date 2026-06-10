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

## N. コマンド alias (git 風) ✅ DONE

### 解きたい問題

- `atcoder update --local` のような **よく打つが長いコマンド**を短い名前で呼びたい。git の `[alias]` (`git co` = `git checkout`) と同じ使い勝手が欲しい。既存の `config.toml` の延長で実現したい。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/016-config-alias.md`](requirements/016-config-alias.md)、利用手引は [`atcoder-config-usage.md`](atcoder-config-usage.md)。

- `config.toml` の `[alias]` セクションに `名前 = "コマンド列"` を書き、`atcoder <名前> [追加引数]` をそのコマンド列に展開して実行 (追加引数は後ろに連結)。例: `alias.upd-lo = "update --local"` → `atcoder upd-lo`。
- 管理は既存 config 経由 (`config set/get/show alias.<name>`) + **汎用 `config unset <key>` を新設** (削除・typed キーのリセット兼用)。
- **組み込みサブコマンドが常に優先** (git 流)。alias は未知名のときだけ解決、組み込み名の alias は無視 (set 時に警告)。alias→alias は再帰展開しループは exit 2。値は空白区切り (クォート対応は将来)。
- 既存サブコマンドの解決・挙動・exit code は不変。新規 `internal/alias` (展開の純粋関数) + `internal/config` 拡張 + dispatch 前段に展開を 1 つ挟むだけ。

### 影響範囲

- 新規 `internal/alias/` (Expand: 再帰展開・ループ検出・組み込み優先)
- `internal/config/` (`[alias]` スキーマ・`alias.*` の set/get/show・`Unset`)、`cmd/atcoder/{main,config}.go` (展開・`unset`)
- `internal/complete/` (alias 名をサブコマンド候補に・`unset` 候補)、`fixtures/run.sh`、`docs/tools/atcoder-config-usage.md` (新規)

### 関連項目

- config 基盤は要件 007 / ADR 0003、補完登録は 008 / 012、主目的の `update --local` は 013。

## L. ツール自己更新 (`atcoder update` / `version`) ✅ DONE

### 解きたい問題

- ツールはこのリポジトリの `cmd/atcoder` を `go install` した `atcoder` として使うが、機能追加が進む中で**手元のバイナリが古いまま**になりやすい。「今入っているのはいつのコミットか」「最新が出ているか」を確かめる手段が無く、毎回 `cd` してリポジトリで `git pull && go install ./cmd/atcoder` するのは摩擦。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/013-atcoder-self-update.md`](requirements/013-atcoder-self-update.md)、利用手引は [`atcoder-update-usage.md`](atcoder-update-usage.md)。

- `atcoder version` で現在版 (Go 自動埋め込みの commit sha・日時・dirty) を**オフライン表示**。`atcoder update` で最新版に入れ替え、`atcoder update --check` は確認のみ (インストールしない)。
- **更新元は GitHub (module proxy)**。`go install <module>/cmd/atcoder@latest` を Go ツールチェインに委譲し、どの cwd からでも動く。`go list -m -json <module>@latest` で最新を解決。
- **版の持ち方は Go の自動 VCS スタンプ** (`runtime/debug.ReadBuildInfo`)。git タグ運用・`-ldflags` は行わない (リリース作業ゼロ)。
- 触るのは**自分自身のバイナリのみ**。解答・キャッシュ・設定・git・AtCoder には一切触れない。`go` 必須・`version` 以外はネットワーク必須。
- exit code 規約踏襲 (引数誤り=2 / 解決・install 失敗=1 / 成功=0)。`--check` は成功なら更新有無に関わらず 0。

### 影響範囲

- 新規 `cmd/atcoder/{version,update}.go`, `internal/selfupdate/` (バージョン取得・最新解決・install)
- `cmd/atcoder/main.go` (dispatch + usage)、`internal/complete/` (`version`/`update`/`--check` 補完)
- `fixtures/run.sh` (version=exit 0・update 引数誤り=exit 2。ネットワーク経路は GOPROXY オフ等で固定)
- `docs/tools/atcoder-update-usage.md` (利用手引・新規)

### 関連項目

- 補完への登録は要件 008 / 012。CLI 名 `atcoder` 化と `go install ./cmd/atcoder` 前提は要件 006。

### 残し (優先度: 低)

- **go ツールチェインに依存しない更新経路**。現状の `update` は `go install …@latest` に委譲するため、利用環境に `go` が必要。`go` 無しでも更新できるよう、GitHub Releases のプリビルドバイナリを取得して自身を差し替える経路を将来用意する (OS/arch 判定・ダウンロード・実行ファイルの atomic 置換・チェックサム検証が要る)。要件 013 の「将来の拡張ポイント」にも記載。リリースを発行する運用が前提になるので、当面は優先度低め。

## K. 提出ジャッジ状況の確認 (`atcoder status` / `login`) ❌ 撤去 (実現不可)

### 経緯と撤回理由 (再着手しないこと)

一度 `atcoder login` / `logout` / `status`（認証付きで `/submissions/me` を取得し verdict 表示）を実装したが、**実現不可と判明し全削除した**。理由:

- **AtCoder のログインページは Cloudflare Turnstile (ボット対策) で保護されている。** ブラウザが JS で生成する検証トークン (`cf-turnstile-response`) が無いと、正しい username/password でも認証が拒否される（→ 汎用エラー `Error.`）。`online-judge-tools` 等の既存ツールも同条件では programmatic ログイン不可。
- 回避策としてブラウザの `REVEL_SESSION` cookie を取り込む方式（`--session-cookie` 等）も実装したが、毎回 DevTools から cookie を手でコピーする運用が重く、利用者判断で**機能ごと不要**となった。
- **認証なし経路も不可:** AtCoder の提出一覧はログイン必須で列挙できず、kenkoooo AtCoder Problems API は反映まで約 5 分の遅延・コンテスト中の提出を含まない・第三者依存。即時性が要る用途に合わない。

要件・利用手引・実装（`cmd/atcoder/{login,status}.go`、`internal/atcoder/`、`config.SessionPath`、補完・fixture）は削除済み。再挑戦する場合は **Turnstile を解けるブラウザ自動化**が前提になる点に注意。

## M. 練習コンテスト一覧 (`atcoder review <category>`) ✅ DONE

### 解きたい問題

- `exercise/` に積み上げた解答を「どのコンテストの・どのレターを・最後にいつ解いたか」の粒度で振り返れない。`stats` は集計値 (総数・ストリーク・カテゴリ別・草) は出すが、コンテストを 1 つ 1 つ列挙はしない。

### 決まったこと

> 要件詳細は [`requirements/014-exercise-review.md`](requirements/014-exercise-review.md)、利用手引は [`atcoder-review-usage.md`](atcoder-review-usage.md)。

- **別サブコマンド** `atcoder review <category>` にする (`stats` のサブモードにはしない)。`stats = 集計値 / review = 列挙` と責務を分け、データ層 (`internal/stats` の `Scan`/`Solve`/`Period`) は流用する。
- カテゴリは **必須の位置引数** (`atcoder review abc`)。出力は **contest × letter のテーブル**に各コンテストの**最終解答日**を添える。contest 番号降順。
- **ABC は a–g を固定列**にして未着手の穴を `·` で見せる (他カテゴリは解いた letter の和集合)。各マスは **recency を色の濃淡で表現** (最近=明るい緑・古い=暗い緑、`stats --graph` の色ランプを流用)。
- 読み取り専用・オフライン・決定的。exit code 規約 (引数誤り=2 / I/O 失敗=1 / 0 件含む成功=0)。`stats` の期間フラグ (`--week/--month/--year/--last`) を任意で流用。
- **集計対象は 2 ツリー横断**: `exercise/` (日付あり) + `<category>/<num>/<letter>.py` カテゴリツリー (`abc/`/`arc/`/`awc/`、日付なし) を contest_id でマージ。日付なしマスは中立色 `■`・last solved `—`、期間フィルタ時は除外 (案 A)。
- 要件詳細: [requirements/014-exercise-review.md](requirements/014-exercise-review.md)。

### 影響範囲 (実装済み)

- 新規 `cmd/atcoder/review.go` + `internal/review/` (`Build`/`recencyLevel`/`Render`)。`internal/stats` に `Solve.Contest` 追加・公開ヘルパ `InWindow`/`WindowLabel`/`ShadeGlyph` を追加 (既存挙動は不変)。`main.go` usage・`internal/complete` (サブコマンド + カテゴリ位置引数補完)・`fixtures/run.sh`・`docs/tools/atcoder-review-usage.md`。

## O. 既定レイアウト (`config` の `layout` キー + `ATCODER_LAYOUT`) ✅ DONE

### 解きたい問題

- レイアウト (`auto`/`abc`/`exercise`) は `atcoder test` で `--layout` (デフォルト `auto`) を都度指定する。**ある期間ずっと特定レイアウトで作業したい**ときに毎回フラグを打つのが煩わしく、既定値を固定する手段が無い。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/017-config-layout-default.md`](requirements/017-config-layout-default.md)、利用手引は [`atcoder-config-usage.md`](atcoder-config-usage.md)。

- 既定レイアウトを **環境変数 `ATCODER_LAYOUT`** と **`config.toml` の トップレベル `layout` キー**の 2 段で持つ。解決順は `--layout` フラグ > `$ATCODER_LAYOUT` > `config.toml` の `layout` > `auto`。precedence は純粋関数 `layout.Resolve` に集約。
- **専用 `layout` サブコマンドは作らず**、既存の汎用 `config` (要件 009) に `layout` を string enum キーとして登録。`atcoder config get/set layout` で扱う。当初の旧ブランチ案 (`atcoder layout show/set/unset`) は 009 の汎用 config と重複するため不採用。
- `--layout` のデフォルトを `"auto"`→`""` (未指定) に変更し、空なら env/config にフォールバック。env・config 未設定なら従来挙動と完全一致 (後方互換)。
- 既知レイアウト名は `layout.Names()` に集約 (検証・補完の単一情報源)。`config set layout` の不正値は `ErrInvalidValue` で exit 2、読み取り側 (`atcoder test`) は config を読むだけで解答に触れない。

### 影響範囲 (実装済み)

- `internal/layout/` に `Names`/`Known`/`Resolve` 追加。`internal/config/` に `Config.Layout` トップレベルキー・`keys.go` の `layout` enum エントリ (`field.cands`)。`cmd/atcoder/flags.go` に `resolveLayout` + `ATCODER_LAYOUT` 定数、`test.go` を `resolveLayout` 経由に、`main.go` usage 更新。`fixtures/run.sh` に precedence smoke、`docs/tools/atcoder-config-usage.md` に `layout` 追記。

## P. 着手コマンド (`atcoder start`) ✅ DONE (181cbd2)

### 解きたい問題

- 1 問始めるたびに「ディレクトリを作る → `<task>.py` を作る → `atcoder test ... --watch` を叩く」を手作業で繰り返している。1 コマンドで済ませたい。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/018-start-command.md`](requirements/018-start-command.md)、利用手引は [`atcoder-start-usage.md`](atcoder-start-usage.md)。

- `atcoder start <contest> --task <task>` で、レイアウトに応じた解答ファイルを (無ければ) 空ファイルで作成 → そのまま `test --watch` の編集ループに入る。既存の `layout`/`testexec`/`watch` を束ねる薄い orchestration で、新しい実行・判定ロジックは増やさない。
- `--until-pass` で **サンプル全通過時に watch を終了** (exit 0)。既定は付けず `Ctrl+C` 終了 (`test --watch` と同じ)。
- 解答ファイルは既存を温存 (上書きしない)。watch は **TTY 必須** (非 TTY は exit 2、ただしファイル作成は先に済ませる)。

### 影響範囲 (実装済み)

- 新規 `cmd/atcoder/start.go` (`cmdStart` + `ensureSolutionFile`)。`cmd/atcoder/test.go` の `runTestWatch` に `untilPass` 引数追加。`main.go` の dispatch / `builtins` / usage、`internal/complete/` に `start` 追加、`fixtures/run.sh` にスケルトン生成 + 非 TTY 拒否 smoke、`docs/tools/atcoder-start-usage.md` 新規。

# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

> このファイルは**これからやること**だけを残す。完了した項目は決定記録 (ADR) に移している:
> 採用理由・却下案・トレードオフは [`docs/tools/decisions/`](decisions/) を、機能の使い方は `docs/tools/atcoder-*-usage.md` を、仕様は `docs/tools/requirements/NNN-*.md` を参照。
>
> 完了済み (ADR 化済み): I. `test --watch` ([ADR 0001](decisions/0001-test-watch-mtime-polling.md)) / J. `stats` ([ADR 0002](decisions/0002-stats-readonly-exercise-tree.md)) / ユーザ設定ファイル ([ADR 0003](decisions/0003-user-config-xdg-toml.md)) / `completion` ([ADR 0004](decisions/0004-shell-completion-no-framework.md))。
>
> 完了済み (要件のみ): `stats --graph` 草表示 (contribution graph)。レベルはローカルのレター重み (`a`=1…`g`=7) で算出し、オフライン・読み取り専用を維持 ([要件 011](requirements/011-stats-graph.md))。

## AL. task URL 直指定の DL / meta 編集 (`atcoder meta`) ✅ DONE (94d8937, url override: 後続コミット)

> 要件詳細は [`requirements/046-meta-command.md`](requirements/046-meta-command.md)。利用手引は [`atcoder-meta-usage.md`](atcoder-meta-usage.md)。サンプル取得・キャッシュの元仕様は [`requirements/001-exercise-test.md`](requirements/001-exercise-test.md)。

### 決まったこと (この項目で実装したこと)

- `atcoder meta <fetch|show|set>` を新設。問題ページの **task URL を位置引数で直接渡す**だけで contest_id / task_id を抽出し (URL は `https?://` 有無・`?lang=ja` 等を許容)、`--task` 無しでサンプル + Time Limit をキャッシュへ落とせる。contest + `--task` 指定も併用可。
- `fetch` は既存 `testexec.EnsureTests(..., refresh=true)` を再利用した強制再取得 (キャッシュのみ書き換え。解答ファイル・`tests-extra/` には触れない)。`show` はキャッシュ済み `meta.toml` の表示、`set --time-limit <dur>` は Time Limit の手動上書き。
- **url override** (`set --url <url>`): task_id が contest と食い違う問題 (例: abc111 の D = `arc103_b`) のために、解答スロット (contest/task = `abc111_d`) を保ったまま取得元 URL を meta.toml に記録する。`test` / `start` / `meta fetch` の取得経路 (`ensureTests`) がこの url を尊重するので、`atcoder test abc111 --task d` がそのまま正しいページから取得する。url override はスロット未キャッシュでも記録できる (空 meta を作って後で fetch)。
- URL パースは `internal/layout` の `ParseTaskURL` / `IsTaskURL`、取得元 URL の解決は `internal/testexec` の `DefaultTaskURL` / `resolveFetchURL`、meta 読み書きは公開 API (`Meta` / `LoadMeta` / `SaveMeta` / `SampleCount`) に集約。exit code 規約は引数誤り=2・未キャッシュ/fetch 失敗=1・成功=0。

### 影響範囲 (実装済み)

- `cmd/atcoder/meta.go` (**新規**)、`cmd/atcoder/main.go` (`builtins`/dispatch/`usage`)、`internal/layout/layout.go` (`ParseTaskURL`/`IsTaskURL`)、`internal/testexec/{meta,test,fetch}.go` (`meta`→`Meta` 公開化 + ラッパー、`fetchProblem(url)` 化 + `DefaultTaskURL`/`resolveFetchURL`、`ensureTests` の url override 尊重)、`internal/cliargs/cliargs.go` (`--time-limit`/`--url` を値フラグに)、`internal/complete/complete.go` (`meta` 候補)。テスト: `internal/layout/layout_test.go` (`TestParseTaskURL`/`TestIsTaskURL`)、`internal/testexec/fetch_test.go` (`TestResolveFetchURL`)、`fixtures/run.sh` (meta スモーク群)。docs: `atcoder-meta-usage.md` (新規)。

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

## Q. interactive モードの出力タイミング表示 ✅ DONE

### 解きたい問題

- `test --interactive` (chat TUI) では解答とのやり取りは見られるが、**応答の速さ (レイテンシ) が分からない**。入力を送ってから出力が返るまでの時間・連続出力の間隔をひと目で把握したい (TLE 気味の対話解法に気づける)。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/019-interactive-output-timing.md`](requirements/019-interactive-output-timing.md)、利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md)。

- 子の出力行が届くたびに、**直前イベント (最後の入力送信 or 直前の出力) からの経過時間**を行頭に dim で添える。応答レイテンシと出力間隔が同じ「直前イベントからの経過」として可視化される。
- 計測は **UI 層 (`internal/ui/chat.go`) のみ**。受信時刻は scanner が行を返した瞬間に記録。書式はコンパクト適応 (`2.34s`/`12ms`/`340µs`)。常時表示 (トグルは将来)。
- 子プロセス・judge・解答・バッチ test には不干渉。新フラグ無し。`formatDur` と経過算出は純粋関数でユニットテスト。

### 影響範囲

- `internal/ui/chat.go` (経過の計測・表示)、新規 `internal/ui/chat_test.go`
- `docs/tools/atcoder-test-{usage,architecture}.md` (interactive の説明に追記)

## S. 対話モードのファイル変更リロード ✅ DONE

### 解きたい問題

- `test --interactive` の chat に入っている間は解答ファイルの監視が止まり、コードを直しても一度 chat を抜けて入り直さないと反映されない。`start` は chat の外側でしか watch していない。chat の中で保存→即最新版で対話、を回したい。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/052-interactive-watch-reload.md`](requirements/052-interactive-watch-reload.md)、利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md)。

- chat TUI (TTY) に `internal/watch` の mtime ポーリング (200ms / debounce 120ms) を統合。**解答ファイルの保存を検知したら、実行中の子を kill して最新ファイルで再 spawn** し、`(解答ファイルが更新されました — 新しいプログラムを起動します)` を出す。**常時有効** (chat に入っている間)。
- mid-session で子を差し替えても旧 stream の残響で状態が壊れないよう、`readLineCmd` に **epoch (= sessionN)** を持たせ、Update が不一致メッセージを破棄する。`restart()` は kill→wait→spawn に。
- `WatchPath` を `runChatMode` → `ChatHeader` 経由で UI に渡すだけ。judge・バッチ test・非 TTY passthrough には不干渉。`Ctrl+D` 終了予約中はリロードしない。

### 影響範囲

- `internal/ui/chat.go` (watcher・epoch・fileChangedMsg・pollWatchCmd)、`internal/ui/chat_test.go`
- `internal/runexec/runexec.go` (`ChatHeader.WatchPath`)、`cmd/atcoder/adhoc.go` (受け渡し)
- `docs/tools/atcoder-test-{usage,architecture}.md`

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

> 要件詳細は [`docs/tools/requirements/050-atcoder-self-update.md`](requirements/050-atcoder-self-update.md)、`--check` のローカル比較拡張は [`requirements/059-update-local-check.md`](requirements/059-update-local-check.md)、利用手引は [`atcoder-update-usage.md`](atcoder-update-usage.md)。

- `atcoder version` で現在版 (Go 自動埋め込みの commit sha・日時・dirty) を**オフライン表示**。`atcoder update` で最新版に入れ替え、`atcoder update --check` は確認のみ (インストールしない)。
- `atcoder update --check` は installed を **リモート (`@latest`) とローカル作業ツリー (git HEAD) の両方**と比較し、`remote:` / `local:` の 2 判定を出す (要件 059)。dirty ビルドで「常に update available」と誤表示せず、「installed is newer」「手元と一致 / `--local` で入れ直すと変わる」を言い分ける。リモート解決失敗時もローカル判定までは表示して exit 1。
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

- **go ツールチェインに依存しない更新経路**。現状の `update` は `go install …@latest` に委譲するため、利用環境に `go` が必要。`go` 無しでも更新できるよう、GitHub Releases のプリビルドバイナリを取得して自身を差し替える経路を将来用意する (OS/arch 判定・ダウンロード・実行ファイルの atomic 置換・チェックサム検証が要る)。要件 050 の「将来の拡張ポイント」にも記載。リリースを発行する運用が前提になるので、当面は優先度低め。

## K. 提出ジャッジ状況の確認 (`atcoder status` / `login`) ❌ 撤去 (実現不可)

### 経緯と撤回理由 (再着手しないこと)

一度 `atcoder login` / `logout` / `status`（認証付きで `/submissions/me` を取得し verdict 表示）を実装したが、**実現不可と判明し全削除した**。理由:

- **AtCoder のログインページは Cloudflare Turnstile (ボット対策) で保護されている。** ブラウザが JS で生成する検証トークン (`cf-turnstile-response`) が無いと、正しい username/password でも認証が拒否される（→ 汎用エラー `Error.`）。`online-judge-tools` 等の既存ツールも同条件では programmatic ログイン不可。
- 回避策としてブラウザの `REVEL_SESSION` cookie を取り込む方式（`--session-cookie` 等）も実装したが、毎回 DevTools から cookie を手でコピーする運用が重く、利用者判断で**機能ごと不要**となった。
- **認証なし経路も不可:** AtCoder の提出一覧はログイン必須で列挙できず、kenkoooo AtCoder Problems API は反映まで約 5 分の遅延・コンテスト中の提出を含まない・第三者依存。即時性が要る用途に合わない。

要件・利用手引・実装（`cmd/atcoder/{login,status}.go`、`internal/atcoder/`、`config.SessionPath`、補完・fixture）は削除済み。再挑戦する場合は **Turnstile を解けるブラウザ自動化**が前提になる点に注意。

> **類似ツール横断調査 (2026-06-16)**: oj / atcoder-cli (acc) / AtCoder Tools いずれも正攻法ログインは Turnstile で全滅し、**生存策はブラウザの `REVEL_SESSION` cookie 取り込みのみ**に収束。submit POST 自体は有効 cookie があれば通る。詳細・出典は [`docs/knowledge/atcoder-auth-state.md`](../knowledge/atcoder-auth-state.md)。本撤去判断は業界現状と一致し、再導入するなら cookie 取り込み方式 (UX が重い) 一択。

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

### 追記: watch 待機中のキーアクション ✅ DONE

> 要件詳細は [`docs/tools/requirements/054-start-key-actions.md`](requirements/054-start-key-actions.md)。

- watch 待機中に `q`/`Ctrl+C` = 終了、`i` = インタラクティブ (既存 chat) → 抜けたら watch に復帰。`/dev/tty` を待機中だけ raw 化し mtime poll と多重化。raw 化できなければキー無効で従来の watch にフォールバック。
- start 専用に `runStartWatch` を新設 (`test --watch` の `runTestWatch` は不変)。`internal/watch` に非ブロッキング `Changed()`、`internal/ui` に `StartWatchFooter`、純粋関数 `keyToAction` + `watch.Changed()` をユニットテスト。キー/chat 遷移は TTY 必須で手動確認。

### 追記: 上下分割画面化 (chat + watch 同時動作) ✅ DONE

> 要件詳細は [`requirements/023-start-split-screen.md`](requirements/023-start-split-screen.md)。

- 「`i` で chat に入ると watch が止まる」モード切替を廃止し、**start を常時上下分割画面**に。上=watch 要約 (保存検知でサンプル自動再判定・PASS/FAIL コンパクト表示)、下=対話 chat (auto-restart)。両方を 1 つの bubbletea プログラムに合成して同時動作。
- 新規 `internal/ui/startsplit.go` (`RunStartSplit` + `startSplitModel`: `chatModel` を下ペインに再利用し、watch 高さを引いた `WindowSizeMsg` を転送)。サンプル判定は新規 `testexec.SummaryReporter` で stdout に出さず捕捉。`start.go` は raw-tty 多重化 (`waitForAction`/`keyToAction`) を撤去し `ui.RunStartSplit` を呼ぶだけに。
- 純粋関数 (`formatSampleSummary`/`chatHeight`/`SummaryReporter`) をユニットテスト。分割 TUI のレンダリングは TTY 必須で手動確認 (起動・TTY ゲートは pty smoke で確認)。

### 追記: 問題ナビゲーション (コマンドモードで letter/number 移動) ✅ DONE (04e1118)

> 要件詳細は [`requirements/027-start-problem-navigation.md`](requirements/027-start-problem-navigation.md)、利用手引は [`atcoder-start-usage.md`](atcoder-start-usage.md) のコマンドモード節。

- 分割画面に居たまま隣の問題へ移動する。下ペイン chat の vim 風コマンドモード ([024](requirements/024-interactive-case-builder.md) / [ADR 0007](decisions/0007-interactive-command-mode-trigger.md)) に **`:task next|prev` (letter ±1)**・**`:contest next|prev` (contest_num ±1、letter 保持)**・**`:e <spec>` (任意ジャンプ)** を追加。移動先は start と同じく**着手** (無ければ空ファイル作成) して watch/chat を再ターゲット。
- ID 増減は `internal/layout` の純粋関数 `ShiftLetter`/`ShiftContest` (`ContestNum` を一般化、`arc`/`agc` も番号移動可)。再ターゲットは親 `startSplitModel` が握り、chat はパースして `NavMsg` を通知するだけ (層境界: `internal/ui` は `cmd/atcoder` を import しない)。`buildTarget` を初回起動とナビ解決で共通化。
- 新サブコマンド・新フラグ無し。ナビは **start 限定** (`test --interactive` 単体では `:task`/`:contest` 等は `E492` 未知コマンド)。境界 (`a`/下限)・非数値 contest・複数文字 letter は TUI 内 1 行エラーで継続 (exit code 不変)。純粋関数をユニットテスト、再ターゲット TUI は手動確認。

## R. 対話モードの auto-restart をフラグ化 (`test --interactive --auto-restart`) ✅ DONE

### 決まったこと

> 要件詳細は [`requirements/020-interactive-auto-restart-flag.md`](requirements/020-interactive-auto-restart-flag.md)。

- chat TUI の auto-restart 選択を、子終了後の対話プロンプト (`press [r] to run again`) から **起動フラグ `--auto-restart` (`-R`)** に移し、終了後プロンプトと `r` キー処理を**廃止**した。
- フラグ無し既定 = 子終了で quit。`--auto-restart` = 起動時から sticky に再実行 (`Ctrl+D` graceful / `Ctrl+C` 中断)。`--interactive` 必須 (無ければ exit 2)、非 TTY では無効 (1 回実行)。
- 結線: `test.go --auto-restart` → `runAdHoc` → `runexec.Options.AutoRestart` → `ChatHeader.AutoRestart` → `ui.RunChat`。`chatModel` から `awaitingRestart` を削除。chat Model 初期化と streamEnd 分岐をユニットテスト、非 TTY no-op / 単体指定 exit 2 を fixture smoke で固定。
- 追記 (要件 [021](requirements/021-interactive-ctrl-d-quit.md)): `Ctrl+D` は子の stdin を閉じて EOF を送るのをやめ、**CLI 側の終了キー**に変更。EOF まで読む batch は `test --in` で。`stdinClosed` 経路は撤去。
- 追記 (要件 [022](requirements/022-interactive-unify-quit-keys.md)): `Ctrl+C` と `Ctrl+D` を**どちらも「終了 (子を kill して quit)」に統一**。唯一の差だった auto-restart 時の graceful 停止 (現セッション後 quit) を廃止し、`ctrlDActionFor`/`quitOnChildExit` を撤去。`Ctrl+C` キー自体は残す (bubbletea raw では自前処理しないと無反応=force-quit 不能のため)。
- 追記 (要件 [025](requirements/025-interactive-ctrl-c-interrupt.md)): `Ctrl+C` を**「プログラム中断・再起動」に再分離**。`Ctrl+C` = 走っている子を kill して新プロセスでやり直す (新セッション。chat に留まる。auto-restart の ON/OFF を問わず同じ)、`Ctrl+D` = chat 終了 (022 のまま)。実装は既存 `restart()` を流用。spawn 無し経路の `Ctrl+C` は従来どおり quit にフォールバック。
- 追記 (要件 [051](requirements/051-interactive-ctrl-d-reset-then-quit.md)) ✅ DONE (5984e17): `Ctrl+D` を**「1 回目=プログラムをリセット (`restart()` 相当・chat 残留) / 2 回連続=chat 終了」**に変更。021/022 の「単押し即終了」を置き換え、終了を 2 連続押下に格上げ (誤爆耐性)。「連続」は間に他のキー入力が挟まらないこと (出力到着等の非キーは武装を解かない)。`Ctrl+C` (中断再起動) は据え置き。状態は `ctrlDArmed` 1 つ、`KeyMsg` 先頭クリア + `Ctrl+D` 再武装の対称実装。insert モードのみ (command/builder は不変)。

## V. インタラクティブからの入出力ケース作成 + ライブ検証 ✅ DONE

> **✅ DONE → [requirements/024-interactive-case-builder.md](requirements/024-interactive-case-builder.md)** / [ADR 0007](decisions/0007-interactive-command-mode-trigger.md)。ABC ロードマップ [F](abc-todo.md) を畳む。

- chat 内の **vim 風 command モード** (`Esc` → `:case`) でケースビルダーを開く。トリガーは `Ctrl+:` が bubbletea v1.3.10 で受信不能なため `Esc` に決定 (ADR 0007)。
- `.in` はセッションの送信入力を前埋め・編集可、`.out` は手入力。`:w` で `tests-extra/NN.in|NN.out` (cache 配下・`--refresh` 不可侵) に保存。
- 期待出力を定義すると、ファイル保存と独立に **chat 内で stdout をライブ検証** (行ごと ✓/✗)。
- `atcoder test` / `start` が公式 `tests/` の後ろに `tests-extra/` を連結して判定 (表示 id `x01`)。新サブコマンド・新フラグは増やさない。

### 追記: コマンドモードの Tab 補完 ✅ DONE (762b7e2)

> 要件詳細は [`requirements/031-command-mode-completion.md`](requirements/031-command-mode-completion.md)、利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) / [`atcoder-start-usage.md`](atcoder-start-usage.md) のコマンドモード節。

- chat の `:` 行で **`Tab` 補完**。コマンド名 (`case`/`w`/`set`/`q`/`debug`/`cheat` 常時 + `task`/`contest`/`e` は NavEnabled 時) と既知サブトークン (`:set verify|noverify|debug|nodebug`、`:task`/`:contest` の `next|prev`) を、最長共通プレフィックスまで補完し、複数候補なら `:` 行直下に候補一覧を表示 (bash 風)。
- 補完ロジックは `internal/ui` の純粋関数 `completeCommandLine(line, navEnabled)` に閉じる (子プロセス・stdout・解答ファイルに触れない)。候補は canonical 名のみで `parseCommand` ([024]) / `navRequestFor` ([027]) と整合。`:e <spec>` の問題候補生成は将来拡張。
- 新コマンド・新フラグ無し。`Tab` を押さなければ挙動不変。純粋関数をユニットテスト、`Tab` 駆動・候補行描画は TTY 必須で手動確認。

## T. 対話モードの出力待ちスピナー + 経過時間 ✅ DONE

> 要件詳細は [`requirements/053-interactive-waiting-spinner.md`](requirements/053-interactive-waiting-spinner.md)。

- chat TUI で **入力送信後〜次の出力が来るまで**、入力ボックスの下罫線に**スピナー (braille) + 経過時間** (`⠹ 430ms ───`) をライブ表示。出力到着・子終了・リロードで解除。「打ったのに無反応 / 重いのか固まったのか」を可視化する。
- 下罫線への重ね描きで**画面の行数は不変** (分割画面 `start` の高さ計算を崩さない)。tick は待機中だけ回す (busy-loop にしない)。世代タグ (`spinGen`) で連続送信でも tick ループは 1 本。
- `internal/ui/chat.go` に待機状態 + `spinnerTickMsg`/`spinnerTickCmd` + 純粋関数 `waitStatus` を追加。状態遷移と `waitStatus` をユニットテスト、アニメ自体は TTY 必須で手動確認。

## U. chat 内からの提出準備 (`Ctrl+S`) ✅ DONE (c5d3227)

> 要件詳細は [`requirements/026-chat-submit.md`](requirements/026-chat-submit.md)。ABC ロードマップ [C. 提出](abc-todo.md) の chat 経路を畳む。

- インタラクティブ chat (`test --interactive` と `start` 分割画面の下ペイン) 中に **`Ctrl+S`** で提出準備 (`test --submit` 相当 = 解答コピー + 提出ページ起動、**実 POST はしない**)。chat を抜けず・子を kill せず実行し、結果を 1 行表示。
- トリガーは**独立した予約キー `Ctrl+S`** (024 のコマンドモードは未実装で大きいので entangle を避ける)。024 実装後に `:submit`/`:s` を同じ submit コールバックのエイリアスにできる。
- **サンプルゲート無し** (chat はバッチ判定が走っていない)。`test --submit` (ゲートあり) との意図的な差。
- 層: `internal/ui` は `cmd/atcoder` を import 不可 → `ChatHeader.Submit` コールバックを注入。`test --interactive` は `adhoc.go` の `makeChatRunner`、`start` は分割画面なので `start.go` の `ui.RunStartSplit` 用 `ChatHeader` に `chatSubmitFunc(contest, task, lay)` を各々注入。`prepareSubmission` を非印字 core (`submitPrepCore`) に分離。
## AO. 位置引数とフラグの順序非依存 (`internal/cliargs`) ✅ DONE (87ba3ab)

> 要件詳細は [`requirements/029-flexible-arg-order.md`](requirements/029-flexible-arg-order.md)。

- `atcoder test --task d abc457` のように**位置引数とフラグを任意順**で打てるようにする。Go `flag` は最初の非フラグで停止 + repo は `args[0]` 先頭剥がし、のため現状は位置引数が先頭限定。
- `flag.Parse` の**前に `internal/cliargs.Split` を 1 枚**噛ませ、引数を「フラグ + 値」と「位置引数」に分離してから既存 `flag` に渡す。`flag` 本体・exit code 規約・`-x`/`--x` 両対応は不変。
- value-flag 集合 (どのフラグが次トークンを値に取るか) を `internal/cliargs` に**一本化**し、`internal/complete` (補完の位置引数判定) と共有 = DRY。
- 対象は位置引数+フラグを両方持つ **test / start / review / new abc**。フラグのみ (stats/update) / 位置引数のみ (config/completion) は順序問題が無いので対象外。

## W. start watch ペインの per-case verdict ✅ DONE

> 要件詳細は [`requirements/028-start-watch-per-case.md`](requirements/028-start-watch-per-case.md)。分割画面 [023](requirements/023-start-split-screen.md) の上ペイン表示を richer にする。

- `start` 分割画面の watch ペインを「PASS/FAIL 件数 + 失敗ケース番号」から **per-case verdict** (`01 AC  02 WA  03 TLE  04 AC`、AC=緑 / WA/TLE/RE=赤) に拡張。どのケースで落ちているか即分かる。
- `SummaryReporter` が `End(results)` でケース名順の全 `CaseResult` を捕捉し、`Result()` を `(passed, total, cases []CaseResult)` に拡張。`start.go` が `CaseVerdict` に写像、`formatSampleSummary` が per-case 表示。幅超過は `ansi.Truncate` で `…` 切り詰めて上ペイン 3 行を維持。
- 表示のみ。判定ロジック・exit code・chat ペイン・非 TTY は不変。

## X. chat command モードの `:debug` / `:cheat` ✅ DONE

> 要件詳細は [`requirements/030-chat-debug-cheat-commands.md`](requirements/030-chat-debug-cheat-commands.md)。command モード [024](requirements/024-interactive-case-builder.md) にコマンドを 2 つ追加。

- `:debug` (`:set debug` / `:set nodebug`) で chat 実行中に Debug 表示 (`-d` 相当) をトグル。以降届く `[DEBUG]` stdout 行の振り分けに反映 (既描画行は遡及しない)。
- `:cheat` (`:help` / `:?`) で今使える command 一覧を info 行で表示。`NavEnabled` (start 分割画面) のときだけ `:task`/`:contest`/`:e` も載せる。
- 既存コマンド・キー・判定・exit code は不変。stdout 非汚染 (chat 内 info 行のみ)。

## Y. chat ナビ `:contest` / `:task` の直指定 ✅ DONE

> 要件詳細は [`requirements/032-nav-direct-target.md`](requirements/032-nav-direct-target.md)。ナビ [027](requirements/027-start-problem-navigation.md) を相対移動に加え絶対ジャンプへ拡張。

- `:task <letter>` で現コンテストの記号へ直指定 (`:task f` → `abc457_f`)。`:contest <num>` で現シリーズ・桁数を保って番号直指定 (`:contest 123` → `abc123_d`、`:contest 5` → `abc005`)、`:contest <id>` でシリーズごと (`:contest arc100`)。いずれも `:contest` は現 letter を保持。
- `next`/`prev` 以外の非空トークンを直指定として `NavLetterExplicit` / `NavContestExplicit` に写す (navRequestFor は形のみ、妥当性は nextTarget)。`layout.WithContestNum` を追加。不正値は `E492` で継続。`:e` の自由形式とは役割分担。
- `next`/`prev`・`:e`・他コマンド・判定・exit code は不変。
## Z. chat command モードの履歴ページ移動 (`PageUp`/`PageDown`) ✅ DONE (26d9a56)

> 要件詳細は [`requirements/033-command-mode-scrollback-paging.md`](requirements/033-command-mode-scrollback-paging.md)。command モード [024](requirements/024-interactive-case-builder.md) のあいだ scrollback を遡れるようにする。

- command モード (`Esc` → `:`) 中に **`PageUp`/`PageDown`** で chat 履歴 (scrollback = `viewport`) を 1 ページ上下スクロール。`:` 行 textinput と衝突しないキーを選定。
- `refreshViewport` の常時 `GotoBottom()` を「**スクロール中 (`cmdScrolled`) は `YOffset` 維持、それ以外は最下部追従**」に変更。出力が来ても上スクロール位置が保たれる。insert モードはスクロールキーが無く常に最下部 = 非破壊。
- command モードを抜ける (`Esc` / コマンド実行) と `cmdScrolled` 解除 + 最下部 (最新) に戻す。子・stdin・解答には触れない (表示のみ)。

## AA. chat `:debug` トグルを watch ペインへ反映 ✅ DONE (80e0534)

> 要件詳細は [`requirements/034-start-debug-watch-sync.md`](requirements/034-start-debug-watch-sync.md)。[030](requirements/030-chat-debug-cheat-commands.md) で入れた `:debug` を分割画面の watch ペインにも波及させる。

- `:debug` (`:set debug` / `:set nodebug`) で Debug をトグルすると、chat 表示だけでなく **watch ペインの再判定にも live Debug が反映**される (`testexec.Run` の `Debug` に渡す)。Debug は `[DEBUG]` 行を比較対象から外すので verdict が変わる ⇒ `-d` 付け忘れで起動しても対話中に on にすれば watch の WA が正しく解消する。
- chat → 親への通知に `DebugMsg{On bool}` を新設 ([027](requirements/027-start-problem-navigation.md) の `NavMsg` と同じ流儀)。`startSplitModel` が live `debug` を保持し、トグル時に epoch を進めて即再判定 (in-flight の旧判定は破棄)、ナビ再ターゲットでも live Debug を引き継ぐ。watch ペインのタイトルに `[debug]` バッジ。
- chat 子プロセスの env・バッチ `test`/`run`・exit code・`test --interactive` 単体は不変。`RunSamples` を `func(debug bool) SampleSummary` 化。

## AB. chat 入力の複数行ペースト ✅ DONE

> 要件詳細は [`requirements/035-chat-multiline-paste.md`](requirements/035-chat-multiline-paste.md)。chat の input ([024](requirements/024-interactive-case-builder.md)) に複数行ペーストを対応。(レター A–Z 出尽くしのため AA から継続)

- chat の insert モードで**複数行をペースト**すると、各改行を `Enter` 扱いで完全行を子 stdin へ**逐次送信**し、末尾の未改行行は入力欄に残す。`\r\n`/`\r` は `\n` に正規化。新キー・textarea 化はせず、ペーストのみ対応 (ユーザ意向: コピペ対応 + あとは逐次送信)。
- bracketed paste (`KeyMsg.Paste`) を insert モードで横取り。bracketed 無効端末では `Enter` 列として届くため既存経路で取りこぼさない。送信ロジックを `submitLines` に抽出し単一行 `Enter` と共有、分割は純粋関数 `splitPasteLines`。
- `Enter`・履歴・`Tab` 補完・command モード・`Ctrl+C/D/S`・判定・exit code は不変。command モード/ケースビルダーのペーストは不変。

## AC. start watch ペインの詳細表示 (失敗ケースの diff, `Ctrl+G`) ✅ DONE (d35185e)

> 要件詳細は [`requirements/036-start-watch-detail-view.md`](requirements/036-start-watch-detail-view.md)。分割画面 [023](requirements/023-start-split-screen.md) の per-case verdict (W) の「中身」を見られるようにする。

- `start` 分割画面で **`Ctrl+G`** を押すと、失敗ケース (WA/TLE/RE) の **diff (期待 vs 実際、RE は stderr)** を表示。もう一度 `Ctrl+G` か `Esc` で閉じる。`PageUp`/`PageDown`/`↑`/`↓` でスクロール。AC は省略。
- **表示方式は watch ペイン拡張** (上ペインが下方向に伸び、chat は縮んで下に残る)。当初の全画面オーバーレイから変更し、編集中の chat と詳細を同時に見られるようにした。
- データは既存: `CaseResult` が `Input`/`Expected`/`Actual`/`Stderr` を保持し `SummaryReporter` が運ぶ。失敗ケースの I/O を `CaseVerdict` に載せ、既存 `renderDiff` で描画するだけ。
- `Ctrl+G` は chat 未使用キーで split が chat より先に横取り。chat ペイン・判定・exit code・非 TTY・上ペインの per-case verdict は不変 (表示のみ)。

## AD. コマンド利用テレメトリ (ローカル集計, `atcoder usage`) ✅ DONE

> 要件詳細は [`requirements/037-usage-telemetry.md`](requirements/037-usage-telemetry.md)。利用手引は [`atcoder-usage-usage.md`](atcoder-usage-usage.md)。既存 [`stats`](requirements/005-exercise-stats.md) (練習解答集計) とは責務が別で、新サブコマンドに分けた。

- `main()` の dispatch を 1 箇所でラップし、全組み込みコマンド実行のたびに利用イベント (cmd / フラグ名 / 所要時間 / exit / ts / version) を **JSONL で追記**。`atcoder usage` がそれを読みコマンド別の count / total / avg / last を表で出す (`--flags` でフラグ別内訳、`--json` で機械可読)。
- 記録は **non-fatal** (失敗してもコマンド本体・exit code 不変)。フラグ**名**のみ記録し値・位置引数は残さない (プライバシー)。`__complete`・未知コマンドは対象外。
- 保存先は**データ領域** `$XDG_DATA_HOME/atcoder-tools/usage/events.jsonl` (キャッシュと別。`--refresh` で消えない)。`ATCODER_NO_USAGE` で完全無効化。
- 新規 `internal/usagelog` (記録 + 集計) と `cmd/atcoder/usage.go`。`run.sh` は `XDG_DATA_HOME` を一時 dir に固定して実ユーザのデータを汚さず、`usage` の exit 0・記録の有無・`ATCODER_NO_USAGE` を smoke。

## AE. start / chat から解答をエディタで開く (`Ctrl+E`・nvim remote) ✅ DONE

> 要件詳細は [`requirements/038-start-edit-in-editor.md`](requirements/038-start-edit-in-editor.md)。chat の外部アクション ([Ctrl+S 提出](requirements/026-chat-submit.md)) と同じ注入パターン。

- `start` 分割画面 / `test --interactive` の chat で **`Ctrl+E`** で解答ファイルをエディタに開く。nvim の `:terminal` 内 (`$NVIM` 在り) は**親 nvim へ `--remote-tab` で送り**、新しい nvim を入れ子に起動しない (ネスト回避が主目的)。nvim 外は `editor` (config) / `$EDITOR` / `nvim` を `tea.ExecProcess` で前面起動。`nvr` 等の外部依存なし (nvim 組み込み `--server`)。
- 起動方法の決定を純粋関数 `planEdit` に隔離し ($NVIM 有無・config 上書き・$EDITOR・既定) ユニットテスト。`ChatHeader.Edit` (`EditFunc`) を注入 (`Submit` と同じ層境界)。config に `editor` キーを追加。
- 素の `e` は入力欄が文字として食う・`:e` はナビ使用済みのため **`Ctrl+E`** を採用。解答は開くだけ・判定/提出/exit code は不変。

> **追補 ([041](requirements/041-edit-nvim-remote-reuse.md)) ✅ DONE**: nvim 内 remote の既定を `--remote-tab` → `--remote` (現在のウィンドウで開く = タブ再利用) に変更。問題を切り替えるたびにタブが増えるのを解消。config `editor_nvim_remote` (enum `current`(既定)/`tab`) で切替可能。`planEdit` に `nvimRemote` 引数を追加してユニットテスト。

## AF. chat の前回セッション入力リプレイ (`:replay`) ✅ DONE

> 要件詳細は [`requirements/039-chat-replay-previous-session.md`](requirements/039-chat-replay-previous-session.md)。command モード [024](requirements/024-interactive-case-builder.md) にコマンドを 1 つ追加。永続化は利用テレメトリ [037](requirements/037-usage-telemetry.md) (`internal/usagelog`) と同じ JSONL 追記方式を踏襲。

- `start` 分割画面 / `test --interactive` の chat の command モードに **`:replay`** を追加。同じ問題 (contest+task) の**前回セッション**で子へ送った入力行を、子を**リスタートしてクリーンな状態から順送**して再現する。前回入力が無ければ info 行のみで子は起動しない。
- chat の入力行を**セッションをまたいで永続化**する新パッケージ `internal/chatlog` を追加 (`$XDG_DATA_HOME/atcoder-tools/chat-history/<contest>/<task>.jsonl`・`ATCODER_NO_CHAT_HISTORY` で無効化・best-effort 非 fatal)。1 行 = 1 入力イベント (`ts`/`session`/`text`)、`LoadLastSession` が直近 session 分を順序保持で返す。
- 永続化は `internal/ui` に持ち込まず、ChatHeader に `PrevInputs []string` / `RecordInput func(string)` を**注入** (`Submit`/`Edit` と同じ層境界)。composition root (`makeChatRunner` / `buildTarget`) で session ID 生成・先読み・記録フックを結線。start のナビ再ターゲットは問題ごとに `buildTarget` を通るので前回入力も問題単位で切り替わる。

## AG. insert モードの scrollback ページスクロール (`PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F`) ✅ DONE

> 要件詳細は [`requirements/040-insert-mode-scrollback-paging.md`](requirements/040-insert-mode-scrollback-paging.md)。command モードのスクロール [033](requirements/033-command-mode-scrollback-paging.md) を insert モードへ広げる。

- chat の **insert モード (通常入力時)** で `PageUp`/`Ctrl+B` で 1 ページ上、`PageDown`/`Ctrl+F` で 1 ページ下に scrollback をスクロール。これまで command モード限定だったスクロールを insert でも使えるようにし、過去の出力を見るのに毎回 `Esc` する手間を無くした。
- 追従挙動は 033 と同一: 上スクロール中は出力到着で最下部に引き戻さない。`PageDown`/`Ctrl+F` で最下部に戻る or `Enter` 送信・`Ctrl+C`/`Ctrl+D` で追従再開。
- 内部: `cmdScrolled` → `scrolled` に一般化し、`scrollUp`/`scrollDown` ヘルパを command/insert で共有。`Ctrl+B`/`Ctrl+F` は textinput のカーソル移動を横取りするが `←`/`→` で代替可。command モードの `:` 行編集では従来どおりカーソル移動 (スクロールは `PageUp`/`PageDown` のみ)。
- 既存の command モードスクロール・入力履歴 (`↑`/`↓`)・送信・判定・exit code・start 分割画面は不変。ユニットテスト (`chatscroll_test.go`) で insert のスクロール開閉・追従抑止・Enter 復帰・履歴非破壊を固定。

## AH. 判定結果の構造化出力 (`test --json`) — TUI vs nvim 段階 1 ✅ DONE

> 要件詳細は [`requirements/042-test-json-output.md`](requirements/042-test-json-output.md)。利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) の「JSON 出力」節、内部設計は [`atcoder-test-architecture.md`](atcoder-test-architecture.md) の「Reporter 差し替えによる機械出力」節。

### 背景: TUI として育てるか nvim 拡張に作り直すか

- 「nvim で atcoder をやる」上での方針を議論し、**全面書き直しも全面 TUI 重装化もしない**で合意。判定/fetch/stats などコアロジックは Go CLI のエンジンとして残し UI から切り離す (**段階 1**)、その上で nvim 側に薄い Lua フロント (`vim.system()` でコア CLI を叩き quickfix/diff 表示) を**増設**する (段階 2)。bubbletea 版 TUI は並走で残す。
- 競プロ界隈は「専用 TUI」の潮流が無く (Go 製総合 CLI cpt は 44★ でアーカイブ済み)、主流は CLI エンジン + エディタ薄グルー (competitest.nvim / cphelper.nvim は 96-100% Lua で実ロジックを外部 CLI に委譲、fugitive 21.7k★)。堅牢な CLI を持つことが正解で、Go コアは委譲先になる資産。
- 本項目は段階 1 の最初の一手。`test` の判定結果を機械可読 JSON で吐く出力経路を 1 本足した。

### 決まったこと (この項目で実装したこと)

- `atcoder test <contest> --task <task> --json` で、サンプル判定結果 (per-case の `status`/`elapsed_ms`/`input`/`expected`/`actual`/`stderr`/`debug`・`passed`/`total`/`all_passed`・`contest`/`task`/`time_limit_ms`/`timeout_ms`/`tolerance`) を **JSON オブジェクト 1 個**として stdout に出力。人間向け表示は出さない。`usage --json` (要件 037) と同じ「人間向け表 / 機械向け JSON を `--json` で出し分ける」流儀。
- 判定ロジック (`internal/testexec`) は無改修。既存 `SummaryReporter` を Reporter に差し替えて `testexec.Run` を回し、`cmd/atcoder/testjson.go` で encode するだけ。`SummaryReporter` に `Header` メタ捕捉 (`Meta()`) を追加 (`start.go` は無視するので非破壊)。`CaseStatus`→文字列は cmd 側の純粋関数。
- `--json` はサンプルモード専用。`--in`/`--out`/`--interactive`・`--watch`・`--submit` との併用は `exit 2`。exit code は通常 `test` と同じ (全通過=0 / 不通過=1。不通過でも JSON は出る)。

### 影響範囲 (実装済み)

- `cmd/atcoder/test.go` (`--json` フラグ・併用バリデーション・分岐)、新規 `cmd/atcoder/testjson.go` (スキーマ・`buildTestJSON`/`caseStatusString`/`runTestJSON`) + `testjson_test.go`。`internal/testexec/summaryreporter.go` (Header メタ捕捉 + `Meta()`)。`internal/complete/complete.go` (`--json` 候補)、`cmd/atcoder/main.go` usage。`fixtures/run.sh` (exit code + JSON 本文 + 併用拒否の smoke)、`docs/tools/atcoder-test-{usage,architecture}.md`。

### 段階 1 の残り (将来)

- `stats --json` / `review --json`: それぞれの nvim 機能を作る段で同じ流儀で機械出力を足す。
- `--watch --json` (NDJSON): 再判定のたびに 1 行 JSON を流し nvim 側がライブ更新。
- 段階 2: nvim Lua フロントの増設 (薄グルー)。competitest.nvim のテストケースの扱い方 (Competitive Companion 受信 port 27121・diff トグル・popup/split UI・テンプレ) を参考にする。

## AI. 提出準備時に DEBUG 出力行をコメントアウト (`test --submit` / chat `Ctrl+S`) ✅ DONE

> 要件詳細は [`requirements/043-submit-comment-out-debug.md`](requirements/043-submit-comment-out-debug.md)。利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) の「提出準備」節、内部設計は [`atcoder-test-architecture.md`](atcoder-test-architecture.md) のパッケージ構成 (`internal/debugstrip`)。

### 決まったこと (この項目で実装したこと)

- `test --submit` と chat `Ctrl+S` (= `submitPrepCore` 経由) でクリップボードへコピーする解答ソースから、`[DEBUG]` を出力する `print(...)` 行を**コメントアウトしてからコピー**する。デバッグ出力の消し忘れ提出による WA / TLE を構造的に防ぐ。**解答ファイル本体は書き換えず、メモリ上のコピーだけ加工**する (既存の「解答を壊さない」安全設計を維持)。
- 検出は既存の `-d`/`--debug` の `[DEBUG]` 規約に揃える (行頭がインデント可の `print(` で最初の文字列引数が `[DEBUG]` 始まり)。変換はインデント保持で `# ` を差し込む。コメントアウト済み行は再マッチしないので冪等。
- **空ブロック化の回避**: `if os.environ.get("DEBUG"):` ガード直下の単独 print のように、コメントアウトするとブロックが空になる箇所はスキップ (`IndentationError` 回避。ガード下は判定で `DEBUG` 未設定により実行されないので無害)。ループ等で実コードと混在する `[DEBUG]` print はコメントアウトする。
- デフォルト ON。`test --submit --keep-debug` で無加工コピーにオプトアウト (chat は常に ON)。1 行以上コメントアウトすると件数を表示する。
- 文字列変換ロジックは純粋パッケージ `internal/debugstrip` (`CommentOut(src) (out, n)`) に切り出し、ユニットテストで固定。

### 影響範囲 (実装済み)

- 新規 `internal/debugstrip/debugstrip.go` (+ `_test.go`)。`cmd/atcoder/submitprep.go` (`submitPrepCore` に `keepDebug`・`submitOutcome.DebugCommented`)、`cmd/atcoder/test.go` (`--keep-debug` フラグ + ad-hoc 排他)、`cmd/atcoder/adhoc.go` (chat 経路で件数併記)、`cmd/atcoder/main.go` usage、`internal/complete/complete.go` (`--keep-debug` 候補)。`fixtures/run.sh` (`--keep-debug` + ad-hoc の reject smoke)。`docs/tools/atcoder-test-{usage,architecture}.md`。

## AJ. 提出前チェックと確認プロンプト (`test --submit` / chat `Ctrl+S`) ✅ DONE

> 要件詳細は [`requirements/044-submit-precheck-confirm.md`](requirements/044-submit-precheck-confirm.md)。利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) の「提出準備」節、内部設計は [`atcoder-test-architecture.md`](atcoder-test-architecture.md) (`submitprep.go` の `runSubmitPrep` / `internal/testexec` の `CaseResult.DebugSeen`)。[AI](#ai-提出準備時に-debug-出力行をコメントアウト-test---submit--chat-ctrls--done) (DEBUG コメントアウト) の安全網。

### 決まったこと (この項目で実装したこと)

- `--submit` / chat `Ctrl+S` で提出準備に進む前にサンプルを実行し、**提出前チェック**を通す。リスク条件は (a) サンプルを実行できなかった、(b) 全通過していない (WA/TLE/RE)、(c) 実行中に `[DEBUG]` 出力が検出された、の 3 つ。
- **クリーン** (3 つともなし) なら従来どおり確認なしで提出準備。**リスクあり**なら理由を表示し `[y/N]` で確認 — `y` で提出準備、他で中止 (exit 1)。CLI は stdin が非 TTY なら自動で「いいえ」(ハングしない・安全側)。chat は `submitConfirm` モードで次の 1 打鍵を回答として消費する。
- `[DEBUG]` 検出は実行時の **生 stdout / stderr** を見る (`-d` の有無に依らない)。AI のコメントアウトが regex で拾えない漏れ (例: `print(..., file=sys.stderr)`) に対する安全網になる。
- 判定ロジックは純粋関数 `submitGateReasons` に切り出し、CLI (`runSubmitPrep`) と chat (`chatSubmitCheckFunc`) で共有。将来の `--yes` スキップ / 本番モード判定から再利用できる形にした。

### 影響範囲 (実装済み)

- `internal/testexec/judge.go` (`CaseResult.DebugSeen` + `containsDebugLine`、`_test.go`)。`cmd/atcoder/submitprep.go` (`submitGateReporter` / `submitGateReasons` / `confirmSubmit` / `runSubmitPrep`)、`cmd/atcoder/test.go` (`--submit` を `runSubmitPrep` 経由に)、`cmd/atcoder/adhoc.go` (`chatSubmitCheckFunc`)、`internal/ui/chat.go` (`SubmitCheck`/`SubmitCheckFunc`/`ChatHeader.SubmitCheck`/`submitConfirm`)。`fixtures/fixture_okdebug*` + `fixtures/run.sh`。`fixtures/README.md` / `docs/tools/atcoder-test-{usage,architecture,testing}.md`。

## AK. chat command モードの特定サンプルケース実行 (`:test [case]`) ✅ DONE (dbdeed9)

> 要件詳細は [`requirements/045-chat-run-sample-case.md`](requirements/045-chat-run-sample-case.md)。利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) の command モードのコマンド表、内部設計は [`atcoder-test-architecture.md`](atcoder-test-architecture.md) (`chat_casebuilder.go` の `execTest` / `chat_sample.go`)。[V](#v-インタラクティブからの入出力ケース作成--ライブ検証--done) (ケースビルダー・ライブ検証) と [AF](#af-chat-の前回セッション入力リプレイ-replay--done) (`:replay` の子リスタート + 順送) の合わせ技。

### 決まったこと (この項目で実装したこと)

- chat の command モードに **`:test [case]`** (別名 `:t`) を追加。キャッシュ済みサンプル (公式 `tests/` = `01`、追加 `tests-extra/` = `x01`) の 1 つを指定すると、子をリスタートしてクリーンな状態からその `.in` を順送し、`.out` でライブ検証 (各行 `✓`/`✗`) する。
- 引数省略 (`:test`) は利用可能なケース ID 一覧を表示するだけ (実行しない)。`:test 1`→`01`・`:test x1`→`x01` の正規化はバッチ `test` の `filterRefs`/`normalizeCaseName` と同規約。
- 順送は `:replay` と同じ `submitLines(..., record=false)` を使い、`sessionInputs`/chatlog ([AF](#af-chat-の前回セッション入力リプレイ-replay--done)) を汚さない (`:test` 後の `:replay` は手入力だけを再生)。
- `:test` 自身は **fetch しない** — 既にキャッシュ済みのサンプルだけを読む (取得は `atcoder test <contest>`、追加は `:w`)。`internal/ui` は testexec を import せず層境界を保つ。

### 影響範囲 (実装済み)

- `internal/ui/chat_casebuilder.go` (`parseCommand` に `test`/`t`、`execCommand` の `case "test"`、`execTest`、`newCommandInput`/`showCheat`)、`internal/ui/chat_sample.go` (**新規**: `listSampleCases`/`resolveSampleCase`/`normalizeSampleRef`)、`internal/ui/command_complete.go` (`completeNamesBase` + `completeExpectsArg`)。テスト: `internal/ui/chat_sample_test.go`・`chattest_test.go`・`command_complete_test.go`。`docs/tools/atcoder-{test,start}-usage.md` / `atcoder-test-architecture.md`。

## AP. DEBUG 行の最小 JSON pretty print (`test/run --pp` / chat `:pp`) 📝 設計済み (未実装)

> 要件詳細は [`requirements/047-debug-json-pretty-print.md`](requirements/047-debug-json-pretty-print.md)。[X](#x-chat-command-モードの-debug--cheat--done) (`:debug`) / [AA](#aa-chat-debug-トグルを-watch-ペインへ反映--done-80e0534) (watch 波及) / [AH](#ah-判定結果の構造化出力-test---json--tui-vs-nvim-段階-1--done) (`--json`) で整備した debug パイプラインの**表示層に整形を一段足すだけ**の最小機能。実装は `design` 済みにつき `feature` で着手する。

### 決めたこと (設計)

- `[DEBUG]` 行のうち **ペイロードが単独で valid JSON (`{`/`[` 始まり) のものだけ** を `json.Indent` で 2-space 再インデント。Python `repr`・ラベル付き `key = {...}`・グリッド検出には踏み込まない (言語非依存・`encoding/json` のみ)。
- オプトイン: バッチ `--pp` フラグ / chat `:pp` (`:set pp|nopp`) トグル、既定 off。**verdict・`--json` の `debug` フィールド・exit code・保存値は不変** (整形は表示時のみの純関数 `prettifyDebug`)。
- `--pp` は `-d` と**直交**。`-d` 無しで `--pp` を渡したら stderr に note 1 行 (含意はしない / フットガンだけ消す)。キー順・数値は `json.Indent` で保存 (`Unmarshal`+`Marshal` は使わない)。

### 影響範囲 (設計、未実装)

- 新規 `internal/ui/prettydebug.go` (`prettifyDebug`)、`internal/ui/reporter.go` (`pp bool`)、`cmd/atcoder` の test/run フラグ、`internal/ui/chat_casebuilder.go`/`chat.go` (`:pp`・`header.PP`)、`internal/ui/command_complete.go` (`pp`/`nopp` 補完)、`fixtures/` (JSON debug スモーク)、`docs/tools/atcoder-test-usage.md`。

## AM. chat の `:replay` が直近の `:test` ケースを再生 ✅ DONE (34ee25b)

> 要件詳細は [`requirements/048-chat-replay-test-case.md`](requirements/048-chat-replay-test-case.md)。利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md) / [`atcoder-start-usage.md`](atcoder-start-usage.md) の command モードの `:replay` / `:test` 説明。[AK](#ak-chat-command-モードの特定サンプルケース実行-test-case--done-dbdeed9) (`:test`) と [AF](#af-chat-の前回セッション入力リプレイ-replay--done) (`:replay` の手入力再生) を繋ぐ。

### 決まったこと (この項目で実装したこと)

- `:replay` を「**直近の操作 (手入力 / `:test` ケース) を再生**」に一般化。`:test [case]` でサンプルを流したあと `:replay` を打つと、コマンドの再実行ではなく**そのケースの `.in` を再入力**し直し (子リスタート + 順送)、`.out` でライブ検証も**再度有効化**する。
- 優先順位は **現セッションの手入力 (`sessionInputs`) → 直近の `:test` ケース → 直前セッションの手入力 (`prevSessionInputs`) → 前回 chat 起動 (`PrevInputs`)**。`:test` のあとに手入力すれば手入力が直近として優先、しなければ `:test` ケースが再生される (`sessionInputs` の空・非空で「`:test` より後に手入力したか」を判定 = 明示タイムライン不要)。
- 直近 `:test` ケースは `chatModel.lastTest *testReplay` (`id`/`input`/`expected`) に**今回の起動内でのみ**スナップショット保持。再生も `record=false` を維持し `sessionInputs` / chatlog ([AF](#af-chat-の前回セッション入力リプレイ-replay--done)) を汚さない (反復再生・永続化を膨らませない)。`:test` を一度も使わなければ `:replay` の挙動は [039](requirements/039-chat-replay-previous-session.md) と完全一致。
- `:test`/`:replay` 共通の順送 (検証有効化 → 子リスタート → `submitLines(record=false)`) を `flowInput` に抽出。新サブコマンド・新フラグ・新キーは無し。

### 影響範囲 (実装済み)

- `internal/ui/chat_casebuilder.go` (`testReplay` 型・`execTest` で `lastTest` 記録・`execReplay` の優先順位分岐・`flowInput` 抽出・`showCheat`)、`internal/ui/chat.go` (`chatModel.lastTest`)。テスト: `internal/ui/chatreplay_test.go` (直近 `:test` 再生・手入力優先・再検証・反復再生)。docs: `atcoder-{test,start}-usage.md`・`atcoder-test-architecture.md`。

## AN. 提出前チェックをコメントアウト後ソースで実行 (`test --submit` / chat `Ctrl+S`) ✅ DONE

> 要件詳細は [`requirements/049-submit-precheck-run-commented-source.md`](requirements/049-submit-precheck-run-commented-source.md)。[AJ](#aj-提出前チェックと確認プロンプト-test---submit--chat-ctrls--done) (提出ゲート) のゲート実行対象を「提出される中身」へ差し替える改訂。[AI](#ai-提出準備時に-debug-出力行をコメントアウト-test---submit--chat-ctrls--done) (DEBUG コメントアウト) の出力を実行対象にする。

### 決まったこと (この項目で実装したこと)

- 提出ゲートのサンプル判定を、解答ファイル本体ではなく **「提出される中身」(= `[DEBUG]` print をコメントアウトしたソース、`--keep-debug` なら解答そのまま)** に対して実行する。コメントアウト後の中身を **一時ファイル** に書き出し、`testexec.Run` の `SolutionPathOverride` で実行対象に差す。解答ファイル本体は不変。
- これによりデバッグ中の無条件 `print("[DEBUG]…")` はコメントアウトされて実行されず、stdout がクリーンになって **PASS/FAIL が意味を持ち**、`DebugSeen` は「コメントアウトをすり抜けた `[DEBUG]` 出力」だけを拾う安全網になる。ゲート全条件 (実行可否・全通過・DEBUG 検出) が「実際に提出される状態」を反映する。
- ゲートで実行する中身とクリップボードへ載せる中身は **同一文字列を共有** (1 度構築)。「判定は通ったが別物を提出する」ズレを排除。確認 UI・exit code・理由文言は [AJ](#aj-提出前チェックと確認プロンプト-test---submit--chat-ctrls--done) のまま。

### 影響範囲 (実装済み)

- `internal/testexec/test.go` (`Options.SolutionPathOverride` + `Run` の解決分岐、`_test.go`)。`cmd/atcoder/submitprep.go` (`submitSource`/`buildSubmitSource`/`writeTempSource`、`runSubmitPrep` をコメントアウト後実行へ組み替え、解答の二度読み除去)、`cmd/atcoder/adhoc.go` (`chatSubmitCheckFunc` をコメントアウト後実行へ)。`fixtures/` (コメントアウト後にクリーン化して提出準備へ進む非 TTY スモーク) + `fixtures/run.sh`。`fixtures/README.md` / `docs/tools/atcoder-test-{usage,architecture,testing}.md`。

## AQ. chat command モードからの meta 編集 (`:meta` url / time_limit) ✅ DONE (8e79fa9)

> 要件詳細は [`requirements/055-chat-meta-edit.md`](requirements/055-chat-meta-edit.md)。利用手引は [`atcoder-meta-usage.md`](atcoder-meta-usage.md) / [`atcoder-test-usage.md`](atcoder-test-usage.md) / [`atcoder-start-usage.md`](atcoder-start-usage.md) の command モードのコマンド表。CLI 側の元仕様は [AL](#al-task-url-直指定の-dl--meta-編集-atcoder-meta--done-94d8937-url-override-後続コミット) ([046](requirements/046-meta-command.md))、フック注入の前例は [U](#u-chat-内からの提出準備-ctrls--done-c5d3227) ([026](requirements/026-chat-submit.md))。

### 決まったこと (この項目で実装したこと)

- chat の command モードに **`:meta`** を追加。`:meta` でキャッシュ済み `meta.toml` の **url / time limit / samples** を表示し、`:meta url <url>` で取得元 URL override、`:meta time_limit <dur>` (`5s`/`1500ms`) で Time Limit を上書きする (CLI `atcoder meta show` / `set --url|--time-limit` 相当)。`:meta url` / `:meta time_limit` (値なし) は当該フィールドの現在値のみ表示。
- 編集対象 (url/time_limit)・検証規則 (AtCoder URL のみ / `> 0` duration)・未キャッシュ時の非対称 (url は空 meta に書ける / time_limit はキャッシュ前提) は CLI [AL](#al-task-url-直指定の-dl--meta-編集-atcoder-meta--done-94d8937-url-override-後続コミット) と完全一致。`time_limit` 更新時は chat ヘッダの Time Limit 表示も更新し、続く `:test` の TLE 判定に反映する。
- **fetch しない** — キャッシュ済み `meta.toml` のみ読み書き。`internal/ui` は `testexec`/`layout`/`cmd/atcoder` に新規依存せず、meta の読み書き・検証は `ChatHeader.MetaShow`/`MetaSet` の**注入フック**で composition root に逃がす ([U](#u-chat-内からの提出準備-ctrls--done-c5d3227) の `Submit` と同じ層境界)。

### 影響範囲 (実装済み)

- `internal/ui/chat.go` (`ChatHeader.MetaShow`/`MetaSet` フック)、`internal/ui/chat_casebuilder.go` (`parseCommand` の `meta`・`execCommand` の `case "meta"`・`execMeta`・`newCommandInput`/`showCheat`)、`internal/ui/command_complete.go` (`completeNamesBase` + `completeSubTokens["meta"]` + `completeExpectsArg`)、`cmd/atcoder/chatmeta.go` (**新規**: `chatMetaShowFunc`/`chatMetaSetFunc`)、`cmd/atcoder/start.go`・`adhoc.go` (フック注入)。テスト: `internal/ui/chatmeta_test.go`・`command_complete_test.go`・`cmd/atcoder/chatmeta_test.go`。docs: `atcoder-{meta,test,start}-usage.md`・`atcoder-test-architecture.md`。

## AR. chat scrollback の右端スクロールバー ✅ DONE

> 要件詳細は [`requirements/056-chat-scrollbar.md`](requirements/056-chat-scrollbar.md)。スクロール機構そのものは command [033](requirements/033-command-mode-scrollback-paging.md) / insert [040](requirements/040-insert-mode-scrollback-paging.md) のまま不変で、その**現在地を視覚化**する表示追加。

### 決まったこと (この項目で実装したこと)

- chat の scrollback (viewport) が 1 画面に収まらず**スクロール可能なときだけ**、viewport の**右端 1 列**に縦スクロールバー (track `│` dim + thumb `█` やや明るい) を描画。thumb の長さ・位置は `表示高 × 表示高 / 総行数` と `ScrollPercent()` から算出し、最下部 (追従中) で下端・最上部で上端に来る。
- **gutter は常時確保**: 本文の折り返し幅を常に `width-1` (= `contentWidth()`) にして、overflow の開始/終了で既存行がリフローしないようにした。収まっているとき・端末幅が狭い (`width < 2`) ときは gutter を空白にしてスクロールバーを描かない。
- キー割当・追従ロジック (033/040)・送信・入力履歴・command/builder モード・子プロセス・判定・exit code は不変。純粋な viewport 描画への追加。insert/command で viewport 描画は共通なので両モードで同じバーが出る。

### 影響範囲 (実装済み)

- `internal/ui/chat.go` (`contentWidth()`・`renderViewport()`・`scrollbarColumn()` を追加、`WindowSizeMsg`/`refreshViewport`/`View` の幅を `contentWidth()` 経由に、`chatScrollTrackStyle`/`chatScrollThumbStyle` を追加)。テスト: `internal/ui/chatscrollbar_test.go` (新規: scrollable で track+thumb 表示・最下部で下端・上スクロールで thumb 上昇・収まれば空白・`width<2` で非表示・gutter 確保)。docs: `atcoder-start-usage.md`。

## AS. chat command モードからの meta 再取得 (`:meta fetch`) ✅ DONE

> 要件詳細は [`requirements/057-chat-meta-fetch.md`](requirements/057-chat-meta-fetch.md)。chat の `:meta` ([AQ](#aq-chat-command-モードからの-meta-編集-meta-url--time_limit--done-8e79fa9) / [055](requirements/055-chat-meta-edit.md)) に再取得を足す。CLI 側の元仕様は [AL](#al-task-url-直指定の-dl--meta-編集-atcoder-meta--done-94d8937-url-override-後続コミット) ([046](requirements/046-meta-command.md)) の `meta fetch`、非同期実行の前例は `Ctrl+E` ([038](requirements/038-chat-edit-command.md)) の `editDoneMsg`。

### 決まったこと (この項目で実装したこと)

- chat の `:meta` に **`:meta fetch`** を追加。`:meta url <url>` で取得元 URL を直した後に、その url (override 優先・なければ既定 URL) からサンプル + Time Limit を**強制再取得** (`testexec.EnsureTests` refresh=true) して `tests/` と `meta.toml` を更新する (CLI `atcoder meta fetch` 相当)。Time Limit が変われば chat ヘッダの Time Limit 表示も更新し、続く `:test` の TLE 判定に反映する。
- fetch はネットワーク呼び出し (数秒) を伴うため、`tea.Cmd` (goroutine) で**非同期**実行し UI をブロックしない。即 `(再取得中…)` を 1 行出し、完了で `metaFetchDoneMsg` を受けて結果行 (`fetched/url/time limit/samples`) を積む ([038](requirements/038-chat-edit-command.md) の `editDoneMsg` と同型)。取得進捗は **サイレント reporter** (`testexec.NewSummaryReporter`) で握りつぶし stdout を汚さない。
- 取得経路・url override 解決・`tests-extra` 非破壊は CLI [AL](#al-task-url-直指定の-dl--meta-編集-atcoder-meta--done-94d8937-url-override-後続コミット) と一致。`internal/ui` は `testexec`/`cmd/atcoder` に新規依存せず、再取得は `ChatHeader.MetaFetch` の**注入フック**で composition root に逃がす ([AQ](#aq-chat-command-モードからの-meta-編集-meta-url--time_limit--done-8e79fa9) の `MetaShow`/`MetaSet` と同じ層境界)。

### 影響範囲 (実装済み)

- `internal/ui/chat.go` (`ChatHeader.MetaFetch` フック・`metaFetchDoneMsg` 型・`Update` の `case metaFetchDoneMsg`)、`internal/ui/chat_casebuilder.go` (`execMeta` の `case "fetch"`・`metaFetch`・`applyMetaFetchDone`・`parseCommand`/`showCheat` の追記)、`internal/ui/command_complete.go` (`completeSubTokens["meta"]` に `fetch`)、`cmd/atcoder/chatmeta.go` (`chatMetaFetchFunc`)、`cmd/atcoder/start.go`・`adhoc.go` (フック注入)。テスト: `internal/ui/chatmeta_test.go`・`command_complete_test.go`。docs: `atcoder-{meta,test,start}-usage.md`・`atcoder-test-architecture.md`。

## AT. chat / start TUI の `Ctrl+Z` サスペンド ✅ DONE

> 要件詳細は [`requirements/058-chat-ctrl-z-suspend.md`](requirements/058-chat-ctrl-z-suspend.md)。bubbletea 公式の `tea.Suspend` を配線するだけの薄い追加で、独自シグナル処理は足さない。前例は `Ctrl+G` ([AC](#ac-start-watch-ペインの詳細表示-失敗ケースの-diff-ctrlg--done-d35185e)) / `Ctrl+E` ([AE](#ae-start--chat-から解答をエディタで開く-ctrle-nvim-remote--done)) の chat 未使用キー横取りパターン。

### 決まったこと (この項目で実装したこと)

- chat (`test --interactive`) と start 分割画面で **`Ctrl+Z`** を押すとプロセスを **SIGTSTP でサスペンド** (シェルのジョブとして一時停止)。`fg` で再開・`jobs` で一覧。bubbletea は altscreen 破壊回避のため Ctrl+Z を自動処理しないので、`tea.KeyCtrlZ` を捕捉して **`tea.Suspend`** を返す配線にした。端末の解放/復元/再描画は bubbletea の `suspend()`/`RestoreTerminal()` 任せ (非 altscreen は `repaintMsg`、altscreen は再入で自動再描画) なので `ResumeMsg` の明示処理は不要。
- chat 側は `KeyMsg` 先頭 (Ctrl+D 武装解除の直後・モード分岐より前) で捕捉するので **insert / command / builder の全モード**で有効。split 側も詳細横取りより前で捕捉し**詳細表示中 (Ctrl+G 中) でも有効**。解答の子は kill せずプロセスグループごと停止し `fg` でまとめて再開。Windows は `suspendSupported=false` で安全に no-op。
- Ctrl+C (中断再起動) / Ctrl+D (リセット・2連で終了) / Ctrl+S / Ctrl+E / Ctrl+G / スクロール系は不変。exit code 規約も不変 (Ctrl+Z は終了経路ではない)。

### 影響範囲 (実装済み)

- `internal/ui/chat.go` (`Update` の `KeyMsg` 冒頭で `tea.KeyCtrlZ` → `tea.Suspend`・placeholder ヘルプに `Ctrl+Z` 追記)、`internal/ui/startsplit.go` (`Update` の `KeyMsg` 冒頭で同捕捉・最下部ヘルプ 2 本に `Ctrl+Z` 追記)。テスト: `internal/ui/chatsuspend_test.go` (新規: insert/command/split-通常/split-詳細で `tea.Suspend` を返す・placeholder に Ctrl+Z)。docs: `atcoder-start-usage.md`・`atcoder-test-usage.md`。

## AU. 制約・入力形式からのランダム入力生成 (`atcoder gen` / chat `:gen`) 📝 設計済み (未実装)

> 要件詳細は [`requirements/060-gen-random-input.md`](requirements/060-gen-random-input.md)。方針の決定記録は [ADR 0008](decisions/0008-gen-best-effort-raw-cache.md)。追加ケースの保存規約は [V. 入出力ケース作成](#v-インタラクティブからの入出力ケース作成--ライブ検証--done) ([要件 024](requirements/024-interactive-case-builder.md))、fetch/cache 基盤は [AL](#al-task-url-直指定の-dl--meta-編集-atcoder-meta--done-94d8937-url-override-後続コミット) ([要件 046](requirements/046-meta-command.md))。

### 解きたい問題

- サンプルは PASS でも提出で WA/TLE/RE、というとき、手元で大量・大規模な入力を試したい。現状のテストデータ手段は chat `:case` の**手入力** (要件 024) か他問題のサンプル流用のみで、edge / 大規模ケースを自作する摩擦が大きい。
- 問題を読めば「入力形式」と「制約」は必ず書いてある。そこから機械的にランダム入力を作れれば、WA 再現の探索が速くなる。

### 決めること (設計で確定済み)

- **ベストエフォート即生成**に倒す。拾えた制約でその場でランダム入力を吐き、取りこぼした変数は既定レンジ + 警告、構造的制約 (順列・連結・単調等) は無視して独立生成し `coverage=partial` を明示 (ADR 0008)。完全自動認識・generator 雛形出力・ストレステストはスコープ外 (将来の拡張余地)。
- 用途は**ランダム入力を作るだけ** (出力の正しさ検証はしない)。出力先は stdout / `--out <path>` / `--save` で `tests-extra/` に**入力のみケース** (空 `.out`, 要件 024 で許容済み) として追加。
- CLI 表面は独立サブコマンド **`atcoder gen <contest> --task <letter>`** と対話 chat 内 **`:gen`** の両方。
- 解析元の**生テキスト**を新ファイル `gen.toml` (`[raw]`) にキャッシュ (解析済み構造ではなく)。生成のたびに生テキストから `Spec` を組む → 解析器改善が再 fetch なしで効き、将来のストレステスト / 雛形出力も同じ入力を使える (ADR 0008)。抽出は既存 `fetchProblem` の同一 HTML から拾い追加 HTTP を出さない。
- 不変則: 解答ファイル不可侵 / `--refresh` はキャッシュのみ / exit code (引数誤り=2・実行時失敗=1・成功=0) / 標準 `flag` 維持。

### 影響範囲 (実装は feature フェーズ)

- 新規 `internal/gen/` (`Raw`/`Var`/`Block`/`Spec`・`ParseSpec`・`Generate`・`gen.toml` load/save)、新規 `cmd/atcoder/gen.go`、`internal/testexec/fetch.go` (制約・入力形式節の抽出 + `gen.toml` 保存フック)、`cmd/atcoder/main.go` (dispatch/usage)、`internal/cliargs` (`--out`/`--count`/`--size`/`--seed`)、`internal/complete` (`gen` 候補)、`internal/ui/chat.go` (`:gen`)、`fixtures/run.sh` (シード固定スモーク)。利用手引 `atcoder-gen-usage.md` を新規作成。

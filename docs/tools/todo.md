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

> 要件詳細は [`docs/tools/requirements/022-interactive-watch-reload.md`](requirements/022-interactive-watch-reload.md)、利用手引は [`atcoder-test-usage.md`](atcoder-test-usage.md)。

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

### 追記: watch 待機中のキーアクション ✅ DONE

> 要件詳細は [`docs/tools/requirements/019-start-key-actions.md`](requirements/019-start-key-actions.md)。

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
- 追記 (要件 [030](requirements/030-interactive-ctrl-d-reset-then-quit.md)) ✅ DONE (5984e17): `Ctrl+D` を**「1 回目=プログラムをリセット (`restart()` 相当・chat 残留) / 2 回連続=chat 終了」**に変更。021/022 の「単押し即終了」を置き換え、終了を 2 連続押下に格上げ (誤爆耐性)。「連続」は間に他のキー入力が挟まらないこと (出力到着等の非キーは武装を解かない)。`Ctrl+C` (中断再起動) は据え置き。状態は `ctrlDArmed` 1 つ、`KeyMsg` 先頭クリア + `Ctrl+D` 再武装の対称実装。insert モードのみ (command/builder は不変)。

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

> 要件詳細は [`requirements/025-interactive-waiting-spinner.md`](requirements/025-interactive-waiting-spinner.md)。

- chat TUI で **入力送信後〜次の出力が来るまで**、入力ボックスの下罫線に**スピナー (braille) + 経過時間** (`⠹ 430ms ───`) をライブ表示。出力到着・子終了・リロードで解除。「打ったのに無反応 / 重いのか固まったのか」を可視化する。
- 下罫線への重ね描きで**画面の行数は不変** (分割画面 `start` の高さ計算を崩さない)。tick は待機中だけ回す (busy-loop にしない)。世代タグ (`spinGen`) で連続送信でも tick ループは 1 本。
- `internal/ui/chat.go` に待機状態 + `spinnerTickMsg`/`spinnerTickCmd` + 純粋関数 `waitStatus` を追加。状態遷移と `waitStatus` をユニットテスト、アニメ自体は TTY 必須で手動確認。

## U. chat 内からの提出準備 (`Ctrl+S`) ✅ DONE (c5d3227)

> 要件詳細は [`requirements/026-chat-submit.md`](requirements/026-chat-submit.md)。ABC ロードマップ [C. 提出](abc-todo.md) の chat 経路を畳む。

- インタラクティブ chat (`test --interactive` と `start` 分割画面の下ペイン) 中に **`Ctrl+S`** で提出準備 (`test --submit` 相当 = 解答コピー + 提出ページ起動、**実 POST はしない**)。chat を抜けず・子を kill せず実行し、結果を 1 行表示。
- トリガーは**独立した予約キー `Ctrl+S`** (024 のコマンドモードは未実装で大きいので entangle を避ける)。024 実装後に `:submit`/`:s` を同じ submit コールバックのエイリアスにできる。
- **サンプルゲート無し** (chat はバッチ判定が走っていない)。`test --submit` (ゲートあり) との意図的な差。
- 層: `internal/ui` は `cmd/atcoder` を import 不可 → `ChatHeader.Submit` コールバックを注入。`test --interactive` は `adhoc.go` の `makeChatRunner`、`start` は分割画面なので `start.go` の `ui.RunStartSplit` 用 `ChatHeader` に `chatSubmitFunc(contest, task, lay)` を各々注入。`prepareSubmission` を非印字 core (`submitPrepCore`) に分離。
## V. 位置引数とフラグの順序非依存 (`internal/cliargs`) ✅ DONE (87ba3ab)

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

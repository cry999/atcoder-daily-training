# インタラクティブ chat に meta 編集 `:meta` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) に **`:meta`** を足す。対話で解答をデバッグしている最中に、その問題の `meta.toml` の **取得元 URL** と **Time Limit** を **chat を抜けずに**表示・編集できるようにする。これは CLI の `atcoder meta show` / `atcoder meta set --url|--time-limit` ([046](046-meta-command.md)) を chat 内へ持ち込むもので、編集対象・検証規則・キャッシュ操作はすべて [046] と同一にする。新フラグ・新パッケージ・ネットワーク経路は増やさない。`internal/ui` (chat) は fetch/judge/testexec を知らない層境界を保ち、meta の読み書きは `ChatHeader` に**注入する関数フック** (`Ctrl+S` 提出準備の `Submit` ([026](026-chat-submit.md)) と同じパターン) で composition root (`cmd/atcoder`) に委譲する。

## 背景・目的

- chat で対話デバッグ中に「この問題の Time Limit が AtCoder の HTML 変更でずれて取れていない」「task_id が contest と食い違うので取得元 URL を直したい」(例 abc111 の D = `arc103_b`) と気づいても、いまは **一度 chat を抜けて** `atcoder meta set ...` を別に叩き直す必要がある。`:meta` があれば対話の流れを切らずに直せる。
- とくに Time Limit は chat ヘッダ ([startsplit](../atcoder-test-architecture.md)) に出ており、`:test` ([045](045-chat-run-sample-case.md)) のライブ実行でも TLE 判定に効く。chat 内で `:meta time_limit 5s` と直せば、ヘッダ表示にも即反映でき、続く `:test` がその値で走る。
- 必要な部品はすべて揃っている: meta 読み書きの公開 API (`testexec.LoadMeta` / `SaveMeta` / `SampleCount`、[046])、URL 検証 (`layout.IsTaskURL`、[046])、duration パース (Go 標準 `time.ParseDuration`)、そして chat へ外部作用を注入する確立パターン (`ChatHeader.Submit` / `Edit` / `RecordInput`、[026])。これらを束ねるだけで実現でき、新しい設計判断を増やさない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 表示 (`:meta`) | キャッシュ済み `meta.toml` の **url / time limit / samples** を info 行で表示 (CLI `meta show` 相当) | `fetched_at` 等の追加フィールド表示 / JSON |
| URL 編集 (`:meta url <url>`) | 取得元 URL の override を書き込む。値は AtCoder URL (`atcoder.jp/` か `://` を含む) のみ。CLI `meta set --url` と同一 ([046]) | 任意フィールドの編集 |
| Time Limit 編集 (`:meta time_limit <dur>`) | `5s` / `1500ms` 等の duration を `time_limit_ms` に変換して上書き。`> 0` のみ。CLI `meta set --time-limit` と同一 ([046])。成功時は chat ヘッダの Time Limit 表示も更新 | ヘッダ更新の他フィールド波及 |
| フィールド単独表示 (`:meta url` / `:meta time_limit` 値なし) | 当該フィールドの現在値のみを info 行で表示 | — |
| 取得 | **しない**。`:meta` は AtCoder へ fetch しない (取得は `atcoder meta fetch` / `atcoder test` が担う) | chat 内 `:meta fetch` (要 reporter 配線) |

### 境界

- 子プロセス・判定 (`testexec`/`runexec`)・exit code・`Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+E`・既存コマンド (`:case`/`:w`/`:set`/`:debug`/`:replay`/`:cheat`/`:q`/`:test`/`:task`/`:contest`/`:e`) は不変。
- **層境界を保つ**: `internal/ui` は `cmd/atcoder` を import しない ([026] と同じ)。meta の読み書き (`testexec.LoadMeta`/`SaveMeta`)・URL 検証 (`layout.IsTaskURL`)・duration パースはすべて composition root 側で行い、chat はフック呼び出しと info 行表示・ヘッダ更新だけを担う。`internal/ui` に `testexec`/`layout` への新規 import は増やさない。
- **解答非破壊**: `meta` はキャッシュ層 (`meta.toml`) のみ操作。解答ファイル・`tests/`・`tests-extra/` は読み書きしない ([046] と同じ安全設計)。
- stdout には何も書かない (chat 内の info 行のみ)。バッチ `meta`/`test`/`run` 経路には触れない。
- 編集対象は **url / time_limit の 2 フィールドに限定** (CLI `meta set` と一致)。それ以外のフィールド (contest/task/fetched_at) は触らない。

## meta の格納先とスキーマ

[046] と同じキャッシュ階層・スキーマ (新規ディレクトリ・新規フィールドは作らない):

```
$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/meta.toml
```

| フィールド | 型 | `:meta` での扱い |
|---|---|---|
| `contest` | string | 表示・編集しない (chat ヘッダの contest_id) |
| `task` | string | 表示・編集しない (chat ヘッダの task_id) |
| `url` | string | `:meta url <url>` で override。表示対象 |
| `time_limit_ms` | int | `:meta time_limit <dur>` で上書き。表示対象。ヘッダ Time Limit にも反映 |
| `fetched_at` | time | 表示・編集しない (当面) |

chat の `ChatHeader.Contest` / `.Task` には起動時に contest_id (`abc457`) / task_id (`abc457_d`) が入っており ([start.go `buildTarget`](../../cmd/atcoder/start.go) / [adhoc.go `makeChatRunner`](../../cmd/atcoder/adhoc.go))、これがそのまま `LoadMeta(contest, task)` / `SaveMeta(contest, task, m)` のキーになる。

## CLI / TUI 仕様

新フラグ無し。すべて command モード (insert で `Esc` → `:`) の内側。

### コマンド一覧 (追加分)

| コマンド | 動作 |
|---|---|
| `:meta` | キャッシュ済み meta の url / time limit / samples を表示 (`meta show` 相当) |
| `:meta url` | 現在の url のみ表示 |
| `:meta url <url>` | url override を書き込む (AtCoder URL のみ) |
| `:meta time_limit` | 現在の time limit のみ表示 |
| `:meta time_limit <dur>` | Time Limit を `<dur>` (`5s` / `1500ms`) に上書き。ヘッダ表示も更新 |

- 別名は設けない (`:meta` のまま)。`parseCommand` で `meta` を canonical `meta` に正規化する。
- フィールド名は meta.toml のキーに合わせ `url` / `time_limit` (CLI フラグ `--time-limit` のハイフンに対し、サブトークンはアンダースコア)。
- 補完 ([031](031-command-mode-completion.md)): canonical 名 `meta` を常時候補に出す (`NavEnabled` に依らない)。第 2 トークンは既知サブトークン `url` / `time_limit` を `completeSubTokens` に登録。`completeExpectsArg["meta"] = true` (フィールド/値を取るので一意確定時は末尾に空白)。

### `:meta` (引数なし) の動作

1. command モードを抜けて元のモード (builder 中なら builder、ふだんは insert) へ戻る ([039](039-chat-replay-previous-session.md) の復帰と同じ)。
2. `Meta` フックが未注入 (nil) なら info 行 `(メタ編集はこの画面では使えません)` を 1 本積んで終了。
3. フックの **show** を呼ぶ。成功なら url / time limit / samples を info 行群で表示する。未キャッシュ (`meta.toml` 無し) なら info 行 `(meta が未取得です — atcoder test / meta fetch で取得してください)` を積む。

### `:meta <field> [value]` の動作

1. command モードを抜けて元のモードへ戻る。
2. `Meta` フック未注入なら 2. と同じ info 行で終了。
3. `field` が `url` / `time_limit` のいずれでもなければ info 行 `E518: unknown meta field :meta <field>` を積んで終了。
4. **value 省略** (`:meta url` / `:meta time_limit`): フックの show を呼び、当該フィールドの現在値のみを 1 行表示する。
5. **value あり**: フックの **set** を `(field, value)` で呼ぶ。
   - 成功: フックが返した結果行 (例 `time limit: 2000 ms -> 5000 ms` / `url: (none) -> https://...`) を info 行で積む。`time_limit` を更新したときはフックが返す新しい `time_limit_ms` で `m.header.TimeLimitMs` を更新し、ヘッダ再描画に反映する。
   - 失敗 (検証エラー: URL 不正 / duration パース失敗 / `<= 0` / 未キャッシュ): フックが返した err を info 行 (err) で 1 本積む。chat は継続する。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:meta` (キャッシュ有り) | `url: ... / time limit: 2000 ms / samples: 3` を表示 |
| `:meta` (未キャッシュ) | `(meta が未取得です — atcoder test / meta fetch で取得してください)` |
| `:meta url` | 現在の url を 1 行表示 (未設定なら `url: (none)`) |
| `:meta url https://atcoder.jp/contests/abc111/tasks/arc103_b` | url override を書き込み、`url: (none) -> https://...` を表示 |
| `:meta url not-a-url` | `(--url は AtCoder の URL を指定してください)` (検証失敗、書き込まない) |
| `:meta time_limit` | 現在の time limit を 1 行表示 |
| `:meta time_limit 5s` | `time_limit_ms` を 5000 に上書き、`time limit: 2000 ms -> 5000 ms` を表示、ヘッダ Time Limit も 5000 ms に更新 |
| `:meta time_limit 0` / `:meta time_limit -1s` | `(--time-limit は正の duration を指定してください)` (書き込まない) |
| `:meta time_limit abc` | duration パース失敗の err 行 (書き込まない) |
| `:meta time_limit 5s` (未キャッシュ) | `(meta が未取得です — ...)` ([046] の `set --time-limit` 前提と同じ。url と違い未キャッシュには書かない) |
| `:meta foo` | `E518: unknown meta field :meta foo` |
| `:meta` (builder 中) | builder に戻ってから表示する (builder は破棄しない。`:set`/`:debug`/`:test` と同じ復帰) |
| `Meta` フック未注入の chat | `(メタ編集はこの画面では使えません)` (表示も編集もしない) |
| 編集後の `:test` | 更新後の `time_limit_ms` で TLE 判定される (ヘッダと meta が一致) |

`url` は [046] と同じく **スロット未キャッシュでも書き込める** (空の `meta.toml` を作って url だけ記録)。`time_limit` は [046] と同じく **キャッシュ済みが前提** (未取得なら案内のみ)。この非対称は CLI と一致させる。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader` に meta フック 2 つを追加: `MetaShow func(field string) ([]string, error)` (field="" で全体、`url`/`time_limit` で当該行)、`MetaSet func(field, value string) (lines []string, newTimeLimitMs int, err error)`。型ドキュメントコメントを付す ([026] の `Submit`/`SubmitCheck` と同じ注入様式) |
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `meta`→`meta` を追加。`execCommand` に `case "meta": return m.execMeta(cmd.arg)`。`execMeta(arg) tea.Cmd` ヘルパ (引数/フィールド分岐・フック呼び出し・info 行・`time_limit` 成功時の `header.TimeLimitMs` 更新) を追加。`newCommandInput` placeholder と `showCheat` に `:meta` を追記 |
| `internal/ui/command_complete.go` | `completeNamesBase` に `meta` を追加。`completeSubTokens["meta"] = {"time_limit", "url"}`、`completeExpectsArg["meta"] = true` |
| `cmd/atcoder/chatmeta.go` (新規) | composition root のフック生成: `chatMetaShowFunc(contest, task) func(string) ([]string, error)` と `chatMetaSetFunc(contest, task) func(string, string) ([]string, int, error)`。`testexec.LoadMeta`/`SaveMeta`/`SampleCount`・`layout.IsTaskURL`・`time.ParseDuration` を使い、`atcoder meta show`/`set` ([046] `cmd/atcoder/meta.go`) と同じ検証・整形ロジックを共有/再現する |
| `cmd/atcoder/start.go` | `buildTarget` の `ui.ChatHeader{...}` に `MetaShow: chatMetaShowFunc(contestID, task)` / `MetaSet: chatMetaSetFunc(contestID, task)` を注入 |
| `cmd/atcoder/adhoc.go` | `makeChatRunner` の `ui.ChatHeader{...}` に同 2 フックを注入 (`test --interactive` 経路) |
| `internal/ui/chatmeta_test.go` (新規) | `execMeta` の各分岐を fake フックで検証: 引数なしで show 行が積まれる、`url <url>`/`time_limit <dur>` で set が呼ばれ結果行が積まれる、`time_limit` 成功で `header.TimeLimitMs` が更新される、未知フィールドで `E518`、フック nil で「使えません」、set の err が err 行になる |
| `internal/ui/command_complete_test.go` | 候補一覧の期待値に `meta` を反映。`:me`→`meta ` (空白付き) 確定、第 2 トークン `url`/`time_limit` 補完のケースを追加 |
| `cmd/atcoder/chatmeta_test.go` (新規, 任意) | `chatMetaSetFunc` の検証 (url 不正/duration 不正/未キャッシュ time_limit) を一時 `XDG_CACHE_HOME` で固定 |
| `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` | command モードのコマンド表に `:meta` を追記 |
| `docs/tools/atcoder-meta-usage.md` | chat からの編集 (`:meta`) への相互リンクを 1 行追記 |
| `docs/tools/atcoder-test-architecture.md` | chat の command モード節に `:meta` (meta 表示・編集フック) を追記 |
| `docs/tools/todo.md` | ロードマップ項目を追記し本要件へ相互リンク |

### 注入フックの素描

```go
// internal/ui/chat.go (package ui) — ChatHeader に追加。Submit/Edit と同じ注入様式。

// MetaShow は meta.toml の表示行を返す。field="" なら全体 (url/time limit/samples)、
// field="url"/"time_limit" なら当該フィールドのみ。未キャッシュ等は error。
// composition root が testexec.LoadMeta / SampleCount で整形する。
MetaShow func(field string) (lines []string, err error)

// MetaSet は field ("url"/"time_limit") を value で上書きし、結果行と
// (time_limit を更新したときの) 新しい time_limit_ms を返す。検証失敗・未キャッシュは error。
// composition root が layout.IsTaskURL / time.ParseDuration で検証し SaveMeta する。
MetaSet func(field, value string) (lines []string, newTimeLimitMs int, err error)
```

```go
// internal/ui/chat_casebuilder.go (package ui) — execMeta の骨子。
func (m *chatModel) execMeta(arg string) tea.Cmd {
    m.returnFromCommand()
    if m.header.MetaShow == nil || m.header.MetaSet == nil {
        m.addInfoLine("(メタ編集はこの画面では使えません)")
        return nil
    }
    f := strings.Fields(arg)
    switch {
    case len(f) == 0: // :meta → 全体表示
        m.metaShow("")
    case f[0] != "url" && f[0] != "time_limit":
        m.addInfoLine("E518: unknown meta field :meta " + f[0])
    case len(f) == 1: // :meta url / :meta time_limit → 当該フィールド表示
        m.metaShow(f[0])
    default: // :meta <field> <value> → 編集
        m.metaSet(f[0], strings.Join(f[1:], " "))
    }
    return nil
}
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `Meta` フック未注入 | info 行で「この画面では使えません」。実行も表示もしない (chat は継続) |
| 未知フィールド (`:meta foo`) | info 行 `E518: unknown meta field :meta foo` |
| `:meta` / `:meta <field>` で未キャッシュ | info 行で「未取得 — atcoder test / meta fetch」を案内 (表示はしない) |
| `:meta url` の URL 不正 | フックが検証で弾き、err 行を積む (書き込まない)。[046] の `set --url` 検証と同一規則 |
| `:meta time_limit` の duration 不正 / `<= 0` | フックが弾き、err 行を積む (書き込まない)。[046] の `set --time-limit` と同一 |
| `:meta time_limit` で未キャッシュ | err 行で「先に取得せよ」。[046] と同じ (url と違い未キャッシュには書かない) |
| `SaveMeta` の I/O 失敗 (権限等) | err 行を 1 本積んで終了 (chat は継続)。best-effort |
| exit code | 影響なし (表示と meta.toml 書き換えのみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変) |

chat 内コマンドなので exit code 経路は増えない (CLI `meta` の exit 2/1 とは別レイヤ)。検証失敗は err 行で吸収し、chat は落とさない。

## 非機能要件

- **既存非破壊**: 既存コマンド・キー・判定・chat の描画は不変。`:meta` を打たない限り従来どおり。`Meta` フック未注入なら `:meta` は「使えません」を返すだけ。
- **層境界保持**: `internal/ui` は `cmd/atcoder`・`testexec`・`layout` の meta/URL ロジックに新規依存しない。フック注入で composition root に逃がす ([026] と同じ)。`testexec.LoadMeta`/`SaveMeta` の呼び出しは `cmd/atcoder` 側に閉じる。
- **CLI との一貫性**: 編集対象 (url/time_limit)・検証規則 (AtCoder URL / `> 0` duration)・未キャッシュ時の url/time_limit 非対称は CLI `atcoder meta set` ([046]) と完全一致させる。挙動の二重定義を避けるため、フック実装は `cmd/atcoder/meta.go` の検証・整形と共通化できる部分は共有する。
- **解答非破壊**: 解答ファイル・`tests/`・`tests-extra/` に触れない。`meta.toml` のみ書き換える。
- **stdout 非汚染**: 表示は chat 内の info 行のみ。
- **ネットワーク非依存**: `:meta` は fetch しない。ローカルのキャッシュ済み `meta.toml` のみ読み書き。
- **決定的にテスト可能**: `execMeta` は fake フックで分岐・info 行・ヘッダ更新を検証できる ([045] の `chattest_test.go`、[026] の Submit テストと同型)。フック実装は一時 `XDG_CACHE_HOME` で検証できる。
- **スモーク**: 本機能は TUI/ローカル読み書きで `atcoder test`/`meta` の判定 exit code 経路を増やさないため、fixture (`fixtures/run.sh`) は新規追加せず**既存スモークが緑のまま**を確認する。挙動は `internal/ui`・`cmd/atcoder` の Go ユニットテストで固定する。

## 将来の拡張ポイント

- chat 内 `:meta fetch` (reporter を chat へ配線して再取得トリガ)。
- 編集対象フィールドの拡張 ([046] の将来拡張と歩調を合わせる)。
- `:meta` 表示の `fetched_at` 追加・整形強化。

## 用語

| 用語 | 例 | 意味 |
|---|---|---|
| `contest_id` | `abc457` | コンテスト ID。`ChatHeader.Contest` |
| `task_id` | `abc457_d` | タスク ID。`ChatHeader.Task`。`LoadMeta`/`SaveMeta` のキー |
| url override | `https://atcoder.jp/contests/abc111/tasks/arc103_b` | task_id が contest と食い違う問題の取得元 URL ([046]) |
| command モード | `:meta` | chat の `:` ex-command line ([024])。`Esc` で入る |
| 注入フック | `ChatHeader.MetaShow` / `.MetaSet` | `internal/ui` が外部作用を composition root に逃がす関数 ([026] の `Submit` と同様) |

## 関連ドキュメント

- CLI 側の元仕様 (編集対象・検証規則・url override): [046](046-meta-command.md) (`atcoder meta fetch|show|set`)
- command モード基盤: [024](024-interactive-case-builder.md) (ケースビルダー・ライブ検証)
- フック注入の前例: [026](026-chat-submit.md) (`Ctrl+S` 提出準備・`ChatHeader.Submit`)
- コマンド追加の前例: [030](030-chat-debug-cheat-commands.md) / [045](045-chat-run-sample-case.md) (`:test`) / 補完: [031](031-command-mode-completion.md)
- 利用手引: `docs/tools/atcoder-meta-usage.md` / `docs/tools/atcoder-test-usage.md` / `docs/tools/atcoder-start-usage.md`
- アーキテクチャ: `docs/tools/atcoder-test-architecture.md`
- ロードマップ: `docs/tools/todo.md`
</content>
</invoke>

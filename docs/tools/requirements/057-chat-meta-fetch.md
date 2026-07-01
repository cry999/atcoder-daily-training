# インタラクティブ chat に meta 再取得 `:meta fetch` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) の `:meta` ([055](055-chat-meta-edit.md)) に **`:meta fetch`** を足す。`:meta url <url>` で取得元 URL を直した後に、**chat を抜けずに**その URL からサンプル入出力と Time Limit を**再取得**して `meta.toml` + `tests/` を更新し、chat ヘッダの Time Limit 表示にも反映できるようにする。これは CLI の `atcoder meta fetch` ([046](046-meta-command.md)) を chat 内へ持ち込むもので、取得経路・キャッシュ操作はすべて [046] と同一にする。新フラグ・新パッケージ・新キャッシュ層は増やさない。`internal/ui` (chat) は fetch/judge/testexec を知らない層境界を保ち、再取得は `ChatHeader` に**注入する関数フック** (`MetaShow`/`MetaSet` ([055]) と同じパターン) で composition root (`cmd/atcoder`) に委譲する。fetch はネットワーク呼び出し (数秒) を伴うため、chat は `tea.Cmd` で**非同期**に呼び (`Ctrl+E` エディタ起動 ([038](038-start-edit-in-editor.md)) の `editDoneMsg` と同型)、完了通知 (`metaFetchDoneMsg`) を受けて結果行とヘッダを更新する。

## 背景・目的

- [055] で `:meta url <url>` を入れ、chat 内から取得元 URL を直せるようになった。しかし `:meta` は**ネットワーク非依存**で fetch しない設計のため、URL を直しても**サンプルと Time Limit は古いまま**で、新しい URL の問題内容には差し替わらない。反映するには一度 chat を抜けて `atcoder meta fetch` / `atcoder test` を叩き直す必要がある。
- task_id が contest と食い違う問題 (例 abc111 の D = `arc103_b`) を対話デバッグ中に、`:meta url https://atcoder.jp/contests/abc111/tasks/arc103_b` → `:meta fetch` と続けて打てば、対話の流れを切らずに正しいページのサンプル + Time Limit を引き直せる。
- [055] が「将来の拡張ポイント」として明記した **chat 内 `:meta fetch` (reporter を chat へ配線して再取得トリガ)** の実装。必要な部品はすべて揃っている: 強制再取得の公開 API (`testexec.EnsureTests(..., refresh=true)`、[046])、url override を尊重する取得経路 (`ensureTests` が `meta.toml` の `url` を読む、[046])、stdout を汚さないサイレント reporter (`testexec.NewSummaryReporter`)、chat へ外部作用を注入する確立パターン (`MetaShow`/`MetaSet` ([055])・`Edit` ([038]))、そして長時間処理を非同期に回す前例 (`editDoneMsg`)。これらを束ねるだけで実現でき、新しい設計判断を増やさない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 再取得 (`:meta fetch`) | `meta.toml` の url override (なければ既定 URL) からサンプル + Time Limit を**強制再取得** (`EnsureTests` refresh=true)。`atcoder meta fetch` と同一の取得経路・キャッシュ書き込み。`tests/` を更新し `tests-extra/` には触れない | コンテスト一括 fetch / 進捗スピナー表示 |
| ヘッダ反映 | 再取得で Time Limit が変われば chat ヘッダの Time Limit 表示を新値に更新する (`:meta time_limit` の反映と同じ) | url/サンプル数のヘッダ常時表示 |
| 結果表示 | `fetched <task>` / url / time limit / samples を info 行群で表示 (`atcoder meta fetch` の出力相当) | JSON / 差分表示 |
| 非同期実行 | fetch を `tea.Cmd` で goroutine 実行し、即「(再取得中…)」を 1 行出して UI をブロックしない。完了で `metaFetchDoneMsg` を受けて結果行を積む | 進捗スピナー (`waitStatus` 流用)・キャンセル |

### 境界

- 子プロセス・判定 (`testexec`/`runexec`)・exit code・`Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+E`・既存コマンド (`:case`/`:w`/`:set`/`:debug`/`:replay`/`:cheat`/`:q`/`:test`/`:task`/`:contest`/`:e`)・既存の `:meta` (引数なし / `url` / `time_limit`) ([055]) は不変。
- **層境界を保つ**: `internal/ui` は `cmd/atcoder`・`testexec`・`layout` を import しない ([055] と同じ)。再取得 (`testexec.EnsureTests`)・reporter 生成・結果整形はすべて composition root 側で行い、chat はフック呼び出し (非同期) と info 行表示・ヘッダ更新だけを担う。`internal/ui` に `testexec` への新規 import は増やさない。
- **解答非破壊**: `fetch` はキャッシュ層 (`meta.toml` + `tests/`) のみ操作。解答ファイル・`tests-extra/` (ユーザ追加ケース) は読み書きしない ([046] の `fetch` と同じ安全設計)。
- **stdout 非汚染**: 取得進捗は **サイレント reporter** (`testexec.NewSummaryReporter`) で握りつぶし、stdout には何も書かない。表示は chat 内の info 行のみ。CLI `meta fetch` のような stdout サマリは出さない。
- 編集対象・取得対象は [046]/[055] と一致。新フィールド・新キャッシュ階層は作らない。

## meta の格納先とスキーマ

[046]/[055] と同じキャッシュ階層・スキーマ (新規ディレクトリ・新規フィールドは作らない):

```
$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/
  meta.toml          # contest / task / url / time_limit_ms / fetched_at
  tests/
    01.in  01.out  ...
```

`:meta fetch` は `EnsureTests(reporter, contest, task, refresh=true)` を呼ぶ。これは内部で `ensureTests` が fetch 前に `meta.toml` の `url` override を読み (`resolveFetchURL`)、空でなければそれを、空なら既定 URL (`DefaultTaskURL`) を取得元にする ([046] の URL override 解決と同一)。よって直前の `:meta url <url>` で書いた override がそのまま反映される。取得後は `tests/NN.in|out` と `meta.toml` (url=使った URL / time_limit_ms / fetched_at) を書き直す。

## CLI / TUI 仕様

新フラグ無し。すべて command モード (insert で `Esc` → `:`) の内側。

### コマンド一覧 (追加分)

| コマンド | 動作 |
|---|---|
| `:meta fetch` | `meta.toml` の url (override 優先) からサンプル + Time Limit を再取得し、`tests/` と `meta.toml` を更新。Time Limit が変わればヘッダにも反映 (`atcoder meta fetch` 相当) |

- 補完 ([031](031-command-mode-completion.md)): 第 2 トークンの既知サブトークンに `fetch` を追加する (`completeSubTokens["meta"] = {"fetch", "time_limit", "url"}`)。`completeExpectsArg["meta"] = true` は [055] のまま。
- `fetch` は値を取らない (`:meta fetch <x>` の余分なトークンは無視する)。

### `:meta fetch` の動作

1. command モードを抜けて元のモード (builder 中なら builder、ふだんは insert) へ戻る ([055] と同じ復帰)。
2. `MetaShow`/`MetaSet`/`MetaFetch` フックのいずれかが未注入 (nil) なら info 行 `(メタ編集はこの画面では使えません)` を 1 本積んで終了 ([055] と同じガード)。
3. info 行 `(再取得中…)` を 1 本積み、`MetaFetch` フックを呼ぶ `tea.Cmd` (goroutine) を返す。UI はブロックしない。
4. 完了で `metaFetchDoneMsg{lines, newTimeLimitMs, err}` を受ける:
   - **成功**: フックが返した結果行 (`fetched <task>` / `url:` / `time limit:` / `samples:`) を info 行群で積む。`newTimeLimitMs > 0` なら `m.header.TimeLimitMs` を更新し、ヘッダ再描画に反映する。
   - **失敗** (ネットワーク / HTML パース / url 不正 / 未キャッシュで url override も無い): フックが返した err を info 行 (err) で 1 本積む。chat は継続する。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:meta url <url>` → `:meta fetch` | 新 url からサンプル + Time Limit を再取得。`fetched <task> / url: … / time limit: 2000 ms / samples: 3` を表示。Time Limit が変われば ヘッダも更新 |
| `:meta fetch` (url override 済み abc111_d) | `arc103_b` のページから取得し、スロットは `abc111_d` のまま `tests/` を更新 |
| `:meta fetch` (url 未設定・既定 URL でも取得可) | 既定 URL `https://atcoder.jp/contests/<contest>/tasks/<task>` から取得 |
| `:meta fetch` (取得失敗: ネットワーク / 404 / パース) | err 行 `(再取得に失敗しました: …)` を 1 本。chat 継続。ヘッダ・キャッシュは変えない (best-effort) |
| `:meta fetch` 中の UI | 即 `(再取得中…)` を表示し操作を受け付ける (非同期)。完了で結果行に続く |
| 再取得後の `:test` | 更新後の `tests/` と `time_limit_ms` で実行・TLE 判定される (ヘッダと meta が一致) |
| `:meta foo` (未知フィールド) | `E518: unknown meta field :meta foo` ([055] のまま。`fetch` は既知化される) |
| `Meta*` フック未注入の chat | `(メタ編集はこの画面では使えません)` (再取得もしない) |

`:meta fetch` は `tests-extra/` (ユーザ追加ケース) を消さない。`tests/` のサンプルのみ取得し直す ([046] の `fetch` と同じ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader` に meta 再取得フック 1 つを追加: `MetaFetch func() (lines []string, newTimeLimitMs int, err error)`。型ドキュメントコメントを付す ([055] の `MetaShow`/`MetaSet` と同じ注入様式)。`metaFetchDoneMsg{lines []string; newTimeLimitMs int; err error}` 型を追加し、`Update` の msg switch に `case metaFetchDoneMsg:` を足して結果行積み + ヘッダ更新 + `refreshViewport` を行う |
| `internal/ui/chat_casebuilder.go` | `execMeta` の分岐に `case f[0] == "fetch":` を追加し `return m.metaFetch()` (非同期 `tea.Cmd`) を返す。`metaFetch() tea.Cmd` ヘルパ (フック nil ガード・`(再取得中…)` 行・`MetaFetch` を呼ぶ goroutine `tea.Cmd`) と `applyMetaFetchDone(metaFetchDoneMsg)` ヘルパ (結果行 / err 行・`time_limit` 反映) を追加。`parseCommand` の `:meta` コメントと `showCheat` の `:meta` 行に `fetch` を追記 |
| `internal/ui/command_complete.go` | `completeSubTokens["meta"]` に `fetch` を追加 (`{"fetch", "time_limit", "url"}`) |
| `cmd/atcoder/chatmeta.go` | composition root の再取得フック生成 `chatMetaFetchFunc(contest, task) func() ([]string, int, error)` を追加。`testexec.NewSummaryReporter()` (stdout 非汚染) を渡して `testexec.EnsureTests(reporter, contest, task, true)` を呼び、`LoadMeta` で url を読んで `fetched/url/time limit/samples` 行を整形して返す (`cmd/atcoder/meta.go` の `metaFetch` 出力と体裁を揃える) |
| `cmd/atcoder/start.go` | `buildTarget` の `ui.ChatHeader{...}` に `MetaFetch: chatMetaFetchFunc(contestID, task)` を注入 |
| `cmd/atcoder/adhoc.go` | `makeChatRunner` の `ui.ChatHeader{...}` に `MetaFetch: chatMetaFetchFunc(contest, task)` を注入 (`test --interactive` 経路) |
| `internal/ui/chatmeta_test.go` | `:meta fetch` の分岐を fake フックで検証: `(再取得中…)` 行が積まれ非 nil cmd が返る、cmd が `MetaFetch` を呼ぶ、`applyMetaFetchDone` 成功で結果行が積まれ `header.TimeLimitMs` が更新される、err で err 行になる、フック nil で「使えません」 |
| `internal/ui/command_complete_test.go` | 第 2 トークン補完の期待値に `fetch` を反映 |
| `docs/tools/usage/test.md` / `docs/tools/usage/start.md` | command モードのコマンド表の `:meta` 行に `fetch` を追記 |
| `docs/tools/usage/meta.md` | chat からの再取得 (`:meta fetch`) への相互リンクを 1 行追記 |
| `docs/tools/atcoder-test-architecture.md` | chat の command モード節の `:meta` に `fetch` (再取得フック・非同期) を追記 |
| `docs/tools/todo.md` | ロードマップ項目を追記し本要件へ相互リンク |

### 注入フックの素描

```go
// internal/ui/chat.go (package ui) — ChatHeader に追加。MetaShow/MetaSet ([055]) と同じ注入様式。

// MetaFetch は :meta fetch (要件 057) で meta.toml の url (override 優先) から
// サンプル + Time Limit を再取得するフック。結果行と (Time Limit が変わったときの)
// 新しい time_limit_ms を返す。ネットワーク呼び出しを伴うため chat は tea.Cmd で
// 非同期に呼ぶ。composition root が testexec.EnsureTests(refresh=true) を
// サイレント reporter で実行する (internal/ui は testexec を知らないため)。
MetaFetch func() (lines []string, newTimeLimitMs int, err error)
```

```go
// internal/ui/chat.go (package ui) — 非同期完了通知。
type metaFetchDoneMsg struct {
    lines          []string
    newTimeLimitMs int
    err            error
}
```

```go
// internal/ui/chat_casebuilder.go (package ui) — metaFetch / applyMetaFetchDone の骨子。

func (m *chatModel) metaFetch() tea.Cmd {
    if m.header.MetaFetch == nil { // 念のため (execMeta 冒頭で Show/Set は確認済み)
        m.addInfoLine("(メタ編集はこの画面では使えません)")
        m.refreshViewport()
        return nil
    }
    m.addInfoLine("(再取得中…)")
    m.refreshViewport()
    fetch := m.header.MetaFetch
    return func() tea.Msg {
        lines, ms, err := fetch()
        return metaFetchDoneMsg{lines: lines, newTimeLimitMs: ms, err: err}
    }
}

func (m *chatModel) applyMetaFetchDone(msg metaFetchDoneMsg) {
    if msg.err != nil {
        m.addErrLine("(" + msg.err.Error() + ")")
        return
    }
    for _, l := range msg.lines {
        m.addInfoLine(l)
    }
    if msg.newTimeLimitMs > 0 {
        m.header.TimeLimitMs = msg.newTimeLimitMs
    }
}
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `Meta*` フック未注入 | info 行で「この画面では使えません」。再取得しない (chat は継続) |
| `:meta fetch` の取得失敗 (ネットワーク / HTML パース / url 不正 / 既定 URL も 404) | フックが error を返し、err 行を 1 本積む (キャッシュ・ヘッダは変えない)。[046] の `fetch` 失敗と同じ扱い |
| 取得中の追加 `:meta fetch` 連打 | 各 fetch が独立に走り、それぞれの完了で結果行を積む (best-effort。多重起動の抑止は当面しない) |
| exit code | 影響なし (chat 内コマンド。表示と meta.toml/tests 書き換えのみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変) |

chat 内コマンドなので exit code 経路は増えない。取得失敗は err 行で吸収し、chat は落とさない。

## 非機能要件

- **既存非破壊**: 既存コマンド・キー・判定・chat の描画は不変。`:meta fetch` を打たない限り従来どおり。`Meta*` フック未注入なら `:meta fetch` は「使えません」を返すだけ。`:meta` の他分岐 ([055]) は変えない。
- **層境界保持**: `internal/ui` は `cmd/atcoder`・`testexec`・`layout` に新規依存しない。フック注入で composition root に逃がす ([055]/[026] と同じ)。`testexec.EnsureTests`/`NewSummaryReporter` の呼び出しは `cmd/atcoder` 側に閉じる。
- **CLI との一貫性**: 取得経路 (`EnsureTests` refresh=true)・url override 解決・`tests-extra` 非破壊・結果行の体裁は CLI `atcoder meta fetch` ([046]) と一致させる。
- **解答非破壊**: 解答ファイル・`tests-extra/` に触れない。`meta.toml` + `tests/` のみ書き換える。
- **stdout 非汚染**: サイレント reporter で取得進捗を握りつぶす。表示は chat 内の info 行のみ。
- **UI 応答性**: fetch は `tea.Cmd` (goroutine) で非同期実行し、UI スレッドをブロックしない。即 `(再取得中…)` を出し、完了で結果行を追う (`editDoneMsg` と同型)。
- **決定的にテスト可能**: `metaFetch`/`applyMetaFetchDone` は fake フックで分岐・info 行・ヘッダ更新を検証できる ([055] の `chatmeta_test.go` と同型)。フック実装は一時 `XDG_CACHE_HOME` + ネットワーク有無で検証できる (本 fixture スモークは TUI 非対象)。
- **スモーク**: 本機能は TUI/非同期取得で `atcoder test`/`meta` の判定 exit code 経路を増やさないため、fixture (`fixtures/run.sh`) は新規追加せず**既存スモークが緑のまま**を確認する。挙動は `internal/ui`・`cmd/atcoder` の Go ユニットテストで固定する。

## 将来の拡張ポイント

- 取得中の進捗スピナー (`waitStatus` 流用) と多重起動の抑止 (`metaFetching` フラグ)。
- `:meta fetch` のコンテスト一括 fetch ([046] の将来拡張と歩調を合わせる)。
- url/サンプル数の chat ヘッダ常時表示 ([055] の将来拡張)。

## 用語

| 用語 | 例 | 意味 |
|---|---|---|
| `contest_id` | `abc457` | コンテスト ID。`ChatHeader.Contest` |
| `task_id` | `abc457_d` | タスク ID。`ChatHeader.Task`。`EnsureTests` のキー |
| url override | `https://atcoder.jp/contests/abc111/tasks/arc103_b` | task_id が contest と食い違う問題の取得元 URL ([046]/[055]) |
| サイレント reporter | `testexec.NewSummaryReporter` | 進捗を stdout に書かず捕捉する Reporter。TUI から取得経路を呼ぶのに使う |
| 注入フック | `ChatHeader.MetaFetch` | `internal/ui` が外部作用を composition root に逃がす関数 ([055] の `MetaShow`/`MetaSet` と同様) |

## 関連ドキュメント

- chat の `:meta` (表示・編集): [055](055-chat-meta-edit.md) (`:meta` / `:meta url` / `:meta time_limit`)
- CLI 側の元仕様 (取得経路・url override): [046](046-meta-command.md) (`atcoder meta fetch|show|set`)
- フック注入の前例: [026](026-chat-submit.md) (`Ctrl+S`) / [038](038-start-edit-in-editor.md) (`Ctrl+E`・`editDoneMsg` 非同期)
- command モード基盤 / 補完: [024](024-interactive-case-builder.md) / [031](031-command-mode-completion.md)
- 利用手引: `docs/tools/usage/meta.md` / `docs/tools/usage/test.md` / `docs/tools/usage/start.md`
- アーキテクチャ: `docs/tools/atcoder-test-architecture.md`
- ロードマップ: `docs/tools/todo.md`
</content>

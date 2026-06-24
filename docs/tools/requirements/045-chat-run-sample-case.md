# インタラクティブ chat に特定サンプルケース実行 `:test` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) に **`:test [case]`** を足す。キャッシュ済みのサンプルケース (公式 `tests/` + ユーザ追加 `tests-extra/`) の **1 つ**を指定し、その入力 (`.in`) を**子をリスタートしてクリーンな状態から順送**しつつ、期待出力 (`.out`) でライブ検証 ([024]) して各行に `✓`/`✗` を付ける。引数を省略すると**利用可能なケース ID の一覧**を表示する。再生は `:replay` ([039](039-chat-replay-previous-session.md)) の「子リスタート + 入力順送」機構と `:case` ([024]) の「expected ライブ検証」機構を組み合わせるだけで、新フラグ・新サブコマンド・新パッケージ・ネットワーク経路は増やさない。ケースの読み込み先 (`TaskDir`) と保存系統 (`extracase`) は既に `:w` で注入・利用済みのものをそのまま使う。

## 背景・目的

- 対話で解答をデバッグしていると、毎回**サンプル入力を手で打ち直す**ことになる。`:replay` ([039](039-chat-replay-previous-session.md)) は「直前に**自分が打った**入力」を再生できるが、**公式サンプルや `:w` で保存した追加ケース**を起点に「このケースを流して期待値と合うか」を chat 内で素早く試す手段が無い。
- バッチ `atcoder test` は全ケースをまとめて PASS/FAIL 判定するが、chat で 1 ケースだけ対話的に流して**どの行で食い違うか**をライブで見たいことがある (特にインタラクティブ問題・途中まで合っているが後半で崩れる問題)。
- 必要な機構はすべて揃っている: 子のクリーン再起動 + 入力順送 (`restart()` + `submitLines(..., record=false)`、[039]) と、expected による行ごとライブ検証 (`enableVerify` + `applyVerify`、[024])。ケースの場所も `:w` の保存先 `TaskDir` (公式 `tests/` と `extracase` の `tests-extra/`) で既知。これらを束ねるだけで実現でき、新しい設計判断を増やさない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象ケース | **キャッシュ済みのサンプル 1 つ**: 公式 `tests/<NN>.in/.out` と追加 `tests-extra/<NN>.in/.out`。前者は `01`、後者は `x01` の表示 ID (バッチ `test` と同じ規約) | 複数ケースの連続実行 / 範囲指定 |
| ケース指定 | bare 数字 (`1`→`01`)・`NN` (`01`)・`xNN` (`x01`)。`testexec` の `filterRefs`/`normalizeCaseName` と同じ正規化 | 名前付き追加ケース (任意名) の指定 |
| 引数省略 | 利用可能なケース ID の一覧を info 行で表示 (実行はしない) | 一覧から選択 UI |
| 実行方法 | 子を**リスタート**してクリーンな状態からケースの `.in` を順送 (`:replay` と同じ)。同時に `.out` でライブ検証 ([024]) | static な input/expected/actual の 3 ブロック表示 |
| ケース取得 | **キャッシュ済みのものだけ**読む。`:test` 自身は AtCoder へ fetch しない | `--refresh` 相当の取得トリガ |

### 境界

- 子プロセス・判定 (`testexec`/`runexec`)・exit code・`Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+E`・既存コマンド (`:case`/`:w`/`:set`/`:debug`/`:replay`/`:cheat`/`:q`/`:task`/`:contest`/`:e`) は不変。
- stdout には何も書かない (chat 内の info 行と、子への stdin 送信のみ)。バッチ `test`/`run` 経路には触れない。
- **fetch しない**: `:test` は既に `$XDG_CACHE_HOME` にキャッシュ済みのサンプル (公式は `atcoder test` 実行時に取得済み・追加は `:w` で保存済み) だけを読む。サンプル未取得なら一覧は空で、その旨を案内する (取得は従来どおり `atcoder test <contest>` が担う)。`internal/ui` は fetch/judge を知らない層境界 ([039] と同じ) を保つ。
- ライブ検証 ([024]) の許容誤差・トークン比較 (`tokensMatch`) はそのまま流用する (独自判定を増やさない)。

## ケースの場所と表示 ID

`:w` の保存先と同じ `TaskDir` (composition root が注入する `cachepath.Task(contest, task)`) を根に、2 系統を読む:

```
<TaskDir>/tests/<NN>.in        公式サンプル  → 表示 ID "NN"   (例 01, 02)
<TaskDir>/tests/<NN>.out
<TaskDir>/tests-extra/<NN>.in  追加ケース    → 表示 ID "xNN"  (例 x01, x02)
<TaskDir>/tests-extra/<NN>.out
```

- 追加ケースの場所解決・列挙は既存の `extracase.Dir(TaskDir)` / `extracase.List(TaskDir)` を使う ([024])。公式サンプルは `TaskDir/tests` を `os.ReadDir` して `*.in` を拾う (バッチの `listCases` と同じ要領だが、`internal/ui` から読むため UI 側に小さな純粋ヘルパを置く)。
- 表示 ID 規約は `testexec` (`collectCases`) と一致させる: 公式はファイル名のまま、追加は `x` プレフィックス。

## CLI / TUI 仕様

新フラグ無し。すべて command モード (insert で `Esc` → `:`) の内側。

### コマンド一覧 (追加分)

| コマンド | 動作 |
|---|---|
| `:test [case]` (`:t`) | `case` 指定: そのサンプルケースの `.in` を子のリスタート後に順送し、`.out` でライブ検証する。`case` 省略: 利用可能なケース ID の一覧を表示する |

- 別名: `:t` を受理する (`:case` の `:c` と同様の 1 文字短縮)。`parseCommand` で `test`/`t` を canonical `test` に正規化する。
- 補完 ([031](031-command-mode-completion.md)): canonical 名 `test` を常時候補に出す (`NavEnabled` に依らない)。`case` 引数を取るので一意確定時は末尾に空白を足す (`completeExpectsArg`)。第 2 トークン (ケース ID) は動的なので補完候補には載せない (`:e` のスペック引数と同じ扱い)。

### `:test <case>` の動作

1. command モードを抜けて元のモード (builder 中なら builder、ふだんは insert) に戻る ([039] の復帰と同じ)。
2. `TaskDir` が空 (識別不能) なら info 行 `(ケースの場所が不明なため :test は使えません)` を 1 本積んで終了。
3. 指定 `case` を正規化して該当ケースを解決する:
   - `xNN` / `xN` → `tests-extra/` の `NN` (`x` を剥がして数字を `%02d` 正規化)。
   - それ以外 (`NN` / `N`) → `tests/` の `NN` (`%02d` 正規化)。数字でない名前はそのまま (任意名の追加ケースに備える)。
   - 見つからなければ info 行 `(ケース <case> が見つかりません — :test で一覧)` を積んで終了 (子は起動しない)。
4. ケースの `.in` を行スライスへ、`.out` を expected 行スライスへ読む。読み込み失敗は info 行 (err) を積んで終了。
5. info 行 `(case <id> を実行 — input <N>行 / expected <M>行)` を 1 本積む。
6. expected が空でなければ `enableVerify(expected)` でライブ検証を (再) 開始し、`m.lastExpected` も更新する (以後 `:set verify` の対象になる)。expected が空なら検証は付けない (出力だけ見る)。
7. 子を **`restart()`** で作り直し (動作中の子も Kill して新規 spawn。`─── session #N ───` 区切りが出る)、リスタート後のクリーンな子へ `.in` 行を `submitLines(inLines, cmds, record=false)` で**順送**する。**`record=false`** なので再生行は `sessionInputs`/chatlog に積まない ([039] と同じ — 次の `:replay` を膨らませない)。spawn 失敗時は既存 `restart()` の失敗経路どおり。

### `:test` (引数省略) の動作

1. command モードを抜けて元のモードへ戻る。
2. `TaskDir` が空なら 2. と同じ info 行で終了。
3. 公式 (`tests/`) と追加 (`tests-extra/`) のケース ID を集めて一覧化する。
4. 1 件以上あれば info 行で `(利用可能なケース: 01 02 x01)` のように列挙する。0 件なら `(利用可能なサンプルがありません — atcoder test で取得、または :w で追加)` を積む。
5. 子は起動しない (一覧表示のみ)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:test 01` (公式 01 あり) | 子をリスタートして `tests/01.in` を順送、`tests/01.out` でライブ検証 |
| `:test 1` | `01` に正規化して同上 |
| `:test x01` / `:test x1` | `tests-extra/01` を実行 (`x` 系統) |
| `:t 02` | 別名。`:test 02` と同じ |
| `:test` (引数なし・ケースあり) | 利用可能なケース ID 一覧を表示 (実行しない) |
| `:test` (引数なし・ケース無し) | `(利用可能なサンプルがありません …)` の info 行のみ |
| `:test 99` (該当なし) | `(ケース 99 が見つかりません — :test で一覧)` の info 行のみ。子は起動しない |
| expected (`.out`) が空のケース | 入力を順送するがライブ検証は付けない (出力だけ見る) |
| `:test` (builder 中) | builder に戻ってから実行する (builder は破棄しない。`:set`/`:debug`/`:replay` と同じ復帰) |
| 子が動作中に `:test` | リスタート (現在の子を Kill して新規 spawn) してから順送 |
| 実行後に手入力 Enter | 通常どおり子へ送信。`:test` の順送行は `record=false` なので `:replay` の対象 (`sessionInputs`) には入らない |
| 同一問題で `:test` を連打 | 毎回クリーンな子で対象ケースを流し直せる (`record=false` で膨らまない) |
| `TaskDir` 空 | `(ケースの場所が不明なため :test は使えません)`。実行も一覧もしない |
| `--refresh` でサンプルが消えた直後 | 公式 `tests/` が無ければ一覧に出ない。`atcoder test` で再取得後に使える (追加 `tests-extra/` は `--refresh` 非対象なので残る) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `test`/`t`→`test` を追加。`execCommand` に `case "test"`。`execTest(arg)` ヘルパ (引数空→一覧 `listSampleCases`、指定→解決 `resolveSampleCase`・`enableVerify`・`restart()`+`submitLines(..., record=false)`) を追加。`newCommandInput` placeholder と `showCheat` に `:test` を追記 |
| `internal/ui/chat_sample.go` | **新規**。`TaskDir` から公式 (`tests/`) + 追加 (`tests-extra/`、`extracase`) のケースを読む小さな純粋ヘルパ: `listSampleCases(taskDir) []string` (表示 ID 一覧)、`resolveSampleCase(taskDir, ref) (in, out []string, id string, ok bool)`、`normalizeSampleRef(ref) (dir "tests"|"tests-extra", name string)`。`os.ReadFile`/`os.ReadDir` と `extracase.Dir/List` のみ依存 (testexec を import しない — 層境界を保つ) |
| `internal/ui/command_complete.go` | `completeNamesBase` に `test` を追加し、`completeExpectsArg["test"] = true` (ケース ID 引数を取るので一意確定時に末尾空白)。第 2 トークン候補 (`completeSubTokens`) は動的なので登録しない |
| `internal/ui/chat_sample_test.go` | **新規**。`normalizeSampleRef`/`resolveSampleCase`/`listSampleCases` を一時ディレクトリの `tests/`・`tests-extra/` で検証 (公式/追加の表示 ID、`1`→`01`・`x1`→`x01` 正規化、欠落時 `ok=false`、空 `.out` 許容) |
| `internal/ui/chattest_test.go` | **新規/回帰**。`execTest` の各分岐を fake spawner で検証: 指定実行が `restart` 後に `.in` を順送し `record=false` で `sessionInputs` を汚さないこと、ライブ検証が有効化されること、引数省略で一覧 info を積むこと、未知ケース/`TaskDir` 空で子を起動しないこと |
| `internal/ui/command_complete_test.go` | 候補一覧の期待値に `test` を反映。`:te`→`test ` (空白付き) 確定のケースを追加 |
| `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` | command モードのコマンド表に `:test [case]` を追記 |
| `docs/tools/atcoder-test-architecture.md` | chat の command モード節に `:test` (サンプル実行 + ライブ検証) を追記 |
| `docs/tools/todo.md` | ロードマップ項目 (AK) を追記し本要件へ相互リンク |

### 新規ヘルパの素描

```go
// internal/ui/chat_sample.go (package ui)

// listSampleCases は TaskDir 配下の公式 (tests/) + 追加 (tests-extra/) ケースの
// 表示 ID を昇順 (公式→追加) で返す。公式はファイル名のまま、追加は "x" プレフィックス。
func listSampleCases(taskDir string) []string

// resolveSampleCase は表示 ID 風の ref を解決し、入力行/期待行/正規化 ID を返す。
// 見つからなければ ok=false。
func resolveSampleCase(taskDir, ref string) (in, out []string, id string, ok bool)

// normalizeSampleRef は ref を (サブディレクトリ, ファイル名) に振り分ける純粋関数。
// "x" プレフィックスなら tests-extra、それ以外は tests。数字は %02d に正規化。
func normalizeSampleRef(ref string) (dir, name string)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `TaskDir` 空 | info 行で「場所不明」を案内。実行も一覧もしない (chat は継続) |
| ケース未解決 (該当 ID なし) | info 行で「見つからない — :test で一覧」。子は起動しない |
| `.in`/`.out` 読み込み失敗 (権限・I/O) | info 行 (err) を 1 本積んで終了 (chat は継続)。best-effort |
| サンプル未取得 (`tests/` 無し) | 一覧は追加ケースのみ (or 空)。空なら取得方法を案内 |
| `:test` 中の spawn 失敗 | 既存 `restart()` の spawn 失敗経路どおり (err 行 + `tea.Quit`)。引数誤りではないので exit code 規約には影響しない |
| exit code | 影響なし (表示と stdin 送信のみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変) |

## 非機能要件

- **既存非破壊**: 既存コマンド・キー・判定・chat の描画は不変。`:test` を打たない限り従来どおり。`TaskDir` 未注入なら `:test` は「場所不明」を返すだけ。
- **stdout 非汚染**: 表示は chat 内の info 行のみ。子への stdin 送信は `:replay` と同じ経路。
- **ネットワーク非依存**: ローカルのキャッシュ済みファイルのみ。AtCoder へは一切出さない (fetch しない)。
- **解答非破壊**: 解答ファイルには触れない。公式 `tests/`・追加 `tests-extra/` は読むだけで書き換えない。
- **`:replay` 非干渉**: 順送は `record=false`。`sessionInputs`/chatlog ([039]) を変えないので、`:test` 後の `:replay` は「自分が手で打った入力」だけを再生する。
- **決定的にテスト可能**: ケース読み込みヘルパは (taskDir, ref) → 行スライスの純粋な読込でテストできる。`parseCommand` は純粋関数のまま、`execTest` は fake spawner で送信行を検証できる ([039] の `chatreplay_test.go` と同型)。
- **スモーク**: 本機能は TUI/ローカル読込で `atcoder test` の判定 exit code 経路を増やさないため、fixture (`fixtures/run.sh`) は新規追加せず**既存スモークが緑のまま**を確認する。挙動は `internal/ui` の Go ユニットテストで固定する。

## 将来の拡張ポイント

- 複数ケースの連続実行 (`:test 01 02` / `:test all`) と各ケースの PASS/FAIL サマリ。
- static な input/expected/actual の 3 ブロック表示モード (順送ではなく一括判定)。
- 一覧からの選択 UI (`:test` でリストを出してカーソル選択)。
- 名前付き追加ケース (任意名で保存したもの) の指定。

## 用語

- **サンプルケース**: 公式サンプル (`tests/`、`atcoder test` が取得) と追加ケース (`tests-extra/`、`:w` で保存。[024])。
- **表示 ID**: ケースを指す ID。公式は `01`、追加は `x01` (バッチ `test` の `collectCases` と同じ規約)。
- **command モード**: chat の `:` ex-command line ([024](024-interactive-case-builder.md))。`Esc` で入る。
- **ライブ検証**: 子 stdout の各行を expected と順に突き合わせ `✓`/`✗` を添える機構 ([024])。

## 関連ドキュメント

- command モード基盤: [024](024-interactive-case-builder.md) (ケースビルダー・ライブ検証・`tests-extra`)
- 子リスタート + 入力順送の前例: [039](039-chat-replay-previous-session.md) (`:replay`・`submitLines(record=false)`)
- コマンド追加の前例: [030](030-chat-debug-cheat-commands.md) / 補完: [031](031-command-mode-completion.md)
- 利用手引: `docs/tools/atcoder-test-usage.md` / `docs/tools/atcoder-start-usage.md`
- アーキテクチャ: `docs/tools/atcoder-test-architecture.md`
- ロードマップ: `docs/tools/todo.md`
</content>
</invoke>
